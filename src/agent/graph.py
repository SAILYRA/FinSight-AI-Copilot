"""
FinSight AI - LangGraph Multi-Tool ReAct Agent with Memory (Day 4)
Orchestrates Document RAG (search_company_docs_tool) and Safe Text-to-SQL (query_sales_database)
using Groq's Llama-3.3-70B model and MemorySaver for multi-turn session persistence.
"""

import os
import re
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from src.config import settings
from src.rag.rag_tool import search_company_docs_tool
from src.sql.sql_tool import query_sales_database
from src.agent.prompts import FINSIGHT_SYSTEM_PROMPT


# Shared in-memory checkpointer for multi-turn conversations
global_checkpointer = MemorySaver()


def get_agent_executor(checkpointer: Optional[MemorySaver] = None):
    """
    Constructs and returns the LangGraph ReAct agent.
    """
    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set in environment, .env file, or Streamlit Secrets. "
            "Please obtain a free API key from https://console.groq.com/keys and add GROQ_API_KEY=gsk_... in your Streamlit Cloud Secrets."
        )

    llm = ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=api_key,
        temperature=settings.TEMPERATURE
    )

    tools = [search_company_docs_tool, query_sales_database]
    cp = checkpointer or global_checkpointer

    agent = create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=cp,
        prompt=FINSIGHT_SYSTEM_PROMPT
    )
    return agent


def invoke_agent(
    message: str,
    thread_id: str = "default_session"
) -> Dict[str, Any]:
    """
    Executes a multi-turn conversation turn with thread persistence.
    Extracts citations, SQL queries, and tool call inspection metadata.
    """
    agent = get_agent_executor()
    config = {"configurable": {"thread_id": thread_id}}

    inputs = {"messages": [HumanMessage(content=message)]}
    result = agent.invoke(inputs, config=config)

    messages = result["messages"]
    last_message = messages[-1]
    response_text = last_message.content if isinstance(last_message, AIMessage) else str(last_message)

    # Extract executed SQL queries & citations from intermediate tool messages
    sql_queries: List[str] = []
    citations: List[str] = []
    tools_called: List[str] = []

    for msg in messages:
        if isinstance(msg, ToolMessage):
            t_name = msg.name or "tool"
            tools_called.append(t_name)
            content = str(msg.content)
            
            # Extract SQL queries
            sql_matches = re.findall(r"```sql\s*(.*?)\s*```", content, flags=re.DOTALL)
            for sm in sql_matches:
                if sm.strip() not in sql_queries:
                    sql_queries.append(sm.strip())
                    
            # Extract document citations
            cite_matches = re.findall(r"\[Source:\s*([^\|\]]+)\s*\|\s*Page:\s*(\d+)\]", content)
            for f_name, p_num in cite_matches:
                cite_str = f"{f_name.strip()} (Page {p_num.strip()})"
                if cite_str not in citations:
                    citations.append(cite_str)

    return {
        "thread_id": thread_id,
        "input_message": message,
        "response": response_text,
        "tools_called": list(set(tools_called)),
        "sql_queries": sql_queries,
        "citations": citations,
        "raw_messages_count": len(messages)
    }


if __name__ == "__main__":
    import sys
    # Demo test runner if API key is present
    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[!] Note: GROQ_API_KEY is not configured yet. Set it in .env to run live agent queries.")
        print("[!] The agent architecture, tools, and LangGraph state graph are ready.")
    else:
        print("[*] Running Agent Multi-Turn Test with Groq...")
        r1 = invoke_agent("Who is the regional manager for North America - East?", thread_id="test_session")
        print("\nTurn 1 Response:\n", r1["response"])
        
        r2 = invoke_agent("What is their headquarters location and country?", thread_id="test_session")
        print("\nTurn 2 (Memory Follow-up) Response:\n", r2["response"])
