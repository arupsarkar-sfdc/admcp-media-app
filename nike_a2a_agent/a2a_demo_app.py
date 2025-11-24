"""
A2A Communication Demo - Streamlit App

Split-screen visualization showing real-time communication between
Nike A2A Campaign Agent and Yahoo A2A Sales Agent.

Left: Nike Agent (orchestrator)
Right: Yahoo Agent (advertising platform)
Center: Communication flow visualization
"""

import streamlit as st
import httpx
import json
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - Using deployed Heroku agents
NIKE_AGENT_URL = os.getenv(
    "NIKE_AGENT_URL",
    "https://nike-a2a-campaign-agent-b951306ad0ce.herokuapp.com/a2a/nike_campaign_agent"
)
YAHOO_AGENT_URL = os.getenv(
    "YAHOO_AGENT_URL",
    "https://yahoo-a2a-agent-72829d23cce8.herokuapp.com/a2a/yahoo_sales_agent"
)

# Page config
st.set_page_config(
    page_title="A2A Communication",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .agent-card {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .nike-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .yahoo-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    .message-box {
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-family: monospace;
        font-size: 14px;
        font-weight: 500;
    }
    .request-box {
        background-color: #1e3a5f;
        border-left: 4px solid #2196F3;
        color: #e3f2fd;
    }
    .request-box pre {
        color: #e3f2fd;
        margin: 0;
    }
    .response-box {
        background-color: #1b4d3e;
        border-left: 4px solid #8bc34a;
        color: #f1f8e9;
    }
    .response-box pre {
        color: #f1f8e9;
        margin: 0;
    }
    .error-box {
        background-color: #4d1f1f;
        border-left: 4px solid #f44336;
        color: #ffebee;
    }
    .error-box pre {
        color: #ffebee;
        margin: 0;
    }
    .flow-arrow {
        text-align: center;
        font-size: 24px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'communication_log' not in st.session_state:
    st.session_state.communication_log = []

# Helper functions
async def call_nike_agent(skill_id: str, input_data: str):
    """Call Nike A2A agent"""
    request_payload = {
        "jsonrpc": "2.0",
        "method": "task/execute",
        "params": {
            "skill_id": skill_id,
            "input": input_data
        },
        "id": len(st.session_state.communication_log) + 1
    }
    
    st.write(f"🔍 DEBUG: Calling Nike agent at: {NIKE_AGENT_URL}")
    st.write(f"🔍 DEBUG: Request payload: {json.dumps(request_payload, indent=2)}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            NIKE_AGENT_URL,
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        
        st.write(f"🔍 DEBUG: Response status: {response.status_code}")
        st.write(f"🔍 DEBUG: Response headers: {dict(response.headers)}")
        st.write(f"🔍 DEBUG: Response text: {response.text[:500]}")
        
        return request_payload, response.json()

async def call_yahoo_agent(skill_id: str, input_data: str):
    """Call Yahoo A2A agent directly"""
    request_payload = {
        "jsonrpc": "2.0",
        "method": "task/execute",
        "params": {
            "skill_id": skill_id,
            "input": input_data
        },
        "id": len(st.session_state.communication_log) + 1
    }
    
    st.write(f"🔍 DEBUG: Calling Yahoo agent at: {YAHOO_AGENT_URL}")
    st.write(f"🔍 DEBUG: Request payload: {json.dumps(request_payload, indent=2)}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            YAHOO_AGENT_URL,
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        
        st.write(f"🔍 DEBUG: Response status: {response.status_code}")
        st.write(f"🔍 DEBUG: Response headers: {dict(response.headers)}")
        st.write(f"🔍 DEBUG: Response text: {response.text[:500]}")
        
        return request_payload, response.json()

def log_communication(source: str, target: str, request: dict, response: dict):
    """Log communication event"""
    st.session_state.communication_log.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "source": source,
        "target": target,
        "request": request,
        "response": response
    })

# Header
st.title("🔄 A2A Agent Communication App")
st.markdown("**Real-time visualization of Agent-to-Agent (A2A) protocol communication**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.markdown("### 🏢 Agent Endpoints")
    st.text_input("Nike Agent URL", value=NIKE_AGENT_URL, disabled=True, key="nike_url_display")
    st.text_input("Yahoo Agent URL", value=YAHOO_AGENT_URL, disabled=True, key="yahoo_url_display")
    
    st.markdown("---")
    
    st.markdown("### 📊 Communication Stats")
    st.metric("Total Calls", len(st.session_state.communication_log))
    
    if st.button("🗑️ Clear Log", use_container_width=True):
        st.session_state.communication_log = []
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📖 About")
    st.markdown("""
    This demo shows:
    - **Nike Agent** (left) orchestrating campaigns
    - **Yahoo Agent** (right) providing advertising inventory
    - **A2A Protocol** (JSON-RPC 2.0) for communication
    """)

# Main content - Split screen
col_nike, col_center, col_yahoo = st.columns([2, 1, 2])

with col_nike:
    st.markdown('<div class="agent-card nike-card"><h2>👟 Nike Campaign Agent</h2><p>Campaign Orchestrator</p></div>', unsafe_allow_html=True)
    
    st.info("💡 **How it works**: Nike agent receives your request, then calls Yahoo agent internally to get advertising inventory. You'll see the full Nike → Yahoo → Nike flow in the log.")
    
    st.markdown("#### Available Skills")
    nike_skill = st.selectbox(
        "Select Nike Skill",
        ["test_connection", "plan_campaign"],
        key="nike_skill"
    )
    
    nike_input = st.text_area(
        "Input Message",
        value="Hello from Nike!",
        height=100,
        key="nike_input"
    )
    
    if st.button("🚀 Call Nike Agent", use_container_width=True, type="primary"):
        with st.spinner("Calling Nike agent..."):
            try:
                request, response = asyncio.run(call_nike_agent(nike_skill, nike_input))
                log_communication("User", "Nike", request, response)
                st.success("✅ Nike agent responded!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with col_center:
    st.markdown("### 🔄 Communication Flow")
    
    if len(st.session_state.communication_log) > 0:
        last_log = st.session_state.communication_log[-1]
        
        st.markdown('<div class="flow-arrow">⬇️</div>', unsafe_allow_html=True)
        st.markdown(f"**{last_log['source']}**")
        st.markdown('<div class="flow-arrow">➡️</div>', unsafe_allow_html=True)
        st.markdown(f"**{last_log['target']}**")
        st.markdown('<div class="flow-arrow">⬇️</div>', unsafe_allow_html=True)
        
        if "yahoo_response" in str(last_log['response']):
            st.markdown("**Nike → Yahoo**")
            st.markdown('<div class="flow-arrow">➡️</div>', unsafe_allow_html=True)
            st.markdown("**Yahoo → Nike**")
            st.markdown('<div class="flow-arrow">⬅️</div>', unsafe_allow_html=True)
    else:
        st.info("No communication yet.\n\nTry calling an agent!")

with col_yahoo:
    st.markdown('<div class="agent-card yahoo-card"><h2>🎯 Yahoo Sales Agent</h2><p>Advertising Platform</p></div>', unsafe_allow_html=True)
    
    st.info("💡 **How it works**: Yahoo agent responds directly with advertising data. This is a simple request → response flow (no nested calls).")
    
    st.markdown("#### Available Skills")
    yahoo_skill = st.selectbox(
        "Select Yahoo Skill",
        ["echo"],
        key="yahoo_skill"
    )
    
    yahoo_input = st.text_area(
        "Input Message",
        value="Hello from Yahoo!",
        height=100,
        key="yahoo_input"
    )
    
    if st.button("🚀 Call Yahoo Agent", use_container_width=True, type="primary"):
        with st.spinner("Calling Yahoo agent..."):
            try:
                request, response = asyncio.run(call_yahoo_agent(yahoo_skill, yahoo_input))
                log_communication("User", "Yahoo", request, response)
                st.success("✅ Yahoo agent responded!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Helper function to format response as natural language
def format_natural_language(log: dict) -> str:
    """Convert A2A response to natural language summary"""
    response = log.get("response", {})
    result = response.get("result", {})
    
    # Handle errors
    if "error" in response:
        error = response["error"]
        return f"❌ **Error**: {error.get('message', 'Unknown error')}"
    
    # Handle different skill types
    skill_id = log.get("request", {}).get("params", {}).get("skill_id", "")
    
    if skill_id == "echo":
        message = result.get("message", "")
        return f"✅ **Echo Response**: {message}"
    
    elif skill_id == "test_connection":
        yahoo_resp = result.get("yahoo_response", {})
        yahoo_msg = yahoo_resp.get("message", "")
        return f"""
✅ **Connection Test Successful!**

Nike agent successfully communicated with Yahoo agent via A2A protocol.

**Yahoo's Response**: {yahoo_msg}
"""
    
    elif skill_id == "plan_campaign":
        yahoo_resp = result.get("yahoo_response", {})
        
        # Check if this is Phase 2 (echo) or Phase 4 (real discovery)
        if "products_found" in result:
            # Phase 4 - Real product discovery
            products = result.get("recommended_products", [])
            total = result.get("products_found", 0)
            brief = result.get("campaign_brief", "")
            
            summary = f"""
✅ **Campaign Plan Created!**

**Campaign Brief**: {brief}

**Products Discovered**: {total} Yahoo advertising products found

**Top Recommendations**:
"""
            for idx, product in enumerate(products[:3], 1):
                name = product.get("name", "Unknown")
                cpm = product.get("pricing", {}).get("base_cpm", 0)
                reach = product.get("estimated_reach", 0)
                summary += f"\n{idx}. **{name}**\n   - CPM: ${cpm:.2f}\n   - Estimated Reach: {reach:,}\n"
            
            return summary
        else:
            # Phase 2 - Basic echo test
            yahoo_msg = yahoo_resp.get("message", "")
            return f"""
✅ **Campaign Planning Request Sent**

Nike agent forwarded your campaign request to Yahoo agent.

**Yahoo's Response**: {yahoo_msg}

💡 *Note: This is Phase 2 (connectivity test). Phase 4 will add real product discovery and campaign creation.*
"""
    
    elif skill_id == "discover_products":
        data = result.get("data", {})
        products = data.get("products", [])
        total = data.get("total_count", 0)
        brief = data.get("brief", "")
        
        summary = f"""
✅ **Products Discovered!**

**Search Brief**: {brief}

**Found**: {total} matching advertising products

**Products**:
"""
        for idx, product in enumerate(products[:5], 1):
            name = product.get("name", "Unknown")
            desc = product.get("description", "")
            cpm = product.get("pricing", {}).get("base_cpm", 0)
            budget = product.get("minimum_budget", 0)
            reach = product.get("estimated_reach", 0)
            
            summary += f"""
{idx}. **{name}**
   - {desc}
   - CPM: ${cpm:.2f} | Min Budget: ${budget:,} | Reach: {reach:,}
"""
        
        return summary
    
    elif skill_id == "create_campaign":
        data = result.get("data", {})
        campaign_id = data.get("campaign_id", "")
        campaign_name = data.get("campaign_name", "")
        packages = data.get("packages_created", 0)
        
        return f"""
✅ **Campaign Created Successfully!**

**Campaign Name**: {campaign_name}
**Campaign ID**: `{campaign_id}`
**Packages Created**: {packages}

**Data Written To**: Snowflake (instantly reflected in Data Cloud via Zero Copy)

🎉 Your campaign is now live and ready for delivery tracking!
"""
    
    elif skill_id == "get_campaign_status":
        data = result.get("data", {})
        campaign_id = data.get("campaign_id", "")
        impressions = data.get("impressions_delivered", 0)
        spend = data.get("spend", 0)
        clicks = data.get("clicks", 0)
        conversions = data.get("conversions", 0)
        
        return f"""
✅ **Campaign Status Retrieved**

**Campaign ID**: `{campaign_id}`

**Delivery Metrics**:
- 👁️ Impressions: {impressions:,}
- 💰 Spend: ${spend:,.2f}
- 🖱️ Clicks: {clicks:,}
- ✨ Conversions: {conversions:,}

**Data Source**: Salesforce Data Cloud (Snowflake Zero Copy)
"""
    
    else:
        # Generic response
        return f"✅ **Response received**: {json.dumps(result, indent=2)}"

# Communication Log
st.markdown("---")
st.markdown("## 📜 Communication Log")

if len(st.session_state.communication_log) == 0:
    st.info("No communication logged yet. Call an agent to see the communication flow!")
else:
    # Show logs in reverse chronological order
    for i, log in enumerate(reversed(st.session_state.communication_log)):
        with st.expander(f"🕐 {log['timestamp']} - {log['source']} → {log['target']}", expanded=(i == 0)):
            # Natural Language Summary (NEW!)
            st.markdown("### 💬 Summary")
            natural_summary = format_natural_language(log)
            st.markdown(natural_summary)
            
            st.markdown("---")
            
            # Technical Details (collapsible)
            with st.expander("🔧 Technical Details (JSON)", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📤 Request**")
                    st.markdown(f'<div class="message-box request-box"><pre>{json.dumps(log["request"], indent=2)}</pre></div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**📥 Response**")
                    if "error" in log["response"]:
                        st.markdown(f'<div class="message-box error-box"><pre>{json.dumps(log["response"], indent=2)}</pre></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="message-box response-box"><pre>{json.dumps(log["response"], indent=2)}</pre></div>', unsafe_allow_html=True)
                
                # Show nested Yahoo response if present
                if "result" in log["response"] and "yahoo_response" in log["response"]["result"]:
                    st.markdown("**🔗 Nested Yahoo Response**")
                    st.markdown(f'<div class="message-box response-box"><pre>{json.dumps(log["response"]["result"]["yahoo_response"], indent=2)}</pre></div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Built with Streamlit | A2A Protocol (JSON-RPC 2.0) | AdCP v2.3.0 Compliant</p>
</div>
""", unsafe_allow_html=True)

