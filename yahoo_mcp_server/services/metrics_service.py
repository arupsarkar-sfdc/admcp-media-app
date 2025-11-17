"""
Metrics Service
Performance data aggregation and reporting
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import MediaBuy, DeliveryMetric, Principal, MatchedAudience

logger = logging.getLogger(__name__)


class MetricsService:
    def __init__(self, session: Session):
        self.session = session
    
    async def get_media_buy_delivery(
        self,
        media_buy_id: str,
        principal: Principal
    ) -> Dict[str, Any]:
        """
        Get real-time performance metrics for a media buy
        
        Args:
            media_buy_id: Media buy ID
            principal: Authenticated principal
        
        Returns:
            Delivery metrics with CTR, pacing, etc.
        """
        # Get media buy
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
        
        # Aggregate metrics from delivery_metrics table
        metrics = self.session.query(
            func.sum(DeliveryMetric.impressions).label('impressions'),
            func.sum(DeliveryMetric.clicks).label('clicks'),
            func.sum(DeliveryMetric.conversions).label('conversions'),
            func.sum(DeliveryMetric.spend).label('spend')
        ).filter(
            DeliveryMetric.media_buy_id == media_buy.id
        ).first()
        
        impressions = metrics.impressions or 0
        clicks = metrics.clicks or 0
        conversions = metrics.conversions or 0
        spend = float(metrics.spend or 0.0)
        
        # Calculate derived metrics
        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        cvr = (conversions / clicks * 100) if clicks > 0 else 0.0
        cpm = (spend / impressions * 1000) if impressions > 0 else 0.0
        cpc = (spend / clicks) if clicks > 0 else 0.0
        cpa = (spend / conversions) if conversions > 0 else 0.0
        
        # Calculate pacing
        budget_pacing = (spend / media_buy.total_budget * 100) if media_buy.total_budget > 0 else 0.0
        
        # Calculate time pacing
        start_date = datetime.strptime(media_buy.flight_start_date, "%Y-%m-%d")
        end_date = datetime.strptime(media_buy.flight_end_date, "%Y-%m-%d")
        today = datetime.now()
        
        total_days = (end_date - start_date).days
        elapsed_days = (today - start_date).days
        time_pacing = (elapsed_days / total_days * 100) if total_days > 0 else 0.0
        
        # Pacing health
        pacing_health = "on_track"
        if budget_pacing > time_pacing + 10:
            pacing_health = "ahead"
        elif budget_pacing < time_pacing - 10:
            pacing_health = "behind"
        
        return {
            "media_buy_id": media_buy_id,
            "status": media_buy.status,
            "campaign": {
                "name": media_buy.media_buy_id,
                "budget": media_buy.total_budget,
                "spend": spend,
                "remaining_budget": media_buy.total_budget - spend,
                "flight_start_date": media_buy.flight_start_date,
                "flight_end_date": media_buy.flight_end_date
            },
            "matched_audience": {
                "segment_name": audience.segment_name,
                "overlap_count": audience.overlap_count,
                "engagement_score": audience.engagement_score
            } if audience else None,
            "delivery": {
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "spend": round(spend, 2)
            },
            "performance": {
                "ctr": round(ctr, 2),
                "cvr": round(cvr, 2),
                "cpm": round(cpm, 2),
                "cpc": round(cpc, 2),
                "cpa": round(cpa, 2)
            },
            "pacing": {
                "budget_pacing": round(budget_pacing, 1),
                "time_pacing": round(time_pacing, 1),
                "health": pacing_health,
                "days_elapsed": elapsed_days,
                "days_total": total_days
            }
        }
    
    async def get_media_buy_report(
        self,
        media_buy_id: str,
        principal: Principal,
        date_range: str = "last_7_days"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analytics report
        
        Args:
            media_buy_id: Media buy ID
            principal: Authenticated principal
            date_range: Report time range
        
        Returns:
            Detailed analytics report with breakdowns
        """
        # Get media buy
        media_buy = self.session.query(MediaBuy).filter(
            MediaBuy.media_buy_id == media_buy_id,
            MediaBuy.principal_id == principal.id
        ).first()
        
        if not media_buy:
            raise ValueError(f"Media buy '{media_buy_id}' not found")
        
        # Determine date range
        end_date = datetime.now()
        if date_range == "last_7_days":
            start_date = end_date - timedelta(days=7)
        elif date_range == "last_30_days":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(media_buy.flight_start_date, "%Y-%m-%d")
        
        # Daily breakdown
        daily_metrics = self.session.query(
            DeliveryMetric.date,
            func.sum(DeliveryMetric.impressions).label('impressions'),
            func.sum(DeliveryMetric.clicks).label('clicks'),
            func.sum(DeliveryMetric.conversions).label('conversions'),
            func.sum(DeliveryMetric.spend).label('spend')
        ).filter(
            DeliveryMetric.media_buy_id == media_buy.id,
            DeliveryMetric.date >= start_date.strftime("%Y-%m-%d")
        ).group_by(
            DeliveryMetric.date
        ).order_by(
            DeliveryMetric.date
        ).all()
        
        daily_data = []
        for row in daily_metrics:
            impressions = row.impressions or 0
            clicks = row.clicks or 0
            ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
            
            daily_data.append({
                "date": row.date,
                "impressions": impressions,
                "clicks": clicks,
                "conversions": row.conversions or 0,
                "spend": round(float(row.spend or 0.0), 2),
                "ctr": round(ctr, 2)
            })
        
        # Device breakdown
        device_metrics = self.session.query(
            DeliveryMetric.device_type,
            func.sum(DeliveryMetric.impressions).label('impressions'),
            func.sum(DeliveryMetric.clicks).label('clicks'),
            func.sum(DeliveryMetric.spend).label('spend')
        ).filter(
            DeliveryMetric.media_buy_id == media_buy.id
        ).group_by(
            DeliveryMetric.device_type
        ).all()
        
        device_data = []
        for row in device_metrics:
            impressions = row.impressions or 0
            clicks = row.clicks or 0
            ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
            
            device_data.append({
                "device_type": row.device_type,
                "impressions": impressions,
                "clicks": clicks,
                "spend": round(float(row.spend or 0.0), 2),
                "ctr": round(ctr, 2)
            })
        
        # Get overall delivery
        overall = await self.get_media_buy_delivery(media_buy_id, principal)
        
        return {
            "media_buy_id": media_buy_id,
            "report_date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "type": date_range
            },
            "overall": overall,
            "daily_breakdown": daily_data,
            "device_breakdown": device_data
        }

