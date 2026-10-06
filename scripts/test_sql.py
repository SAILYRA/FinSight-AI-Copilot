"""
FinSight AI - Interactive SQL & Safety Guardrails Verification Script (Day 3 Hands-on)
Demonstrates schema introspection, complex relational queries, and security enforcement.
"""

import sys
import os

# Set utf-8 encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.sql.database import get_database
from src.sql.sql_tool import query_sales_database


def run_sql_tests():
    print("=" * 75)
    print("🚀 FIN-SIGHT AI — SAFE TEXT-TO-SQL & DATABASE TOOL VERIFICATION (DAY 3)")
    print("=" * 75)

    db = get_database()

    # TEST 1: Database Schema Introspection
    print("\n" + "#" * 75)
    print("TEST 1: 📋 Dynamic Database Schema & Sample Rows Introspection")
    print("#" * 75)
    schema_info = db.get_schema_context()
    print(schema_info[:600] + "\n\n... [Remaining schema truncated for display] ...")

    # TEST 2: Complex Relational Multi-Table Join
    print("\n" + "#" * 75)
    print("TEST 2: 🏆 Top 5 Customers by Total Spend (Customers JOIN Orders)")
    print("#" * 75)
    query_1 = """
    SELECT 
        c.customer_id,
        c.company_name,
        c.industry,
        c.tier,
        COUNT(o.order_id) AS total_orders,
        ROUND(SUM(o.total_amount), 2) AS total_revenue_usd
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status = 'Completed'
    GROUP BY c.customer_id
    ORDER BY total_revenue_usd DESC
    LIMIT 5;
    """
    res1 = query_sales_database.invoke({"query_or_question": query_1})
    print(res1)

    # TEST 3: Product Category Breakdown & Profit Margins
    print("\n" + "#" * 75)
    print("TEST 3: 💰 Product Category Sales & Profitability (Products JOIN Order_Items)")
    print("#" * 75)
    query_2 = """
    SELECT 
        p.category,
        COUNT(DISTINCT p.product_id) AS sku_count,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.line_total), 2) AS gross_sales,
        ROUND(SUM(oi.line_total - (p.unit_cost * oi.quantity)), 2) AS estimated_profit
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.category
    ORDER BY gross_sales DESC;
    """
    res2 = query_sales_database.invoke({"query_or_question": query_2})
    print(res2)

    # TEST 4: Security Guardrail Violations (DROP / DELETE / UPDATE Blocking)
    print("\n" + "#" * 75)
    print("TEST 4: 🛡️ Security Guardrails Verification (Attempting Mutating Operations)")
    print("#" * 75)
    
    malicious_queries = [
        "DROP TABLE customers;",
        "DELETE FROM orders WHERE total_amount > 1000;",
        "UPDATE products SET unit_price = 0.0 WHERE product_id = 201;"
    ]

    for m_query in malicious_queries:
        print(f"\n[Attempting Malicious Query]: {m_query}")
        result = query_sales_database.invoke({"query_or_question": m_query})
        print(f"Result -> {result}")

    print("\n" + "=" * 75)
    print("[SUCCESS] All Day 3 SQL Tool & Security Guardrail tests completed!")
    print("=" * 75)


if __name__ == "__main__":
    run_sql_tests()
