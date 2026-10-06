"""
FinSight AI - LangChain Text-to-SQL Tool (Day 3)
Exposes query_sales_database tool decorated with LangChain's @tool.
Generates valid SQLite queries from natural language, validates read-only security,
and returns both the raw SQL query and formatted markdown tabular results.
"""

import os
import re
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from src.config import settings
from src.sql.database import get_database, SafeSQLiteDatabase

SQL_GENERATION_PROMPT = """You are an expert SQL engineer. Generate a valid, optimized SQLite SQL query based on the user's question and the provided database schema.

{schema_context}

CRITICAL RULES:
1. Return ONLY the raw SQL query. Do NOT wrap it in backticks, markdown, or explain it.
2. Only write read-only SELECT or WITH statements. Never write DROP, DELETE, INSERT, UPDATE, or ALTER.
3. Use proper SQLite JOINs (e.g., JOIN customers ON orders.customer_id = customers.customer_id).
4. Limit the query to 50 rows if unspecified.

User Question: {question}
SQL Query:"""


def generate_sql_from_question(question: str, db: SafeSQLiteDatabase = None) -> str:
    """
    Uses LLM (Groq) to convert a natural language question into valid SQLite query.
    If no API key is set, attempts heuristics or expects direct SQL.
    """
    database = db or get_database()
    schema_context = database.get_schema_context()

    api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

    if not api_key:
        # If question is already valid SQL, return as-is
        if question.strip().upper().startswith(("SELECT", "WITH")):
            return question.strip()
        raise ValueError(
            "GROQ_API_KEY is not configured in .env or Streamlit Secrets. Please provide a direct SQL statement or set GROQ_API_KEY to use natural language Text-to-SQL."
        )

    llm = ChatGroq(
        api_key=api_key,
        model=settings.GROQ_MODEL,
        temperature=0.0
    )

    prompt = PromptTemplate(
        template=SQL_GENERATION_PROMPT,
        input_variables=["schema_context", "question"]
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "schema_context": schema_context,
        "question": question
    })

    raw_sql = response.content.strip()
    # Clean possible markdown formatting
    raw_sql = re.sub(r"^```sql\s*", "", raw_sql, flags=re.IGNORECASE)
    raw_sql = re.sub(r"^```\s*", "", raw_sql)
    raw_sql = re.sub(r"```$", "", raw_sql).strip()
    return raw_sql


@tool
def query_sales_database(query_or_question: str) -> str:
    """
    Executes a safe read-only SQL query or natural language question on the sales_data.db SQLite database.
    Contains 5 relational tables:
    - regions (region_id, region_name, country, manager, headquarters)
    - customers (customer_id, company_name, industry, region_id, tier, joined_date, credit_limit)
    - products (product_id, product_name, category, unit_price, unit_cost, billing_cycle)
    - orders (order_id, customer_id, order_date, status, payment_method, total_amount)
    - order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct, line_total)

    Returns both the executed SQL query and the resulting markdown data table.
    """
    db = get_database()
    
    # Determine if input is raw SQL or natural language question
    clean_input = query_or_question.strip()
    sql_command_keywords = ("SELECT", "WITH", "EXPLAIN", "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE", "REPLACE", "PRAGMA")
    
    if clean_input.upper().startswith(sql_command_keywords):
        sql_query = clean_input
    else:
        try:
            sql_query = generate_sql_from_question(clean_input, db=db)
        except Exception as e:
            return f"Error translating question to SQL: {str(e)}"

    # Execute safely in read-only mode
    try:
        result = db.execute_query(sql_query)
        if not result["success"]:
            return f"**SQL Execution Error**:\nQuery: `{sql_query}`\nError: {result.get('error', 'Unknown')}"

        output = [
            f"**Generated SQL Query**:\n```sql\n{result['sql_query']}\n```",
            f"**Result Table ({result['row_count']} rows)**:\n{result['markdown_table']}"
        ]
        return "\n\n".join(output)

    except PermissionError as pe:
        return f"🚨 **Security Guardrail Violation**: {str(pe)}"
    except Exception as ex:
        return f"**Database Error**: {str(ex)}"


if __name__ == "__main__":
    test_sql = """
    SELECT c.company_name, c.industry, COUNT(o.order_id) AS total_orders, SUM(o.total_amount) AS total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
    ORDER BY total_spent DESC
    LIMIT 5;
    """
    print("[*] Testing SQL Tool with Direct SQL Query:")
    print(query_sales_database.invoke({"query_or_question": test_sql}))
