"""
Order Validator - Pure SQL Validation

Validates media_buy orders against master tables in Snowflake.
All validation is done via SQL - no business logic in code.

Validations:
1. Product exists and is active
2. Format IDs are valid
3. Principal is authorized
4. Budget within limits
5. Flight dates are valid
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a single validation check"""
    check_name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass 
class OrderValidation:
    """Complete validation result for an order"""
    media_buy_id: str
    all_passed: bool
    checks: List[ValidationResult]
    summary: str
    validated_at: str


class OrderValidator:
    """
    Validates media_buy orders against master tables.
    Uses Snowflake queries for all validation logic.
    """
    
    def __init__(self, snowflake_connection=None):
        """
        Initialize validator with Snowflake connection.
        
        Args:
            snowflake_connection: Active Snowflake connection or None to create new
        """
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
                logger.info("Snowflake connection established for validation")
            except Exception as e:
                logger.error(f"Failed to connect to Snowflake: {e}")
                self.conn = None
    
    def validate_order(self, media_buy_id: str) -> OrderValidation:
        """
        Run all validation checks on a media_buy order.
        
        Args:
            media_buy_id: The media_buy_id to validate
            
        Returns:
            OrderValidation with all check results
        """
        checks = []
        
        # Run all validation checks
        checks.append(self._validate_media_buy_exists(media_buy_id))
        checks.append(self._validate_products_exist(media_buy_id))
        checks.append(self._validate_formats_exist(media_buy_id))
        checks.append(self._validate_principal_authorized(media_buy_id))
        checks.append(self._validate_budget_limits(media_buy_id))
        checks.append(self._validate_flight_dates(media_buy_id))
        
        # Calculate overall result
        all_passed = all(check.passed for check in checks)
        passed_count = sum(1 for check in checks if check.passed)
        
        summary = f"{passed_count}/{len(checks)} checks passed"
        if all_passed:
            summary = f"✅ ALL VALIDATIONS PASSED ({passed_count}/{len(checks)})"
        else:
            failed = [c.check_name for c in checks if not c.passed]
            summary = f"❌ VALIDATION FAILED: {', '.join(failed)}"
        
        return OrderValidation(
            media_buy_id=media_buy_id,
            all_passed=all_passed,
            checks=checks,
            summary=summary,
            validated_at=datetime.now(timezone.utc).isoformat()
        )
    
    def _validate_media_buy_exists(self, media_buy_id: str) -> ValidationResult:
        """Check that the media_buy record exists"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT media_buy_id, campaign_name, total_budget, status
                FROM media_buys 
                WHERE media_buy_id = %s
            """, (media_buy_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return ValidationResult(
                    check_name="media_buy_exists",
                    passed=True,
                    message=f"Media buy '{row[1]}' found with budget ${row[2]:,.2f}",
                    details={"campaign_name": row[1], "budget": row[2], "status": row[3]}
                )
            else:
                return ValidationResult(
                    check_name="media_buy_exists",
                    passed=False,
                    message=f"Media buy '{media_buy_id}' not found"
                )
        except Exception as e:
            return ValidationResult(
                check_name="media_buy_exists",
                passed=False,
                message=f"Error checking media_buy: {str(e)}"
            )
    
    def _validate_products_exist(self, media_buy_id: str) -> ValidationResult:
        """Check that all products in packages exist in master table"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    p.product_id,
                    CASE WHEN pr.product_id IS NOT NULL THEN 'valid' ELSE 'invalid' END as status
                FROM packages p
                LEFT JOIN products pr ON p.product_id = pr.product_id AND pr.is_active = true
                WHERE p.media_buy_id = %s
            """, (media_buy_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            
            if not rows:
                return ValidationResult(
                    check_name="products_exist",
                    passed=False,
                    message="No packages found for this media buy"
                )
            
            invalid = [r[0] for r in rows if r[1] == 'invalid']
            valid = [r[0] for r in rows if r[1] == 'valid']
            
            if invalid:
                return ValidationResult(
                    check_name="products_exist",
                    passed=False,
                    message=f"Invalid products: {', '.join(invalid)}",
                    details={"invalid": invalid, "valid": valid}
                )
            
            return ValidationResult(
                check_name="products_exist",
                passed=True,
                message=f"All {len(valid)} products validated",
                details={"valid": valid}
            )
        except Exception as e:
            return ValidationResult(
                check_name="products_exist",
                passed=False,
                message=f"Error validating products: {str(e)}"
            )
    
    def _validate_formats_exist(self, media_buy_id: str) -> ValidationResult:
        """Check that all format_ids in package_formats are valid"""
        try:
            cursor = self.conn.cursor()
            # Check package_formats against known format IDs
            # For now, we'll check against a list of valid formats
            cursor.execute("""
                SELECT pf.format_id, p.package_id
                FROM package_formats pf
                JOIN packages p ON pf.package_id = p.id
                WHERE p.media_buy_id = %s
            """, (media_buy_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            
            if not rows:
                return ValidationResult(
                    check_name="formats_exist",
                    passed=True,
                    message="No package formats to validate (optional)"
                )
            
            # Valid format IDs from AdCP spec
            valid_formats = {
                'display_300x250', 'display_728x90', 'display_160x600', 'display_320x50',
                'video_16x9_15s', 'video_16x9_30s', 'video_9x16_15s',
                'native_content_feed', 'native_in_stream'
            }
            
            format_ids = [r[0] for r in rows]
            invalid = [f for f in format_ids if f not in valid_formats]
            
            if invalid:
                return ValidationResult(
                    check_name="formats_exist",
                    passed=False,
                    message=f"Invalid formats: {', '.join(invalid)}",
                    details={"invalid": invalid, "valid_formats": list(valid_formats)}
                )
            
            return ValidationResult(
                check_name="formats_exist",
                passed=True,
                message=f"All {len(format_ids)} formats validated",
                details={"formats": format_ids}
            )
        except Exception as e:
            return ValidationResult(
                check_name="formats_exist",
                passed=False,
                message=f"Error validating formats: {str(e)}"
            )
    
    def _validate_principal_authorized(self, media_buy_id: str) -> ValidationResult:
        """Check that the principal is authorized for this tenant"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    mb.principal_id,
                    p.name as principal_name,
                    p.access_level,
                    p.is_active
                FROM media_buys mb
                JOIN principals p ON mb.principal_id = p.principal_id
                WHERE mb.media_buy_id = %s
            """, (media_buy_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return ValidationResult(
                    check_name="principal_authorized",
                    passed=False,
                    message="Principal not found or not linked"
                )
            
            principal_id, name, access_level, is_active = row
            
            if not is_active:
                return ValidationResult(
                    check_name="principal_authorized",
                    passed=False,
                    message=f"Principal '{name}' is not active",
                    details={"principal_id": principal_id, "is_active": False}
                )
            
            return ValidationResult(
                check_name="principal_authorized",
                passed=True,
                message=f"Principal '{name}' authorized (access: {access_level})",
                details={"principal_id": principal_id, "name": name, "access_level": access_level}
            )
        except Exception as e:
            return ValidationResult(
                check_name="principal_authorized",
                passed=False,
                message=f"Error validating principal: {str(e)}"
            )
    
    def _validate_budget_limits(self, media_buy_id: str) -> ValidationResult:
        """Check that budget is within acceptable limits"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    mb.total_budget,
                    p.access_level,
                    CASE 
                        WHEN p.access_level = 'enterprise' THEN 1000000
                        WHEN p.access_level = 'preferred' THEN 500000
                        ELSE 100000
                    END as max_budget
                FROM media_buys mb
                JOIN principals p ON mb.principal_id = p.principal_id
                WHERE mb.media_buy_id = %s
            """, (media_buy_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return ValidationResult(
                    check_name="budget_limits",
                    passed=False,
                    message="Could not retrieve budget information"
                )
            
            budget, access_level, max_budget = row
            
            if budget > max_budget:
                return ValidationResult(
                    check_name="budget_limits",
                    passed=False,
                    message=f"Budget ${budget:,.2f} exceeds {access_level} limit of ${max_budget:,.2f}",
                    details={"budget": budget, "max_budget": max_budget, "access_level": access_level}
                )
            
            return ValidationResult(
                check_name="budget_limits",
                passed=True,
                message=f"Budget ${budget:,.2f} within {access_level} limit (${max_budget:,.2f})",
                details={"budget": budget, "max_budget": max_budget, "access_level": access_level}
            )
        except Exception as e:
            return ValidationResult(
                check_name="budget_limits",
                passed=False,
                message=f"Error validating budget: {str(e)}"
            )
    
    def _validate_flight_dates(self, media_buy_id: str) -> ValidationResult:
        """Check that flight dates are valid (start < end, not in past)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT flight_start_date, flight_end_date
                FROM media_buys 
                WHERE media_buy_id = %s
            """, (media_buy_id,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return ValidationResult(
                    check_name="flight_dates",
                    passed=False,
                    message="Could not retrieve flight dates"
                )
            
            start_date, end_date = row
            today = datetime.now(timezone.utc).date()
            
            issues = []
            
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if start_date >= end_date:
                issues.append("Start date must be before end date")
            
            # Note: We allow past dates for testing, but flag it
            if start_date < today:
                issues.append(f"Start date {start_date} is in the past")
            
            if issues:
                return ValidationResult(
                    check_name="flight_dates",
                    passed=False,
                    message="; ".join(issues),
                    details={"start": str(start_date), "end": str(end_date)}
                )
            
            return ValidationResult(
                check_name="flight_dates",
                passed=True,
                message=f"Flight: {start_date} to {end_date}",
                details={"start": str(start_date), "end": str(end_date)}
            )
        except Exception as e:
            return ValidationResult(
                check_name="flight_dates",
                passed=False,
                message=f"Error validating dates: {str(e)}"
            )
    
    def get_order_details(self, media_buy_id: str) -> Optional[Dict[str, Any]]:
        """Get full order details for CEM review"""
        try:
            cursor = self.conn.cursor()
            
            # Get media_buy details
            cursor.execute("""
                SELECT 
                    mb.media_buy_id,
                    mb.campaign_name,
                    mb.total_budget,
                    mb.currency,
                    mb.flight_start_date,
                    mb.flight_end_date,
                    mb.status,
                    mb.created_at,
                    p.name as principal_name,
                    p.access_level
                FROM media_buys mb
                JOIN principals p ON mb.principal_id = p.principal_id
                WHERE mb.media_buy_id = %s
            """, (media_buy_id,))
            
            mb_row = cursor.fetchone()
            
            if not mb_row:
                cursor.close()
                return None
            
            # Get packages
            cursor.execute("""
                SELECT 
                    pkg.product_id,
                    pkg.budget,
                    pkg.pacing,
                    pkg.pricing_strategy,
                    pr.name as product_name,
                    pr.pricing
                FROM packages pkg
                LEFT JOIN products pr ON pkg.product_id = pr.product_id
                WHERE pkg.media_buy_id = %s
            """, (media_buy_id,))
            
            pkg_rows = cursor.fetchall()
            cursor.close()
            
            # Build order details
            packages = []
            for pkg in pkg_rows:
                pricing = pkg[5]
                if isinstance(pricing, str):
                    pricing = json.loads(pricing)
                
                cpm = pricing.get('value', 0) if pricing else 0
                impressions = int(pkg[1] / (cpm / 1000)) if cpm > 0 else 0
                
                packages.append({
                    'product_id': pkg[0],
                    'product_name': pkg[4] or pkg[0],
                    'budget': pkg[1],
                    'pacing': pkg[2],
                    'pricing_strategy': pkg[3],
                    'cpm': cpm,
                    'estimated_impressions': impressions
                })
            
            return {
                'media_buy_id': mb_row[0],
                'campaign_name': mb_row[1],
                'total_budget': mb_row[2],
                'currency': mb_row[3],
                'flight_start_date': str(mb_row[4]),
                'flight_end_date': str(mb_row[5]),
                'status': mb_row[6],
                'created_at': str(mb_row[7]),
                'principal_name': mb_row[8],
                'access_level': mb_row[9],
                'packages': packages,
                'total_impressions': sum(p['estimated_impressions'] for p in packages)
            }
            
        except Exception as e:
            logger.error(f"Error getting order details: {e}")
            return None

