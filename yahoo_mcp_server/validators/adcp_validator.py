"""
AdCP v2.3.0 Validator
Validates package-based media buy structure for Ad Context Protocol compliance

Author: Yahoo MCP Server Team
Protocol: AdCP v2.3.0
"""
from typing import List, Dict, Any, Tuple


class AdCPValidator:
    """Validates AdCP v2.3.0 package structure"""
    
    # Valid creative format IDs from list_creative_formats
    VALID_FORMAT_IDS = {
        "display_300x250",
        "display_728x90",
        "display_160x600",
        "video_preroll_640x480",
        "video_midroll_1280x720",
        "video_outstream_1920x1080",
        "native_feed",
        "native_content",
        "native_app_install"
    }
    
    VALID_PACING_STRATEGIES = {"even", "asap", "frontloaded"}
    VALID_PRICING_STRATEGIES = {"cpm", "cpc", "cpa", "cpv"}
    
    @classmethod
    def validate_packages(cls, packages: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validate AdCP v2.3.0 package structure.
        
        Args:
            packages: List of package dictionaries
            
        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, "error description") if invalid
        """
        if not isinstance(packages, list):
            return False, "packages must be a list"
        
        if len(packages) == 0:
            return False, "packages list cannot be empty"
        
        for idx, package in enumerate(packages):
            if not isinstance(package, dict):
                return False, f"Package {idx} must be a dictionary"
            
            # Validate required fields
            is_valid, error = cls._validate_required_fields(package, idx)
            if not is_valid:
                return False, error
            
            # Validate format_ids structure
            is_valid, error = cls._validate_format_ids(package.get("format_ids", []), idx)
            if not is_valid:
                return False, error
            
            # Validate optional fields if present
            is_valid, error = cls._validate_optional_fields(package, idx)
            if not is_valid:
                return False, error
        
        return True, ""
    
    @classmethod
    def _validate_required_fields(cls, package: Dict[str, Any], idx: int) -> Tuple[bool, str]:
        """Validate required fields in package"""
        # product_id (required)
        if "product_id" not in package:
            return False, f"Package {idx} missing required field: product_id"
        if not isinstance(package["product_id"], str) or not package["product_id"]:
            return False, f"Package {idx} product_id must be a non-empty string"
        
        # budget (required)
        if "budget" not in package:
            return False, f"Package {idx} missing required field: budget"
        if not isinstance(package["budget"], (int, float)):
            return False, f"Package {idx} budget must be a number"
        if package["budget"] <= 0:
            return False, f"Package {idx} budget must be greater than 0"
        
        # format_ids (required for AdCP v2.3.0)
        if "format_ids" not in package:
            return False, f"Package {idx} missing required field: format_ids (AdCP v2.3.0)"
        
        return True, ""
    
    @classmethod
    def _validate_format_ids(cls, format_ids: List[Dict[str, str]], pkg_idx: int) -> Tuple[bool, str]:
        """
        Validate format_ids structure per AdCP v2.3.0.
        
        Each format_id must be:
        {
            "agent_url": "http://localhost:8080/mcp",
            "id": "display_300x250"
        }
        """
        if not isinstance(format_ids, list):
            return False, f"Package {pkg_idx} format_ids must be a list"
        
        if len(format_ids) == 0:
            return False, f"Package {pkg_idx} format_ids list cannot be empty (AdCP v2.3.0 requirement)"
        
        for fmt_idx, format_id in enumerate(format_ids):
            if not isinstance(format_id, dict):
                return False, f"Package {pkg_idx} format_ids[{fmt_idx}] must be a dictionary"
            
            # Validate agent_url
            if "agent_url" not in format_id:
                return False, f"Package {pkg_idx} format_ids[{fmt_idx}] missing required field: agent_url"
            if not isinstance(format_id["agent_url"], str) or not format_id["agent_url"]:
                return False, f"Package {pkg_idx} format_ids[{fmt_idx}] agent_url must be a non-empty string"
            
            # Validate id
            if "id" not in format_id:
                return False, f"Package {pkg_idx} format_ids[{fmt_idx}] missing required field: id"
            if not isinstance(format_id["id"], str) or not format_id["id"]:
                return False, f"Package {pkg_idx} format_ids[{fmt_idx}] id must be a non-empty string"
            
            # Validate id is in our supported formats
            if format_id["id"] not in cls.VALID_FORMAT_IDS:
                return False, (
                    f"Package {pkg_idx} format_ids[{fmt_idx}] id '{format_id['id']}' not supported. "
                    f"Use list_creative_formats tool to discover valid format IDs."
                )
        
        return True, ""
    
    @classmethod
    def _validate_optional_fields(cls, package: Dict[str, Any], idx: int) -> Tuple[bool, str]:
        """Validate optional fields if present"""
        # targeting_overlay (optional)
        if "targeting_overlay" in package:
            if not isinstance(package["targeting_overlay"], dict):
                return False, f"Package {idx} targeting_overlay must be a dictionary"
        
        # pacing (optional)
        if "pacing" in package:
            if not isinstance(package["pacing"], str):
                return False, f"Package {idx} pacing must be a string"
            if package["pacing"] not in cls.VALID_PACING_STRATEGIES:
                return False, (
                    f"Package {idx} pacing '{package['pacing']}' invalid. "
                    f"Valid options: {', '.join(cls.VALID_PACING_STRATEGIES)}"
                )
        
        # pricing_strategy (optional)
        if "pricing_strategy" in package:
            if not isinstance(package["pricing_strategy"], str):
                return False, f"Package {idx} pricing_strategy must be a string"
            if package["pricing_strategy"] not in cls.VALID_PRICING_STRATEGIES:
                return False, (
                    f"Package {idx} pricing_strategy '{package['pricing_strategy']}' invalid. "
                    f"Valid options: {', '.join(cls.VALID_PRICING_STRATEGIES)}"
                )
        
        return True, ""
    
    @classmethod
    def calculate_total_budget(cls, packages: List[Dict[str, Any]]) -> float:
        """Calculate total budget across all packages"""
        return sum(pkg.get("budget", 0) for pkg in packages)

