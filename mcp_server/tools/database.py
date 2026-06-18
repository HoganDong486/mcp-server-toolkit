import sqlite3
import os
import json


def _connect(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def db_query(args: dict) -> dict:
    db_path = args.get("database", os.environ.get("MCP_DEFAULT_DB", ":memory:"))
    sql = args["query"]
    conn = _connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("PRAGMA"):
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return {"content": json.dumps(rows, indent=2, default=str)}
        else:
            conn.commit()
            return {"content": f"Query executed. Rows affected: {cursor.rowcount}"}
    finally:
        conn.close()


def db_list_tables(args: dict) -> dict:
    db_path = args.get("database", os.environ.get("MCP_DEFAULT_DB", ":memory:"))
    conn = _connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        return {"content": "\n".join(tables) if tables else "(no tables)"}
    finally:
        conn.close()


def db_schema(args: dict) -> dict:
    db_path = args.get("database", os.environ.get("MCP_DEFAULT_DB", ":memory:"))
    table = args.get("table")
    conn = _connect(db_path)
    try:
        if table:
            cursor = conn.cursor()
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,))
            row = cursor.fetchone()
            return {"content": row[0] if row else f"Table '{table}' not found"}
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            schemas = [row[0] for row in cursor.fetchall() if row[0]]
            return {"content": "\n\n".join(schemas) if schemas else "(no tables with schema)"}
    finally:
        conn.close()


DB_TOOLS = {
    "db_query": {
        "description": "Execute a SQL query on a SQLite database (SELECT writes JSON rows, DML returns row count)",
        "schema": {
            "type": "object",
            "properties": {
                "database": {"type": "string", "description": "Path to SQLite database file"},
                "query": {"type": "string", "description": "SQL query to execute"},
            },
            "required": ["query"],
        },
        "handler": db_query,
    },
    "db_list_tables": {
        "description": "List all tables in a SQLite database",
        "schema": {
            "type": "object",
            "properties": {"database": {"type": "string", "description": "Path to SQLite database file"}},
        },
        "handler": db_list_tables,
    },
    "db_schema": {
        "description": "Show schema for all tables or a specific table",
        "schema": {
            "type": "object",
            "properties": {
                "database": {"type": "string", "description": "Path to SQLite database file"},
                "table": {"type": "string", "description": "Specific table name (optional)"},
            },
        },
        "handler": db_schema,
    },
}
