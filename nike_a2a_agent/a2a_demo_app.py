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
    page_title="A2A Communication Demo",
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
st.title("🔄 A2A Agent Communication Demo")
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

# Communication Log
st.markdown("---")
st.markdown("## 📜 Communication Log")

if len(st.session_state.communication_log) == 0:
    st.info("No communication logged yet. Call an agent to see the communication flow!")
else:
    # Show logs in reverse chronological order
    for i, log in enumerate(reversed(st.session_state.communication_log)):
        with st.expander(f"🕐 {log['timestamp']} - {log['source']} → {log['target']}", expanded=(i == 0)):
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

