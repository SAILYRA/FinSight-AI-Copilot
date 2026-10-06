"""
FinSight AI - Streamlit Interactive Frontend (Day 6-7)
Modern, portfolio-ready financial intelligence dashboard with expandable Citations & SQL inspection.
"""

import sys
import os
import time
import uuid
import streamlit as st

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import settings
from src.agent.graph import invoke_agent


# Page Configuration
st.set_page_config(
    page_title="FinSight AI — Enterprise Financial & Operations Copilot",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-badge {
        display: inline-block;
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .citation-card {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 10px 14px;
        border-radius: 4px;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    .sql-box {
        background-color: #0F172A;
        color: #F8FAFC;
        border-radius: 8px;
        padding: 12px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hello! I am **FinSight AI**, your enterprise intelligence copilot. I can query our **relational sales database** (`sales_data.db`) and search our **unstructured corporate documents** (Annual Reports, HR Policies, Technical SLAs, and Security Standards).\n\nHow can I help you today?",
            "citations": [],
            "sql_queries": [],
            "tools_called": [],
            "latency": 0.0
        }
    ]


# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/combo-chart.png", width=60)
    st.title("FinSight AI")
    st.caption("Hybrid RAG & Safe Text-to-SQL Agent")
    
    st.divider()
    
    st.markdown("### 🛠️ Architecture Stack")
    st.markdown(f"""
    - **LLM**: Groq `{settings.GROQ_MODEL}`
    - **Orchestration**: LangGraph ReAct Agent
    - **Dense RAG**: `BAAI/bge-small-en-v1.5` + ChromaDB
    - **Sparse RAG**: BM25 Keyword Search
    - **Structured SQL**: Safe Read-Only SQLite (`?mode=ro`)
    - **Session ID**: `{st.session_state.thread_id}`
    """)

    st.divider()

    st.markdown("### 💡 Quick Starters")
    
    sample_queries = [
        ("📊 Financial Highlights", "What was Acme Corp's total revenue and YoY growth in FY 2025?"),
        ("🏆 Top Customers", "Who are our top 3 highest revenue customers in the database?"),
        ("🏢 HR Leave Policy", "How many days of annual leave can I carry over into next year?"),
        ("⚙️ Cloud SLA Guarantee", "What is the SLA uptime guarantee for Mission-Critical Tier in ApexCloud?"),
        ("🔒 Cybersecurity SLA", "What is the incident response and escalation SLA for Severity 1 incidents?")
    ]

    for label, query in sample_queries:
        if st.button(label, use_container_width=True):
            st.session_state.pending_prompt = query

    st.divider()
    
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()


# --- Main Chat UI ---
st.markdown('<div class="main-header">💼 FinSight AI Copilot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Tool Enterprise Agent Combining Hybrid Document RAG with Safe Text-to-SQL</div>', unsafe_allow_html=True)

# Display chat messages
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    citations = msg.get("citations", [])
    sql_queries = msg.get("sql_queries", [])
    tools = msg.get("tools_called", [])
    latency = msg.get("latency", 0.0)

    with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🤖"):
        st.markdown(content)

        # Expandable inspection cards for assistant turns
        if role == "assistant" and (citations or sql_queries or tools):
            meta_cols = st.columns([1, 1, 3])
            if latency > 0:
                meta_cols[0].markdown(f"<span class='metric-badge'>⚡ {latency}s</span>", unsafe_allow_html=True)
            if tools:
                meta_cols[1].markdown(f"<span class='metric-badge'>🛠️ {len(tools)} Tool(s)</span>", unsafe_allow_html=True)

            # Sources Cited Tab
            if citations:
                with st.expander(f"📑 Sources Cited ({len(citations)} Reference{'s' if len(citations) > 1 else ''})"):
                    for c in citations:
                        st.markdown(f"<div class='citation-card'>📄 <b>{c}</b></div>", unsafe_allow_html=True)

            # SQL Queries Tab
            if sql_queries:
                with st.expander(f"💻 Generated SQL Query ({len(sql_queries)})"):
                    for q in sql_queries:
                        st.code(q, language="sql")


# Handle User Input
prompt = st.chat_input("Ask about company financials, HR policies, technical SLAs, or customer sales data...")

# Check if a starter prompt was clicked
if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt:
    # Append user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analyzing request and orchestrating tools..."):
            start_t = time.perf_counter()
            try:
                agent_res = invoke_agent(prompt, thread_id=st.session_state.thread_id)
                elapsed = round(time.perf_counter() - start_t, 2)
                response_text = agent_res["response"]
                citations = agent_res["citations"]
                sql_queries = agent_res["sql_queries"]
                tools = agent_res["tools_called"]

                st.markdown(response_text)

                # Show inspection cards
                if citations:
                    with st.expander(f"📑 Sources Cited ({len(citations)})"):
                        for c in citations:
                            st.markdown(f"<div class='citation-card'>📄 <b>{c}</b></div>", unsafe_allow_html=True)

                if sql_queries:
                    with st.expander(f"💻 Generated SQL Query ({len(sql_queries)})"):
                        for q in sql_queries:
                            st.code(q, language="sql")

                # Store in session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "citations": citations,
                    "sql_queries": sql_queries,
                    "tools_called": tools,
                    "latency": elapsed
                })
                
            except Exception as ex:
                err_msg = f"⚠️ **Agent Error**: {str(ex)}"
                st.error(err_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": err_msg,
                    "citations": [],
                    "sql_queries": [],
                    "tools_called": [],
                    "latency": 0.0
                })
