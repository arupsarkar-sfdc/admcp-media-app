"""
AdCP Campaign Planner - Streamlit Web UI

A simple, fast web interface for the Yahoo MCP Server advertising agent.
Built with Streamlit for rapid deployment and ease of use.

Usage:
    uv run streamlit run streamlit_app.py
"""

import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from advertising_agent import AdvertisingAgent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AdCP Campaign Planner",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .tool-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎯 AdCP Campaign Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered campaign planning • AdCP v2.3.0 compliant</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # MCP Server URL
    mcp_url = st.text_input(
        "MCP Server URL",
        value=os.getenv("MCP_SERVER_URL", "https://yahoo-mcp-server-7c73bfc49f96.herokuapp.com/mcp"),
        help="URL of your Yahoo MCP Server"
    )
    
    # API Key status
    has_api_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    if has_api_key:
        st.success("✅ Anthropic API Key configured")
    else:
        st.error("❌ Anthropic API Key not found")
        st.info("Set ANTHROPIC_API_KEY in your .env file")
    
    st.divider()
    
    # Example Prompts (in sidebar)
    with st.expander("💡 Example Prompts", expanded=False):
        st.markdown("**Quick start prompts:**")
        
        if st.button("🔍 Discover Products", use_container_width=True, key="sidebar_discover"):
            st.session_state.example_prompt = "Show me advertising options for Nike running shoes with a $50,000 budget"
            st.rerun()
        
        if st.button("🚀 Create Campaign", use_container_width=True, key="sidebar_create"):
            st.session_state.example_prompt = "Create a $50K campaign for Nike targeting sports enthusiasts in Q1 2025"
            st.rerun()
        
        if st.button("📊 Check Performance", use_container_width=True, key="sidebar_performance"):
            st.session_state.example_prompt = "How is my Nike Air Max campaign performing?"
            st.rerun()
        
        if st.button("🎨 List Formats", use_container_width=True, key="sidebar_formats"):
            st.session_state.example_prompt = "What creative formats are available for campaigns?"
            st.rerun()
    
    # MCP Tools Available (in sidebar)
    with st.expander("🔧 MCP Tools Available", expanded=False):
        tools_info = [
            ("get_products", "🔍", "Discover inventory"),
            ("list_creative_formats", "🎨", "List ad formats"),
            ("create_media_buy", "🚀", "Create campaigns"),
            ("get_media_buy", "📋", "Get campaign details"),
            ("get_media_buy_delivery", "📊", "Get metrics"),
            ("update_media_buy", "⚙️", "Modify campaigns"),
            ("get_media_buy_report", "📈", "Generate reports"),
        ]
        
        for tool_name, emoji, description in tools_info:
            st.markdown(f"{emoji} **`{tool_name}`**")
            st.caption(description)
        
        st.caption("💡 Agent auto-selects tools!")
    
    st.divider()
    
    # Connection status
    st.header("🔌 Status")
    st.caption(f"**MCP Server:** {mcp_url}")
    st.caption(f"**Model:** Claude Sonnet 4.5")
    st.caption(f"**Data Source:** Snowflake via Data Cloud")

# Initialize agent (singleton pattern)
@st.cache_resource
def get_agent():
    """Initialize and cache the advertising agent"""
    agent = AdvertisingAgent(
        mcp_url=mcp_url,
        use_anthropic=True
    )
    return agent

# Async wrapper for agent initialization
async def initialize_agent():
    """Initialize agent with MCP server connection"""
    agent = get_agent()
    try:
        await agent.initialize()
        return agent, None
    except Exception as e:
        return None, str(e)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    with st.spinner("🔌 Connecting to MCP Server..."):
        agent, error = asyncio.run(initialize_agent())
        if error:
            st.error(f"❌ Failed to connect to MCP server: {error}")
            st.info("Make sure the MCP server is running and the URL is correct.")
            st.stop()
        else:
            st.session_state.agent = agent
            st.success("✅ Connected to MCP Server!")

# Display welcome message if no messages
if len(st.session_state.messages) == 0:
    st.info("""
    👋 **Welcome to AdCP Campaign Planner!**
    
    I'm your AI campaign planning assistant. I can help you:
    - 🔍 Discover advertising inventory
    - 🚀 Create AdCP-compliant campaigns
    - 📊 Monitor campaign performance
    - ⚙️ Optimize active campaigns
    - 📈 Generate analytics reports
    
    Use the sidebar to see example prompts and available MCP tools!
    """)

st.divider()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Clear Chat History Button (right under chat history)
if len(st.session_state.messages) > 0:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            if "agent" in st.session_state:
                st.session_state.agent.reset_conversation()
            st.rerun()

# Handle example prompt
if "example_prompt" in st.session_state:
    prompt = st.session_state.example_prompt
    del st.session_state.example_prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask me about campaigns...", key="chat_input"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.spinner("🤔 Thinking..."):
            try:
                # Call agent
                response = asyncio.run(st.session_state.agent.chat(prompt))
                
                # Display response
                message_placeholder.markdown(response)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_message = f"❌ **Error:** {str(e)}\n\nPlease try again or rephrase your question."
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Footer
st.divider()
st.caption("Connected to Yahoo MCP Server • AdCP v2.3.0 Compliant")
