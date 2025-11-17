"""
Media Buy Service
Campaign lifecycle management
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from models import MediaBuy, Product, Principal, MatchedAudience, Creative

logger = logging.getLogger(__name__)


class MediaBuyService:
    def __init__(self, session: Session):
        self.session = session
    
    async def create_media_buy(
        self,
        principal: Principal,
        product_ids: List[str],
        total_budget: float,
        flight_start_date: str,
        flight_end_date: str,
        targeting: Optional[Dict] = None,
        creative_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new media buy (campaign)
        
        Args:
            principal: Authenticated principal
            product_ids: List of product IDs to activate
            total_budget: Total campaign budget
            flight_start_date: Start date (YYYY-MM-DD)
            flight_end_date: End date (YYYY-MM-DD)
            targeting: Additional targeting parameters
            creative_ids: List of creative IDs to assign
        
        Returns:
            Media buy response with ID and status
        """
        logger.info(f"Creating media buy for principal {principal.principal_id}")
        
        # Validate products
        products = self.session.query(Product).filter(
            Product.product_id.in_(product_ids),
            Product.tenant_id == principal.tenant_id,
            Product.is_active == 1
        ).all()
        
        if len(products) != len(product_ids):
            raise ValueError(f"Invalid product IDs provided")
        
        # Check minimum budget
        total_minimum = sum(p.minimum_budget or 0 for p in products)
        if total_budget < total_minimum:
            raise ValueError(f"Budget ${total_budget:,.2f} below minimum ${total_minimum:,.2f}")
        
        # Determine matched audience (use first product's audience for simplicity)
        matched_audience_id = None
        if products[0].matched_audience_ids_list():
            audience_segment_id = products[0].matched_audience_ids_list()[0]
            audience = self.session.query(MatchedAudience).filter(
                MatchedAudience.segment_id == audience_segment_id
            ).first()
            if audience:
                matched_audience_id = audience.id
        
        # Generate media buy ID
        media_buy_id = f"nike_{products[0].product_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Assign creatives
        assigned_creatives = []
        if creative_ids:
            for creative_id in creative_ids:
                creative = self.session.query(Creative).filter(
                    Creative.creative_id == creative_id,
                    Creative.principal_id == principal.id
                ).first()
                
                if creative:
                    assigned_creatives.append({
                        "creative_id": creative.id,
                        "product_id": products[0].id  # Assign to first product
                    })
        
        # Create media buy
        media_buy = MediaBuy(
            id=str(uuid.uuid4()),
            tenant_id=principal.tenant_id,
            media_buy_id=media_buy_id,
            principal_id=principal.id,
            product_ids=json.dumps([p.id for p in products]),
            total_budget=total_budget,
            currency="USD",
            flight_start_date=flight_start_date,
            flight_end_date=flight_end_date,
            targeting=json.dumps(targeting) if targeting else None,
            matched_audience_id=matched_audience_id,
            assigned_creatives=json.dumps(assigned_creatives) if assigned_creatives else None,
            status="pending",
            workflow_state=json.dumps({
                "created_by": principal.principal_id,
                "requires_approval": total_budget > 10000
            }),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.session.add(media_buy)
        self.session.commit()
        
        logger.info(f"Created media buy: {media_buy_id}")
        
        return {
            "media_buy_id": media_buy_id,
            "status": "pending",
            "total_budget": total_budget,
            "flight_start_date": flight_start_date,
            "flight_end_date": flight_end_date,
            "products": [{"product_id": p.product_id, "name": p.name} for p in products],
            "matched_audience": {
                "segment_id": audience.segment_id,
                "overlap_count": audience.overlap_count
            } if matched_audience_id and audience else None,
            "workflow": {
                "requires_approval": total_budget > 10000,
                "next_steps": "Campaign pending approval" if total_budget > 10000 else "Campaign ready to activate"
            },
            "created_at": media_buy.created_at
        }
    
    async def get_media_buy(
        self,
        media_buy_id: str,
        principal: Principal
    ) -> Dict[str, Any]:
        """
        Get media buy configuration
        
        Args:
            media_buy_id: Media buy ID
            principal: Authenticated principal
        
        Returns:
            Media buy details
        """
        media_buy = self.session.query(MediaBuy).filter(
            MediaBuy.media_buy_id == media_buy_id,
            MediaBuy.principal_id == principal.id
        ).first()
        
        if not media_buy:
            raise ValueError(f"Media buy '{media_buy_id}' not found")
        
        # Get matched audience
        audience = None
        if media_buy.matched_audience_id:
            audience = self.session.query(MatchedAudience).filter(
                MatchedAudience.id == media_buy.matched_audience_id
            ).first()
        
        return {
            "media_buy_id": media_buy.media_buy_id,
            "status": media_buy.status,
            "total_budget": media_buy.total_budget,
            "spend": media_buy.spend,
            "flight_start_date": media_buy.flight_start_date,
            "flight_end_date": media_buy.flight_end_date,
            "targeting": media_buy.targeting_dict(),
            "matched_audience": {
                "segment_id": audience.segment_id,
                "segment_name": audience.segment_name,
                "overlap_count": audience.overlap_count
            } if audience else None,
            "impressions_delivered": media_buy.impressions_delivered,
            "clicks": media_buy.clicks,
            "conversions": media_buy.conversions,
            "created_at": media_buy.created_at,
            "updated_at": media_buy.updated_at
        }
    
    async def update_media_buy(
        self,
        media_buy_id: str,
        updates: Dict[str, Any],
        principal: Principal
    ) -> Dict[str, Any]:
        """
        Update an active media buy
        
        Args:
            media_buy_id: Media buy ID
            updates: Fields to update (budget, targeting, status)
            principal: Authenticated principal
        
        Returns:
            Updated media buy details
        """
        media_buy = self.session.query(MediaBuy).filter(
            MediaBuy.media_buy_id == media_buy_id,
            MediaBuy.principal_id == principal.id
        ).first()
        
        if not media_buy:
            raise ValueError(f"Media buy '{media_buy_id}' not found")
        
        # Apply updates
        if "total_budget" in updates:
            new_budget = updates["total_budget"]
            if new_budget < media_buy.spend:
                raise ValueError(f"Cannot reduce budget below current spend ${media_buy.spend:,.2f}")
            media_buy.total_budget = new_budget
        
        if "targeting" in updates:
            media_buy.targeting = json.dumps(updates["targeting"])
        
        if "status" in updates:
            valid_statuses = ["pending", "approved", "active", "paused", "completed"]
            if updates["status"] in valid_statuses:
                media_buy.status = updates["status"]
        
        media_buy.updated_at = datetime.now().isoformat()
        
        self.session.commit()
        
        logger.info(f"Updated media buy: {media_buy_id}")
        
        return await self.get_media_buy(media_buy_id, principal)

