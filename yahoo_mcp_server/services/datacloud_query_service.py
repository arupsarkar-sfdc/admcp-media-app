"""
Salesforce Data Cloud Query Service
Execute SQL queries against Data Cloud
"""
import httpx
from typing import List, Dict, Any, Optional
from .datacloud_auth_service import get_datacloud_auth_service


class DataCloudQueryService:
    """
    Execute SQL queries against Salesforce Data Cloud
    """
    
    def __init__(self):
        """
        Initialize the query service
        """
        self.auth_service = get_datacloud_auth_service()
    
    async def _get_base_url(self) -> str:
        """Get Data Cloud instance base URL"""
        # Ensure token is fetched (which populates instance URL)
        await self.auth_service.get_access_token()
        
        instance_url = self.auth_service.get_instance_url()
        if not instance_url:
            raise RuntimeError("Instance URL not available. Fetch token first.")
        return f"https://{instance_url}/api/v1"
    
    async def execute_query_sync(self, sql: str, limit: int = 2000) -> Dict[str, Any]:
        """
        Execute SQL query synchronously and return results
        
        Args:
            sql: ANSI SQL query string
            limit: Maximum rows to return (default: 2000)
            
        Returns:
            Query results with rows and metadata
            
        Raises:
            httpx.HTTPError: If query fails
        """
        base_url = await self._get_base_url()
        url = f"{base_url}/query"
        headers = await self.auth_service.get_auth_headers()
        
        payload = {
            "sql": sql,
            "limit": limit
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            # Better error handling for 400 errors
            if response.status_code != 200:
                error_body = response.text
                print(f"\n❌ Query failed with {response.status_code}")
                print(f"   SQL: {sql[:200]}...")
                print(f"   Error Response: {error_body}\n")
                response.raise_for_status()
            
            data = response.json()
            row_count = data.get('rowCount', 0)
            print(f"✅ Query completed: {row_count} rows")
            return data
    
    
    async def execute_query(
        self,
        sql: str,
        max_rows: int = 2000
    ) -> Dict[str, Any]:
        """
        Execute SQL query and return results
        
        Args:
            sql: ANSI SQL query string
            max_rows: Maximum rows to return (default: 2000)
            
        Returns:
            Dictionary with:
                - rows: List of row dictionaries
                - row_count: Number of rows returned
                
        Raises:
            Exception: If query fails
        """
        result = await self.execute_query_sync(sql, limit=max_rows)
        
        rows = result.get("data", [])
        
        return {
            "rows": rows,
            "row_count": len(rows),
            "metadata": result
        }
    
    async def query_products(self, tenant_id: Optional[str] = None, is_active: bool = True) -> List[Dict[str, Any]]:
        """
        Query products from Snowflake via Data Cloud
        
        Args:
            tenant_id: Filter by tenant ID (optional)
            is_active: Filter by active status (default: True)
            
        Returns:
            List of product records
        """
        where_clauses = []
        if is_active:
            where_clauses.append("is_active__c = true")
        if tenant_id:
            where_clauses.append(f"tenant_id__c = '{tenant_id}'")
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        sql = f"""
        SELECT 
            id__c as id,
            tenant_id__c as tenant_id,
            product_id__c as product_id,
            name__c as name,
            description__c as description,
            product_type__c as product_type,
            pricing__c as pricing,
            minimum_budget__c as minimum_budget,
            estimated_reach__c as estimated_reach,
            estimated_impressions__c as estimated_impressions,
            matched_reach__c as matched_reach,
            is_active__c as is_active,
            available_from__c as available_from,
            available_to__c as available_to,
            formats__c as formats,
            targeting__c as targeting,
            properties__c as properties,
            principal_access__c as principal_access,
            created_at__c as created_at,
            updated_at__c as updated_at
        FROM products__dlm
        {where_sql}
        ORDER BY created_at__c DESC
        """
        
        result = await self.execute_query(sql, max_rows=10000)
        return result["rows"]
    
    async def query_media_buys(
        self,
        tenant_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query media buys with packages from Snowflake via Data Cloud
        
        Args:
            tenant_id: Filter by tenant ID (optional)
            status: Filter by status (optional)
            
        Returns:
            List of media buy records
        """
        where_clauses = []
        if tenant_id:
            where_clauses.append(f"tenant_id__c = '{tenant_id}'")
        if status:
            where_clauses.append(f"status__c = '{status}'")
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        sql = f"""
        SELECT 
            id__c as id,
            tenant_id__c as tenant_id,
            media_buy_id__c as media_buy_id,
            principal_id__c as principal_id,
            campaign_name__c as campaign_name,
            adcp_version__c as adcp_version,
            total_budget__c as total_budget,
            currency__c as currency,
            flight_start_date__c as flight_start_date,
            flight_end_date__c as flight_end_date,
            status__c as status,
            workflow_state__c as workflow_state,
            impressions_delivered__c as impressions_delivered,
            spend__c as spend,
            clicks__c as clicks,
            conversions__c as conversions,
            product_ids__c as product_ids,
            matched_audience_id__c as matched_audience_id,
            assigned_creatives__c as assigned_creatives,
            targeting__c as targeting,
            external_campaign_id__c as external_campaign_id,
            salesforce_campaign_id__c as salesforce_campaign_id,
            salesforce_opportunity_id__c as salesforce_opportunity_id,
            created_at__c as created_at,
            updated_at__c as updated_at
        FROM media_buys__dlm
        {where_sql}
        ORDER BY created_at__c DESC
        """
        
        result = await self.execute_query(sql, max_rows=10000)
        return result["rows"]
    
    async def query_packages_by_media_buy(self, media_buy_id: str) -> List[Dict[str, Any]]:
        """
        Query packages for a specific media buy
        
        Args:
            media_buy_id: Media buy ID
            
        Returns:
            List of package records
        """
        sql = f"""
        SELECT 
            id__c as id,
            media_buy_id__c as media_buy_id,
            package_id__c as package_id,
            product_id__c as product_id,
            budget__c as budget,
            currency__c as currency,
            pacing__c as pacing,
            pricing_strategy__c as pricing_strategy,
            impressions_delivered__c as impressions_delivered,
            spend__c as spend,
            clicks__c as clicks,
            conversions__c as conversions,
            targeting_overlay__c as targeting_overlay,
            created_at__c as created_at,
            updated_at__c as updated_at
        FROM packages__dlm
        WHERE media_buy_id__c = '{media_buy_id}'
        ORDER BY created_at__c
        """
        
        result = await self.execute_query(sql, max_rows=10000)
        return result["rows"]
    
    async def query_package_formats_by_package(self, package_id: str) -> List[Dict[str, Any]]:
        """
        Query formats for a specific package
        
        Args:
            package_id: Package ID
            
        Returns:
            List of package format records
        """
        sql = f"""
        SELECT 
            id__c as id,
            package_id__c as package_id,
            agent_url__c as agent_url,
            format_id__c as format_id,
            format_name__c as format_name,
            format_type__c as format_type,
            assigned_creative_id__c as assigned_creative_id,
            created_at__c as created_at
        FROM package_formats__dlm
        WHERE package_id__c = '{package_id}'
        ORDER BY created_at__c
        """
        
        result = await self.execute_query(sql, max_rows=10000)
        return result["rows"]
    
    async def query_matched_audiences(
        self,
        tenant_id: Optional[str] = None,
        min_overlap: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query matched audiences (Profile category)
        
        Args:
            tenant_id: Filter by tenant ID (optional)
            min_overlap: Minimum overlap count (optional)
            
        Returns:
            List of matched audience records
        """
        where_clauses = []
        if tenant_id:
            where_clauses.append(f"tenant_id__c = '{tenant_id}'")
        if min_overlap:
            where_clauses.append(f"overlap_count__c >= {min_overlap}")
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        sql = f"""
        SELECT 
            id__c as id,
            segment_id__c as segment_id,
            segment_name__c as segment_name,
            tenant_id__c as tenant_id,
            principal_id__c as principal_id,
            contact_id__c as contact_id,
            overlap_count__c as overlap_count,
            total_nike_segment__c as total_nike_segment,
            total_yahoo_segment__c as total_yahoo_segment,
            match_rate__c as match_rate,
            demographics__c as demographics,
            engagement_score__c as engagement_score,
            quality_score__c as quality_score,
            privacy_params__c as privacy_params,
            salesforce_account_id__c as salesforce_account_id,
            salesforce_contact_id__c as salesforce_contact_id,
            created_at__c as created_at,
            expires_at__c as expires_at
        FROM matched_audiences__dlm
        {where_sql}
        ORDER BY overlap_count__c DESC
        """
        
        result = await self.execute_query(sql, max_rows=10000)
        return result["rows"]
    
    async def query_delivery_metrics(
        self,
        media_buy_id: Optional[str] = None,
        package_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query delivery metrics (Engagement category)
        
        Args:
            media_buy_id: Filter by media buy ID (optional)
            package_id: Filter by package ID (optional)
            start_date: Start date filter YYYY-MM-DD (optional)
            end_date: End date filter YYYY-MM-DD (optional)
            
        Returns:
            List of delivery metric records
        """
        where_clauses = []
        if media_buy_id:
            where_clauses.append(f"media_buy_id__c = '{media_buy_id}'")
        if package_id:
            where_clauses.append(f"package_id__c = '{package_id}'")
        if start_date:
            where_clauses.append(f"date__c >= '{start_date}'")
        if end_date:
            where_clauses.append(f"date__c <= '{end_date}'")
        
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        sql = f"""
        SELECT 
            id__c as id,
            media_buy_id__c as media_buy_id,
            package_id__c as package_id,
            date__c as date,
            hour__c as hour,
            impressions__c as impressions,
            clicks__c as clicks,
            conversions__c as conversions,
            spend__c as spend,
            product_id__c as product_id,
            creative_id__c as creative_id,
            format_id__c as format_id,
            geo__c as geo,
            device_type__c as device_type,
            created_at__c as created_at
        FROM delivery_metrics__dlm
        {where_sql}
        ORDER BY date__c DESC, hour__c DESC
        """
        
        result = await self.execute_query(sql, max_rows=10000)
        return result["rows"]


# Global singleton instance
_query_service: Optional[DataCloudQueryService] = None


def get_datacloud_query_service() -> DataCloudQueryService:
    """
    Get the global Data Cloud query service instance
    
    Returns:
        Singleton DataCloudQueryService instance
    """
    global _query_service
    if _query_service is None:
        _query_service = DataCloudQueryService()
    return _query_service

