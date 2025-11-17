"""
Product Discovery Service
LLM-powered product matching with matched audience data
"""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models import Product, Principal, MatchedAudience
from utils.llm_client import extract_campaign_criteria, rank_products

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, session: Session):
        self.session = session
    
    async def discover_products(
        self,
        brief: str,
        budget_range: Optional[List[int]],
        principal: Principal,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        Discover products matching natural language brief
        
        Uses LLM to:
        1. Extract intent from brief (product type, targeting, budget)
        2. Match against inventory database
        3. Apply principal-specific pricing and access control
        4. Rank results by relevance
        
        Args:
            brief: Natural language campaign description
            budget_range: [min, max] budget in USD
            principal: Authenticated principal
            tenant_id: Tenant ID
        
        Returns:
            List of product dicts with pricing and matched audience data
        """
        logger.info(f"Product discovery for principal {principal.principal_id}")
        logger.info(f"Brief: {brief}")
        
        # Step 1: Extract criteria from brief using LLM
        criteria = await extract_campaign_criteria(brief, budget_range)
        logger.info(f"Extracted criteria: {criteria}")
        
        # Step 2: Query products from database
        query = self.session.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.is_active == 1
        )
        
        # Apply filters based on extracted criteria
        if criteria.get("product_types"):
            query = query.filter(Product.product_type.in_(criteria["product_types"]))
        
        if budget_range:
            min_budget, max_budget = budget_range
            query = query.filter(
                Product.minimum_budget >= min_budget * 0.5,  # Allow some flexibility
                Product.minimum_budget <= max_budget * 1.5
            )
        
        products = query.all()
        logger.info(f"Found {len(products)} matching products")
        
        if not products:
            return []
        
        # Step 3: Convert to dicts for ranking
        product_dicts = []
        for p in products:
            product_dicts.append({
                'product_id': p.product_id,
                'name': p.name,
                'description': p.description,
                'product_type': p.product_type,
                'matched_reach': p.matched_reach,
                'obj': p  # Keep reference
            })
        
        # Step 4: Rank products using LLM
        ranked_ids = await rank_products(brief, product_dicts)
        
        # Re-order products by ranking
        product_map = {p['product_id']: p['obj'] for p in product_dicts}
        ordered_products = []
        for pid in ranked_ids:
            if pid in product_map:
                ordered_products.append(product_map[pid])
        
        # Add any products not ranked (shouldn't happen, but safety)
        for p in products:
            if p not in ordered_products:
                ordered_products.append(p)
        
        # Step 5: Format products with pricing and matched audience data
        results = []
        for product in ordered_products[:10]:  # Top 10 results
            product_response = await self._format_product(product, principal)
            results.append(product_response)
        
        logger.info(f"Returning {len(results)} ranked products")
        return results
    
    async def _format_product(
        self,
        product: Product,
        principal: Principal
    ) -> Dict[str, Any]:
        """
        Format product for API response with principal-specific pricing
        and matched audience data
        """
        # Apply principal-specific pricing discount
        pricing = product.pricing_dict()
        base_price = pricing["value"]
        discount = 0.0
        
        if principal.access_level == "enterprise":
            discount = pricing.get("enterprise_discount", 0.15)
        elif principal.access_level == "premium":
            discount = pricing.get("premium_discount", 0.10)
        
        final_price = base_price * (1 - discount)
        
        # Get matched audience data
        matched_audiences = []
        for audience_segment_id in product.matched_audience_ids_list():
            audience = self.session.query(MatchedAudience).filter(
                MatchedAudience.segment_id == audience_segment_id
            ).first()
            
            if audience:
                matched_audiences.append({
                    "segment_id": audience.segment_id,
                    "segment_name": audience.segment_name,
                    "overlap_count": audience.overlap_count,
                    "match_rate": audience.match_rate,
                    "engagement_score": audience.engagement_score,
                    "demographics": audience.demographics_dict(),
                    "privacy_params": audience.privacy_params_dict()
                })
        
        return {
            "product_id": product.product_id,
            "name": product.name,
            "description": product.description,
            "product_type": product.product_type,
            "properties": product.properties_list(),
            "formats": product.formats_list(),
            "targeting": product.targeting_dict(),
            "pricing": {
                "type": pricing["type"],
                "value": round(final_price, 2),
                "currency": pricing["currency"],
                "original_value": base_price,
                "discount_applied": discount,
                "discount_percentage": f"{discount * 100:.0f}%"
            },
            "minimum_budget": product.minimum_budget,
            "estimated_reach": product.estimated_reach,
            "matched_reach": product.matched_reach,
            "estimated_impressions": product.estimated_impressions,
            "matched_audiences": matched_audiences,
            "is_active": bool(product.is_active)
        }

