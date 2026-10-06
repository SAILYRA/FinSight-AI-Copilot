"""
FinSight AI - Safe Read-Only Database Connector & Schema Introspector (Day 3)
Connects to SQLite in strict read-only mode (?mode=ro) with AST/keyword guardrails.
"""

import os
import sqlite3
import re
from typing import Dict, Any, List, Tuple
import pandas as pd
from src.config import settings

# Disallowed mutating SQL operations
MUTATING_KEYWORDS = [
    r"\bDROP\b", r"\bDELETE\b", r"\bINSERT\b", r"\bUPDATE\b",
    r"\bALTER\b", r"\bTRUNCATE\b", r"\bCREATE\b", r"\bREPLACE\b",
    r"\bATTACH\b", r"\bDETACH\b", r"\bPRAGMA\b", r"\bVACUUM\b"
]


class SafeSQLiteDatabase:
    """
    Production Safe SQLite Connector enforcing read-only URI mode and keyword safety guardrails.
    """
    def __init__(self, db_path: str = None):
        self.db_path = os.path.abspath(db_path or settings.DATABASE_PATH)
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found at: {self.db_path}")
        self.readonly_uri = f"file:{self.db_path}?mode=ro"

    def get_connection(self) -> sqlite3.Connection:
        """Opens a connection in strict read-only URI mode."""
        conn = sqlite3.connect(self.readonly_uri, uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def validate_query(self, sql_query: str) -> None:
        """
        Validates that a SQL query contains ONLY read operations (SELECT, WITH, EXPLAIN).
        Raises PermissionError if mutating statements are detected.
        """
        clean_sql = sql_query.strip()
        
        # Remove comments and normalize whitespace
        clean_sql = re.sub(r"--.*$", "", clean_sql, flags=re.MULTILINE)
        clean_sql = re.sub(r"/\*.*?\*/", "", clean_sql, flags=re.DOTALL).strip()

        # Check for empty query
        if not clean_sql:
            raise ValueError("SQL query cannot be empty.")

        # Ensure query begins with SELECT, WITH, or EXPLAIN
        first_word = clean_sql.split()[0].upper()
        if first_word not in ("SELECT", "WITH", "EXPLAIN"):
            raise PermissionError(
                f"Security Violation: Query must start with SELECT or WITH. Attempted action: '{first_word}'."
            )

        # Check for mutating keywords anywhere in query
        for pattern in MUTATING_KEYWORDS:
            if re.search(pattern, clean_sql, flags=re.IGNORECASE):
                matched = re.search(pattern, clean_sql, flags=re.IGNORECASE).group(0)
                raise PermissionError(
                    f"Security Violation: Modifying operations like '{matched.upper()}' are strictly prohibited on sales_data.db."
                )

    def execute_query(self, sql_query: str, max_rows: int = 50) -> Dict[str, Any]:
        """
        Validates and executes a SQL query in read-only mode.
        Returns the raw query, columns, rows, and formatted markdown table.
        """
        self.validate_query(sql_query)
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            
            # Fetch column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            raw_rows = cursor.fetchmany(max_rows)
            
            # Convert to list of dicts & dataframe for clean markdown formatting
            rows = [dict(zip(columns, row)) for row in raw_rows]
            
            if rows:
                try:
                    df = pd.DataFrame(rows)
                    markdown_table = df.to_markdown(index=False)
                except Exception:
                    # Fallback pure-python markdown formatter
                    header = "| " + " | ".join(str(c) for c in columns) + " |"
                    separator = "| " + " | ".join("---" for _ in columns) + " |"
                    data_lines = [
                        "| " + " | ".join(str(r.get(c, "")) for c in columns) + " |"
                        for r in rows
                    ]
                    markdown_table = "\n".join([header, separator] + data_lines)
            else:
                markdown_table = "*(0 rows returned)*"

            return {
                "success": True,
                "sql_query": sql_query.strip(),
                "columns": columns,
                "row_count": len(rows),
                "rows": rows,
                "markdown_table": markdown_table
            }
        except Exception as e:
            return {
                "success": False,
                "sql_query": sql_query.strip(),
                "error": str(e),
                "columns": [],
                "row_count": 0,
                "rows": [],
                "markdown_table": f"**Query Execution Error**: {str(e)}"
            }
        finally:
            conn.close()

    def get_schema_context(self) -> str:
        """
        Dynamically extracts table schemas (CREATE TABLE) and 3 sample rows
        for few-shot prompt injection into the LLM.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get list of user tables
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        schema_parts = []
        schema_parts.append("=== SALES DATABASE SCHEMA & SAMPLE DATA ===")
        
        for table_row in tables:
            t_name = table_row["name"]
            create_sql = table_row["sql"]
            schema_parts.append(f"\nTable: {t_name}")
            schema_parts.append(f"Definition:\n{create_sql.strip()}")
            
            # Fetch 3 sample rows
            sample_cursor = conn.cursor()
            sample_cursor.execute(f"SELECT * FROM {t_name} LIMIT 3;")
            sample_cols = [d[0] for d in sample_cursor.description]
            sample_rows = sample_cursor.fetchall()
            
            if sample_rows:
                sample_data = [dict(zip(sample_cols, r)) for r in sample_rows]
                try:
                    df_sample = pd.DataFrame(sample_data)
                    schema_parts.append(f"3 Sample Rows:\n{df_sample.to_markdown(index=False)}")
                except Exception:
                    header = "| " + " | ".join(str(c) for c in sample_cols) + " |"
                    separator = "| " + " | ".join("---" for _ in sample_cols) + " |"
                    data_lines = [
                        "| " + " | ".join(str(r.get(c, "")) for c in sample_cols) + " |"
                        for r in sample_data
                    ]
                    schema_parts.append(f"3 Sample Rows:\n" + "\n".join([header, separator] + data_lines))
                
        conn.close()
        return "\n".join(schema_parts)


# Singleton instance
_db_instance = None

def get_database() -> SafeSQLiteDatabase:
    global _db_instance
    if _db_instance is None:
        _db_instance = SafeSQLiteDatabase()
    return _db_instance


if __name__ == "__main__":
    db = get_database()
    print("[*] Testing Database Schema Introspection:\n")
    print(db.get_schema_context())
    
    print("\n[*] Testing Safe SELECT Query:")
    res = db.execute_query("SELECT region_name, manager, country FROM regions;")
    print(res["markdown_table"])
    
    print("\n[*] Testing Safety Guardrail on DELETE statement:")
    try:
        db.execute_query("DELETE FROM customers WHERE customer_id = 101;")
    except PermissionError as pe:
        print(f"   ✓ Successfully blocked: {pe}")
