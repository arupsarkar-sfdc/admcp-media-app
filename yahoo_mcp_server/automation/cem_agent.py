"""
CEM Agent - AI-Powered Order Summarization

Uses Claude to generate clear, explicit explanations of orders for CEM review.
The explanation must be so clear that a CEM can approve/reject based on it alone.

Key outputs:
- Order summary (human-readable)
- Validation results (with explanations)
- Risk flags (anomalies, concerns)
- Recommendation (approve/review/reject)
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Import Anthropic for Claude
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


@dataclass
class CEMRecommendation:
    """AI recommendation for CEM"""
    action: str  # 'approve', 'review', 'reject'
    confidence: str  # 'high', 'medium', 'low'
    reason: str
    risk_level: str  # 'low', 'medium', 'high'


@dataclass
class CEMSummary:
    """Complete summary for CEM review"""
    media_buy_id: str
    order_summary: str  # Human-readable summary
    validation_explanation: str  # What was validated and results
    risk_flags: List[str]  # Any concerns
    recommendation: CEMRecommendation
    generated_at: str
    
    def to_slack_blocks(self) -> List[Dict]:
        """Convert to Slack Block Kit format"""
        # Risk emoji based on level
        risk_emoji = {
            'low': '🟢',
            'medium': '🟡', 
            'high': '🔴'
        }
        
        # Action emoji
        action_emoji = {
            'approve': '✅',
            'review': '🔍',
            'reject': '❌'
        }
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔔 New Order Pending CEM Approval",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Order ID:* `{self.media_buy_id}`"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📋 Order Summary*\n{self.order_summary}"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*✅ Validation Results*\n{self.validation_explanation}"
                }
            }
        ]
        
        # Add risk flags if any
        if self.risk_flags:
            flags_text = "\n".join([f"• {flag}" for flag in self.risk_flags])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*⚠️ Risk Flags*\n{flags_text}"
                }
            })
        
        # Add recommendation
        rec = self.recommendation
        blocks.extend([
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*🤖 AI Recommendation*\n"
                        f"{action_emoji.get(rec.action, '❓')} *{rec.action.upper()}* "
                        f"(Confidence: {rec.confidence})\n"
                        f"{risk_emoji.get(rec.risk_level, '⚪')} Risk Level: {rec.risk_level}\n\n"
                        f"_{rec.reason}_"
                    )
                }
            },
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Approve", "emoji": True},
                        "style": "primary",
                        "action_id": f"cem_approve_{self.media_buy_id}",
                        "value": self.media_buy_id
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Reject", "emoji": True},
                        "style": "danger",
                        "action_id": f"cem_reject_{self.media_buy_id}",
                        "value": self.media_buy_id
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "📝 Request Changes", "emoji": True},
                        "action_id": f"cem_review_{self.media_buy_id}",
                        "value": self.media_buy_id
                    }
                ]
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Generated at {self.generated_at} | Human-in-the-loop required"
                    }
                ]
            }
        ])
        
        return blocks


class CEMAgent:
    """
    AI Agent for CEM order review.
    
    Takes order details and validation results, produces clear
    explanation for human CEM to approve/reject.
    """
    
    SYSTEM_PROMPT = """You are a Campaign Escalation Manager (CEM) assistant at Yahoo Advertising.

Your job is to review advertising orders and provide CLEAR, EXPLICIT explanations so a human CEM can make an approval decision.

You will receive:
1. Order details (campaign name, budget, products, dates)
2. Validation results (what checks passed/failed)

You must produce:
1. A human-readable summary of the order (2-3 sentences)
2. An explanation of validation results (what was checked, what passed/failed)
3. Any risk flags (unusual budget, new client, date issues, etc.)
4. A recommendation (APPROVE, REVIEW, or REJECT) with clear reasoning

GUIDELINES:
- Be EXPLICIT - the CEM should understand everything without looking up additional info
- Flag anomalies - unusual budgets, new clients, short flight dates
- Be concise but complete
- Format monetary values nicely ($50,000 not 50000)
- Include all relevant details in the summary

