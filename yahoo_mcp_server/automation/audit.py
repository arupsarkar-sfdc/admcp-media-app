"""
Audit Logger - Log All CEM Operations

Logs all validation, approval, and rejection operations to the audit_log table.
Critical for compliance and traceability.
"""

import os
import json
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Logs all CEM operations to Snowflake audit_log table.
    
    Operations logged:
    - cem_validation: Order validated
    - cem_approval_requested: Sent to CEM for approval
    - cem_approved: CEM approved the order
    - cem_rejected: CEM rejected the order
    - cem_review_requested: CEM requested changes
    """
    
    def __init__(self, snowflake_connection=None):
        """Initialize with Snowflake connection"""
        self.conn = snowflake_connection
        self._ensure_connection()
    
    def _ensure_connection(self):
        """Ensure Snowflake connection is available"""
        if self.conn is None:
            try:
                import snowflake.connector
                self.conn = snowflake.connector.connect(
                    account=os.environ.get('SNOWFLAKE_ACCOUNT'),
                    user=os.environ.get('SNOWFLAKE_USER'),
                    password=os.environ.get('SNOWFLAKE_PASSWORD'),
                    database=os.environ.get('SNOWFLAKE_DATABASE', 'DEMO_BYOL_QUERY_FEDERATION_FOR_SALESFORCE'),
                    schema=os.environ.get('SNOWFLAKE_SCHEMA', 'PUBLIC'),
                    warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
                    role=os.environ.get('SNOWFLAKE_ROLE', 'SYSADMIN')
                )
                logger.info("Snowflake connection established for audit logging")
            except Exception as e:
                logger.error(f"Failed to connect to Snowflake for audit: {e}")
                self.conn = None
    
    def log(
        self,
        operation: str,
        media_buy_id: str,
        principal_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        request_params: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        status: str = 'success',
        performed_by: Optional[str] = None
    ) -> Optional[str]:
        """
        Log an operation to the audit_log table.
        
        Args:
            operation: Operation type (cem_validation, cem_approved, etc.)
            media_buy_id: The media_buy being operated on
            principal_id: Principal involved (advertiser)
            tenant_id: Tenant involved (Yahoo)
            request_params: Input parameters
            response_data: Output/result data
            status: success, error, pending
            performed_by: CEM user who performed action (for approvals)
            
        Returns:
            Audit log entry ID or None if failed
        """
        if self.conn is None:
            logger.warning("No Snowflake connection, audit log skipped")
            return None
        
        try:
            audit_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Convert dicts to JSON strings for VARIANT columns
            request_json = json.dumps(request_params) if request_params else '{}'
            response_json = json.dumps(response_data) if response_data else '{}'
            
            cursor = self.conn.cursor()
            # Use SELECT with PARSE_JSON instead of VALUES clause
            cursor.execute("""
                INSERT INTO audit_log (
                    id,
                    principal_id,
                    tenant_id,
                    operation,
                    tool_name,
                    request_params,
                    response_data,
                    status,
                    timestamp
                ) 
                SELECT %s, %s, %s, %s, %s, PARSE_JSON(%s), PARSE_JSON(%s), %s, %s
            """, (
                audit_id,
                principal_id,
                tenant_id,
                operation,
                f"cem_workflow:{media_buy_id}",
                request_json,
                response_json,
                status,
                timestamp
            ))
            
            self.conn.commit()
            cursor.close()
            
            logger.info(f"Audit logged: {operation} for {media_buy_id} (id: {audit_id})")
            return audit_id
            
        except Exception as e:
            logger.error(f"Failed to log audit: {e}")
            return None
    
    def log_validation(
        self,
        media_buy_id: str,
        validation_result: Dict[str, Any],
        principal_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Optional[str]:
        """Log a validation operation"""
        return self.log(
            operation='cem_validation',
            media_buy_id=media_buy_id,
            principal_id=principal_id,
            tenant_id=tenant_id,
            request_params={'media_buy_id': media_buy_id},
            response_data=validation_result,
            status='success' if validation_result.get('all_passed') else 'failed'
        )
    
    def log_approval_requested(
        self,
        media_buy_id: str,
        order_details: Dict[str, Any],
        validation_summary: str,
        cem_channel: str
    ) -> Optional[str]:
        """Log that approval was requested from CEM"""
        return self.log(
            operation='cem_approval_requested',
            media_buy_id=media_buy_id,
            principal_id=order_details.get('principal_id'),
            tenant_id=order_details.get('tenant_id'),
            request_params={
                'media_buy_id': media_buy_id,
                'campaign_name': order_details.get('campaign_name'),
                'total_budget': order_details.get('total_budget'),
                'cem_channel': cem_channel
            },
            response_data={
                'validation_summary': validation_summary,
                'status': 'pending_cem_approval'
            },
            status='pending'
        )
    
    def log_approved(
        self,
        media_buy_id: str,
        approved_by: str,
        comments: Optional[str] = None
    ) -> Optional[str]:
        """Log CEM approval"""
        return self.log(
            operation='cem_approved',
            media_buy_id=media_buy_id,
            request_params={
                'media_buy_id': media_buy_id,
                'approved_by': approved_by
            },
            response_data={
                'comments': comments,
                'new_status': 'active'
            },
            status='success',
            performed_by=approved_by
        )
    
    def log_rejected(
        self,
        media_buy_id: str,
        rejected_by: str,
        reason: str
    ) -> Optional[str]:
        """Log CEM rejection"""
        return self.log(
            operation='cem_rejected',
            media_buy_id=media_buy_id,
            request_params={
                'media_buy_id': media_buy_id,
                'rejected_by': rejected_by
            },
            response_data={
                'reason': reason,
                'new_status': 'rejected'
            },
            status='success',
            performed_by=rejected_by
        )
    
    def log_review_requested(
        self,
        media_buy_id: str,
        requested_by: str,
        comments: str
    ) -> Optional[str]:
        """Log CEM review/changes request"""
        return self.log(
            operation='cem_review_requested',
            media_buy_id=media_buy_id,
            request_params={
                'media_buy_id': media_buy_id,
                'requested_by': requested_by
            },
            response_data={
                'comments': comments,
                'new_status': 'pending_changes'
            },
            status='pending',
            performed_by=requested_by
        )

