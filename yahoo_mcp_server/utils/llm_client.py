"""
LLM Client Wrapper
Supports Gemini (primary) and OpenAI (fallback)
"""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Initialize clients
gemini_client = None
openai_client = None

try:
    import google.generativeai as genai
    if os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # Use gemini-1.5-flash (fast, efficient, available in v1beta)
        gemini_client = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("✓ Gemini client initialized (gemini-1.5-flash)")
except Exception as e:
    logger.warning(f"Gemini initialization failed: {e}")

try:
    from openai import OpenAI
    if os.getenv("OPENAI_API_KEY"):
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("✓ OpenAI client initialized")
except Exception as e:
    logger.warning(f"OpenAI initialization failed: {e}")


async def generate_completion(prompt: str, response_format: str = "json") -> Optional[str]:
    """
    Generate LLM completion with automatic fallback
    
    Args:
        prompt: Input prompt
        response_format: Expected format ('json' or 'text')
    
    Returns:
        Generated text or None if all clients fail
    """
    
    # Try Gemini first
    if gemini_client:
        try:
            response = await gemini_client.generate_content_async(prompt)
            text = response.text.strip()
            
            # Validate JSON if expected
            if response_format == "json":
                json.loads(text)  # Validate
            
            logger.info("✓ Gemini completion successful")
            return text
        except Exception as e:
            logger.warning(f"Gemini failed: {e}, trying OpenAI fallback...")
    
    # Fallback to OpenAI
    if openai_client:
        try:
            # Build request parameters
            request_params = {
                "model": "gpt-4-turbo-preview",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that provides structured responses. Always return valid JSON without markdown code blocks."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            
            # Add JSON mode if expected format is JSON
            if response_format == "json":
                request_params["response_format"] = {"type": "json_object"}
            
            response = openai_client.chat.completions.create(**request_params)
            text = response.choices[0].message.content.strip()
            
            # Strip markdown code blocks if present
            if text.startswith('```'):
                # Extract content between ```json and ``` or ``` and ```
                lines = text.split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]  # Remove opening ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]  # Remove closing ```
                text = '\n'.join(lines).strip()
            
            # Validate JSON if expected
            if response_format == "json":
                json.loads(text)  # Validate
            
            logger.info("✓ OpenAI completion successful")
            return text
        except Exception as e:
            logger.error(f"OpenAI also failed: {e}")
    
    logger.error("All LLM clients failed")
    return None


async def extract_campaign_criteria(brief: str, budget_range: Optional[list] = None) -> Dict[str, Any]:
    """
    Extract structured criteria from natural language campaign brief
    
    Args:
        brief: Natural language campaign description
        budget_range: Optional [min, max] budget
    
    Returns:
        Dict with extracted criteria (product_types, targeting, etc.)
    """
    prompt = f"""
Extract advertising campaign criteria from this brief:

Brief: "{brief}"

Return ONLY valid JSON (no markdown, no explanation) with this structure:
{{
    "product_types": ["display", "video", "native", "ctv"],
    "targeting": {{
        "geo": ["US", "CA"],
        "age": [25, 45],
        "interests": ["sports", "fitness", "running"]
    }},
    "budget_intent": "high" | "medium" | "low",
    "key_themes": ["performance", "brand awareness"]
}}

Infer product types, targeting, and themes from the brief context.
"""
    
    result = await generate_completion(prompt, response_format="json")
    
    if result:
        try:
            criteria = json.loads(result)
            logger.info(f"Extracted criteria: {criteria}")
            return criteria
        except:
            pass
    
    # Fallback: basic extraction
    return {
        "product_types": ["display", "video"],
        "targeting": {},
        "budget_intent": "medium",
        "key_themes": []
    }


async def rank_products(brief: str, products: list) -> list:
    """
    Rank products by relevance to campaign brief using LLM
    
    Args:
        brief: Campaign brief
        products: List of product dicts with id, name, description
    
    Returns:
        List of product IDs in ranked order
    """
    if not products:
        return []
    
    # Create product summaries
    summaries = []
    for i, p in enumerate(products):
        summary = f"{i+1}. ID: {p['product_id']}, Name: {p['name']}, Type: {p.get('product_type', 'unknown')}, Reach: {p.get('matched_reach', 0):,}"
        summaries.append(summary)
    
    prompt = f"""
Rank these advertising products by relevance to the campaign brief.

Brief: "{brief}"

Products:
{chr(10).join(summaries)}

Return ONLY a JSON array of product IDs in ranked order (most relevant first):
["product_id_1", "product_id_2", ...]

RESPOND WITH ONLY VALID JSON, NO EXPLANATION.
"""
    
    result = await generate_completion(prompt, response_format="json")
    
    if result:
        try:
            ranked_ids = json.loads(result)
            logger.info(f"Ranked {len(ranked_ids)} products")
            return ranked_ids
        except:
            pass
    
    # Fallback: return in original order
    return [p['product_id'] for p in products]

