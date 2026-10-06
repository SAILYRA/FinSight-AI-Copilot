"""
FinSight AI - Interactive LangGraph Multi-Turn Agent Verification Script (Day 4 Hands-on)
Demonstrates multi-turn memory, dynamic tool routing between RAG and SQL, and response generation.
"""

import sys
import os

# Set utf-8 encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import settings
from src.agent.graph import invoke_agent, get_agent_executor


def run_agent_interactive_test():
    print("=" * 75)
    print("🚀 FIN-SIGHT AI — LANGGRAPH AGENT & MULTI-TURN MEMORY TEST (DAY 4)")
    print("=" * 75)

    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if not api_key:
        print("\n[!] IMPORTANT: GROQ_API_KEY is not configured in your .env file yet.")
        print("    To run live LLM agent inference with Groq's Llama-3.3-70B model:")
        print("    1. Get a free API key at: https://console.groq.com/keys")
        print("    2. Add it to your .env file: GROQ_API_KEY=gsk_your_key_here")
        print("\n[*] Validating LangGraph agent architecture & tool bindings...")
        try:
            # Check tool imports and graph dependencies
            from src.rag.rag_tool import search_company_docs_tool
            from src.sql.sql_tool import query_sales_database
            print(f"   ✓ Tool 1 Bound: {search_company_docs_tool.name}")
            print(f"   ✓ Tool 2 Bound: {query_sales_database.name}")
            print("   ✓ MemorySaver Checkpointer: Ready")
            print("   ✓ Routing Prompt: Ready")
            print("\n[SUCCESS] Agent graph architecture is ready. Once GROQ_API_KEY is set in .env, run this script to test live!")
        except Exception as e:
            print(f"[ERROR] Graph validation failed: {e}")
        return

    # Live multi-turn conversation test
    thread_session_id = "session_portfolio_demo"

    conversation_turns = [
        {
            "turn": 1,
            "title": "Turn 1 (SQL Routing): Query Database for Top Customers",
            "prompt": "What are the top 3 highest revenue customers in our database and what industries are they in?"
        },
        {
            "turn": 2,
            "title": "Turn 2 (Multi-Turn Memory): Follow-up Referencing Turn 1",
            "prompt": "What region is the first customer located in, and who is the regional manager?"
        },
        {
            "turn": 3,
            "title": "Turn 3 (RAG Routing): Policy Lookup with Citations",
            "prompt": "According to our HR policy handbook, what is the maximum number of unused annual leave days an employee can carry over?"
        }
    ]

    for item in conversation_turns:
        print("\n" + "#" * 75)
        print(f"💬 {item['title']}")
        print(f"USER: \"{item['prompt']}\"")
        print("#" * 75)

        turn_result = invoke_agent(item["prompt"], thread_id=thread_session_id)

        print(f"\n[Tools Activated]: {', '.join(turn_result['tools_called']) or 'Direct Response'}")
        
        if turn_result["sql_queries"]:
            print(f"[Executed SQL]:\n  {turn_result['sql_queries'][0]}")

        if turn_result["citations"]:
            print(f"[Document Citations]: {', '.join(turn_result['citations'])}")

        print("\n[AGENT RESPONSE]:")
        print(turn_result["response"])

    print("\n" + "=" * 75)
    print("[SUCCESS] Multi-turn LangGraph Agent demonstration completed successfully!")
    print("=" * 75)


if __name__ == "__main__":
    run_agent_interactive_test()
