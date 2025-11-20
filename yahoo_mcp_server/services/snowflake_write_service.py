"""
Snowflake Write Service
Direct writes to Snowflake for all AdCP entities
Data Cloud reflects changes instantly via Zero Copy
"""
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables (works in local dev and cloud deployment)
load_dotenv()


class SnowflakeWriteService:
    """
    Write operations to Snowflake
    Data Cloud virtualizes this data via Zero Copy (instant visibility)
    """
    
    def __init__(self):
        """Initialize Snowflake connection"""
        self.account = os.getenv('SNOWFLAKE_ACCOUNT')
        self.user = os.getenv('SNOWFLAKE_USER')
        self.password = os.getenv('SNOWFLAKE_PASSWORD')
        self.database = os.getenv('SNOWFLAKE_DATABASE')
        self.schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
        self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
        self.role = os.getenv('SNOWFLAKE_ROLE')
        
    def _get_connection(self):
        """Get Snowflake connection"""
        return snowflake.connector.connect(
            user=self.user,
            password=self.password,
            account=self.account,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema,
            role=self.role
        )
    
    def insert_media_buy(
        self,
        tenant_id: str,
        principal_id: str,
        campaign_name: str,
        total_budget: float,
        currency: str,
        flight_start_date: str,
        flight_end_date: str,
        adcp_version: str = "2.3.0"
    ) -> str:
        """
        Insert a new media buy into Snowflake
        
        Returns:
            media_buy_id (str)
        """
        media_buy_id = f"{campaign_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            sql = """
            INSERT INTO media_buys (
                id, tenant_id, media_buy_id, principal_id,
                product_ids, campaign_name, adcp_version,
                salesforce_opportunity_id, salesforce_campaign_id,
                total_budget, currency,
                flight_start_date, flight_end_date,
                targeting, matched_audience_id, assigned_creatives,
                status, workflow_state,
                impressions_delivered, spend, clicks, conversions,
                external_campaign_id,
                created_at, updated_at
            ) SELECT 
                %s, %s, %s, %s,
                PARSE_JSON(%s), %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                PARSE_JSON(%s), %s, PARSE_JSON(%s),
                %s, PARSE_JSON(%s),
                %s, %s, %s, %s,
                %s,
                %s, %s
            """
            
            now = datetime.utcnow()
            
            values = (
                str(uuid.uuid4()),          # id
                tenant_id,                  # tenant_id
                media_buy_id,               # media_buy_id
                principal_id,               # principal_id
                json.dumps([]),             # product_ids (VARIANT) -> JSON string
                campaign_name,              # campaign_name
                adcp_version,               # adcp_version
                None,                       # salesforce_opportunity_id
                None,                       # salesforce_campaign_id
                total_budget,               # total_budget
                currency,                   # currency
                flight_start_date,          # flight_start_date (DATE)
                flight_end_date,            # flight_end_date (DATE)
                json.dumps({}),             # targeting (VARIANT) -> JSON string
                None,                       # matched_audience_id
                json.dumps([]),             # assigned_creatives (VARIANT) -> JSON string
                'PENDING',                  # status
                json.dumps({"state": "DRAFT"}),  # workflow_state (VARIANT) -> JSON string
                0,                          # impressions_delivered
                0.0,                        # spend
                0,                          # clicks
                0,                          # conversions
                None,                       # external_campaign_id
                now,                        # created_at (TIMESTAMP_NTZ)
                now                         # updated_at (TIMESTAMP_NTZ)
            )
            
            cur.execute(sql, values)
            conn.commit()
            
            print(f"✅ Inserted media buy into Snowflake: {media_buy_id}")
            return media_buy_id
            
        finally:
            cur.close()
            conn.close()
    
    def insert_package(
        self,
        media_buy_id: str,
        package: Dict[str, Any]
    ) -> str:
        """
        Insert a package into Snowflake
        
        Args:
            media_buy_id: Parent media buy ID
            package: Package data from AdCP structure
            
        Returns:
            package_id (str)
        """
        # Generate package_id if not provided
        package_id = package.get('package_id') or f"pkg_{media_buy_id}_{uuid.uuid4().hex[:8]}"
        
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Insert package
            sql = """
            INSERT INTO packages (
                id, media_buy_id, package_id, product_id,
                budget, currency, pacing, pricing_strategy,
                impressions_delivered, spend, clicks, conversions,
                targeting_overlay, created_at, updated_at
            ) SELECT 
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                PARSE_JSON(%s), %s, %s
            """
            
            # Convert dict to JSON string for PARSE_JSON
            targeting_overlay = json.dumps(package.get('targeting_overlay', {}))
            now = datetime.utcnow()
            
            values = (
                str(uuid.uuid4()),  # id
                media_buy_id,
                package_id,
                package['product_id'],
                package['budget'],
                package.get('currency', 'USD'),
                package.get('pacing', 'even'),
                package.get('pricing_strategy', 'cpm'),
                0,  # impressions_delivered
                0.0,  # spend
                0,  # clicks
                0,  # conversions
                targeting_overlay,  # JSON string for PARSE_JSON
                now,  # created_at (TIMESTAMP_NTZ)
                now   # updated_at (TIMESTAMP_NTZ)
            )
            
            cur.execute(sql, values)
            
            # Insert package formats
            format_ids = package.get('format_ids', [])
            for fmt in format_ids:
                self._insert_package_format(cur, package_id, fmt)
            
            conn.commit()
            
            print(f"✅ Inserted package into Snowflake: {package_id} with {len(format_ids)} formats")
            return package_id
            
        finally:
            cur.close()
            conn.close()
    
    def _insert_package_format(
        self,
        cursor,
        package_id: str,
        format_spec: Dict[str, Any]
    ):
        """Insert a package format"""
        sql = """
        INSERT INTO package_formats (
            id, package_id, agent_url, format_id,
            format_name, format_type, assigned_creative_id, created_at
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        """
        
        values = (
            str(uuid.uuid4()),  # id
            package_id,
            format_spec.get('agent_url'),
            format_spec.get('id'),
            format_spec.get('id', 'unknown'),  # format_name (use id as fallback)
            format_spec.get('id', '').split('_')[0] if '_' in format_spec.get('id', '') else 'display',  # format_type
            None,  # assigned_creative_id
            datetime.utcnow()  # created_at (TIMESTAMP_NTZ)
        )
        
        cursor.execute(sql, values)
    
    def update_media_buy(
        self,
        media_buy_id: str,
        updates: Dict[str, Any]
    ):
        """
        Update an existing media buy in Snowflake
        
        Args:
            media_buy_id: Media buy to update
            updates: Fields to update
        """
        if not updates:
            return
        
        # VARIANT columns that need PARSE_JSON
        variant_columns = {
            'product_ids', 'targeting', 'assigned_creatives', 
            'workflow_state', 'principal_access'
        }
        
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Build dynamic UPDATE query
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                # For VARIANT columns, use PARSE_JSON(%s) and convert to JSON string
                if key in variant_columns:
                    set_clauses.append(f"{key} = PARSE_JSON(%s)")
                    values.append(json.dumps(value))
                else:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            # Always update updated_at
            set_clauses.append("updated_at = %s")
            values.append(datetime.utcnow())
            
            # Add WHERE clause value
            values.append(media_buy_id)
            
            sql = f"""
            UPDATE media_buys
            SET {', '.join(set_clauses)}
            WHERE media_buy_id = %s
            """
            
            cur.execute(sql, values)
            conn.commit()
            
            print(f"✅ Updated media buy in Snowflake: {media_buy_id}")
            
        finally:
            cur.close()
            conn.close()


# Global singleton instance
_snowflake_write_service: Optional[SnowflakeWriteService] = None


def get_snowflake_write_service() -> SnowflakeWriteService:
    """Get singleton Snowflake write service instance"""
    global _snowflake_write_service
    if _snowflake_write_service is None:
        _snowflake_write_service = SnowflakeWriteService()
    return _snowflake_write_service