RECOMMENDATION CRITERIA:
- APPROVE: All validations pass, no risk flags, established client, normal budget
- REVIEW: All validations pass but has risk flags (high budget, new client, etc.)
- REJECT: Any validation failed

OUTPUT FORMAT (JSON):
{
    "order_summary": "Clear 2-3 sentence summary of what this order is",
    "validation_explanation": "What was validated and the results",
    "risk_flags": ["flag1", "flag2"] or [],
    "recommendation": {
        "action": "approve|review|reject",
        "confidence": "high|medium|low",
        "reason": "Clear explanation for the recommendation",
        "risk_level": "low|medium|high"
    }
}"""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize CEM Agent with Claude"""
        if not HAS_ANTHROPIC:
            raise ValueError("anthropic package not installed")
        
        api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"
        
        logger.info("CEMAgent initialized with Claude")
    
    def generate_summary(
        self,
        order_details: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> CEMSummary:
        """
        Generate a complete summary for CEM review.
        
        Args:
            order_details: Order information from validator.get_order_details()
            validation_result: Validation results from validator.validate_order()
            
        Returns:
            CEMSummary with all information for CEM review
        """
        # Build prompt
        prompt = f"""Please review this advertising order and provide a summary for CEM approval.

ORDER DETAILS:
- Campaign Name: {order_details.get('campaign_name')}
- Media Buy ID: {order_details.get('media_buy_id')}
- Client: {order_details.get('principal_name')} (Access Level: {order_details.get('access_level')})
- Total Budget: ${order_details.get('total_budget', 0):,.2f} {order_details.get('currency', 'USD')}
- Flight Dates: {order_details.get('flight_start_date')} to {order_details.get('flight_end_date')}
- Status: {order_details.get('status')}
- Created: {order_details.get('created_at')}

PACKAGES:
"""
        for pkg in order_details.get('packages', []):
            prompt += f"""
- Product: {pkg.get('product_name')} ({pkg.get('product_id')})
  Budget: ${pkg.get('budget', 0):,.2f}
  CPM: ${pkg.get('cpm', 0):.2f}
  Est. Impressions: {pkg.get('estimated_impressions', 0):,}
  Pacing: {pkg.get('pacing')}
"""

        prompt += f"""
Total Estimated Impressions: {order_details.get('total_impressions', 0):,}

VALIDATION RESULTS:
- Overall: {'✅ ALL PASSED' if validation_result.get('all_passed') else '❌ SOME FAILED'}
- Summary: {validation_result.get('summary')}

Individual Checks:
"""
        for check in validation_result.get('checks', []):
            status = '✅' if check.get('passed') else '❌'
            prompt += f"- {status} {check.get('check_name')}: {check.get('message')}\n"
        
        prompt += """
Based on this information, provide your analysis in the JSON format specified."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract response text
            response_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_text = block.text
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text.strip())
            
            # Build CEMSummary
            rec_data = result.get('recommendation', {})
            recommendation = CEMRecommendation(
                action=rec_data.get('action', 'review'),
                confidence=rec_data.get('confidence', 'medium'),
                reason=rec_data.get('reason', 'Unable to determine'),
                risk_level=rec_data.get('risk_level', 'medium')
            )
            
            return CEMSummary(
                media_buy_id=order_details.get('media_buy_id', 'unknown'),
                order_summary=result.get('order_summary', 'No summary generated'),
                validation_explanation=result.get('validation_explanation', 'No explanation'),
                risk_flags=result.get('risk_flags', []),
                recommendation=recommendation,
                generated_at=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}")
            # Return a safe fallback
            return CEMSummary(
                media_buy_id=order_details.get('media_buy_id', 'unknown'),
                order_summary=f"Order for {order_details.get('campaign_name')} - ${order_details.get('total_budget', 0):,.2f}",
                validation_explanation=validation_result.get('summary', 'Validation completed'),
                risk_flags=["AI summarization failed - manual review required"],
                recommendation=CEMRecommendation(
                    action='review',
                    confidence='low',
                    reason='AI summarization failed, requires manual review',
                    risk_level='medium'
                ),
                generated_at=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            )
        except Exception as e:
            logger.error(f"Error generating CEM summary: {e}")
            raise

