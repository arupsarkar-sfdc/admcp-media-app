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
from models import MediaBuy, Product, Principal, MatchedAudience, Creative, Package, PackageFormat

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
    
    async def create_media_buy_v2(
        self,
        principal: Principal,
        campaign_name: str,
        packages: List[Dict[str, Any]],
        total_budget: float,
        flight_start_date: str,
        flight_end_date: str,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Create a new media buy using AdCP v2.3.0 package structure.
        
        Each package contains:
        - product_id: Yahoo product ID
        - budget: Per-package budget
        - format_ids: List of creative formats with {"agent_url": "...", "id": "..."}
        - targeting_overlay: Package-specific targeting (optional)
        - pacing: Pacing strategy (optional)
        - pricing_strategy: Pricing model (optional)
        
        Args:
            principal: Authenticated principal
            campaign_name: Human-readable campaign name
            packages: AdCP v2.3.0 package array
            total_budget: Total campaign budget (sum of all packages)
            flight_start_date: Start date (YYYY-MM-DD)
            flight_end_date: End date (YYYY-MM-DD)
            currency: Currency code
        
        Returns:
            Media buy response with ID, packages, and status
        """
        logger.info(f"Creating AdCP v2.3.0 media buy: {campaign_name} with {len(packages)} package(s)")
        
        # Extract all product IDs
        product_ids = [pkg["product_id"] for pkg in packages]
        
        # Validate products
        products = self.session.query(Product).filter(
            Product.product_id.in_(product_ids),
            Product.tenant_id == principal.tenant_id,
            Product.is_active == 1
        ).all()
        
        if len(products) != len(product_ids):
            found_ids = {p.product_id for p in products}
            missing_ids = set(product_ids) - found_ids
            raise ValueError(f"Invalid product IDs: {missing_ids}")
        
        # Create product lookup
        product_map = {p.product_id: p for p in products}
        
        # Validate budgets
        for pkg in packages:
            product = product_map[pkg["product_id"]]
            if pkg["budget"] < (product.minimum_budget or 0):
                raise ValueError(
                    f"Package budget ${pkg['budget']:,.2f} below minimum "
                    f"${product.minimum_budget:,.2f} for product {pkg['product_id']}"
                )
        
        # Determine matched audience (use first product's audience)
        matched_audience_id = None
        matched_audience = None
        if products[0].matched_audience_ids_list():
            audience_segment_id = products[0].matched_audience_ids_list()[0]
            matched_audience = self.session.query(MatchedAudience).filter(
                MatchedAudience.segment_id == audience_segment_id
            ).first()
            if matched_audience:
                matched_audience_id = matched_audience.id
        
        # Generate media buy ID from campaign name
        safe_name = campaign_name.lower().replace(" ", "_")[:30]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        media_buy_id = f"{safe_name}_{timestamp}"
        media_buy_uuid = str(uuid.uuid4())
        
        # Create media buy (AdCP v2.3.0 with normalized packages)
        media_buy = MediaBuy(
            id=media_buy_uuid,
            tenant_id=principal.tenant_id,
            media_buy_id=media_buy_id,
            principal_id=principal.id,
            campaign_name=campaign_name,
            adcp_version="2.3.0",
            product_ids=json.dumps([p.id for p in products]),
            total_budget=total_budget,
            currency=currency,
            flight_start_date=flight_start_date,
            flight_end_date=flight_end_date,
            targeting=None,  # AdCP v2.3.0: Use packages table instead of JSON
            matched_audience_id=matched_audience_id,
            assigned_creatives=None,  # AdCP v2.3.0: Use package_formats table
            status="pending",
            workflow_state=json.dumps({
                "created_by": principal.principal_id,
                "requires_approval": total_budget > 10000,
                "campaign_name": campaign_name
            }),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.session.add(media_buy)
        self.session.flush()  # Flush to get media_buy.id before creating packages
        
        logger.info(f"Created AdCP v2.3.0 media buy: {media_buy_id}")
        
        # Create normalized Package records
        created_packages = []
        for idx, pkg_data in enumerate(packages, 1):
            package = self._create_package(
                media_buy=media_buy,
                package_idx=idx,
                package_data=pkg_data,
                product_map=product_map
            )
            created_packages.append(package)
        
        self.session.commit()
        logger.info(f"Created {len(created_packages)} package(s) with formats")
        
        # Build response with package details from database
        package_details = []
        for package in created_packages:
            # Get product info
            product = self.session.query(Product).filter(Product.id == package.product_id).first()
            
            # Get package formats
            package_formats = self.session.query(PackageFormat).filter(
                PackageFormat.package_id == package.id
            ).all()
            
            package_details.append({
                "product_id": product.product_id if product else "unknown",
                "product_name": product.name if product else "Unknown Product",
                "budget": package.budget,
                "format_count": len(package_formats),
                "formats": [pf.format_id for pf in package_formats],
                "pacing": package.pacing,
                "pricing_strategy": package.pricing_strategy
            })
        
        return {
            "media_buy_id": media_buy_id,
            "campaign_name": campaign_name,
            "status": "pending",
            "adcp_version": "2.3.0",
            "total_budget": total_budget,
            "currency": currency,
            "flight_start_date": flight_start_date,
            "flight_end_date": flight_end_date,
            "packages": package_details,
            "matched_audience": {
                "segment_id": matched_audience.segment_id,
                "segment_name": matched_audience.segment_name,
                "overlap_count": matched_audience.overlap_count
            } if matched_audience else None,
            "workflow": {
                "requires_approval": total_budget > 10000,
                "next_steps": "Campaign pending approval" if total_budget > 10000 else "Campaign ready to activate"
            },
            "created_at": media_buy.created_at
        }
    
    def _create_package(
        self,
        media_buy: MediaBuy,
        package_idx: int,
        package_data: Dict[str, Any],
        product_map: Dict[str, Product]
    ) -> Package:
        """
        Create a normalized Package record with associated PackageFormat records.
        
        Args:
            media_buy: Parent media buy record
            package_idx: Package index (1-based)
            package_data: Package data from AdCP v2.3.0 request
            product_map: Map of product_id → Product
        
        Returns:
            Created Package record
        """
        product = product_map[package_data["product_id"]]
        package_id = f"pkg_{package_idx}"
        package_uuid = str(uuid.uuid4())
        
        # Create Package record
        package = Package(
            id=package_uuid,
            media_buy_id=media_buy.id,
            package_id=package_id,
            product_id=product.id,
            budget=package_data["budget"],
            currency=package_data.get("currency", "USD"),
            pacing=package_data.get("pacing", "even"),
            pricing_strategy=package_data.get("pricing_strategy", "cpm"),
            targeting_overlay=json.dumps(package_data.get("targeting_overlay", {})),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.session.add(package)
        self.session.flush()  # Flush to get package.id
        
        # Create PackageFormat records
        format_ids = package_data.get("format_ids", [])
        for fmt in format_ids:
            package_format = PackageFormat(
                id=str(uuid.uuid4()),
                package_id=package.id,
                agent_url=fmt["agent_url"],
                format_id=fmt["id"],
                format_name=self._get_format_name(fmt["id"]),  # Denormalized for performance
                format_type=self._get_format_type(fmt["id"]),
                created_at=datetime.now().isoformat()
            )
            self.session.add(package_format)
        
        logger.info(f"Created package {package_id} with {len(format_ids)} format(s)")
        return package
    
    def _get_format_name(self, format_id: str) -> str:
        """Get human-readable format name from format_id"""
        format_names = {
            "display_300x250": "Display - Medium Rectangle (300x250)",
            "display_728x90": "Display - Leaderboard (728x90)",
            "display_160x600": "Display - Wide Skyscraper (160x600)",
            "video_preroll_640x480": "Video - Preroll (640x480)",
            "video_midroll_1280x720": "Video - Midroll (1280x720)",
            "video_outstream_1920x1080": "Video - Outstream (1920x1080)",
            "native_feed": "Native - Feed",
            "native_content": "Native - Content",
            "native_app_install": "Native - App Install"
        }
        return format_names.get(format_id, format_id)
    
    def _get_format_type(self, format_id: str) -> str:
        """Get format type from format_id"""
        if format_id.startswith("display_"):
            return "display"
        elif format_id.startswith("video_"):
            return "video"
        elif format_id.startswith("native_"):
            return "native"
        return "unknown"
    
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

