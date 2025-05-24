import sqlite3
import streamlit as st
# from streamlit_mermaid import mermaid

def generate_mermaid_er(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    mermaid_lines = ["erDiagram"]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        cols = cursor.fetchall()
        mermaid_lines.append(f"    {table} {{")
        for col in cols:
            col_name = col[1]
            col_type = col[2]
            pk = "PK" if col[5] else ""
            mermaid_lines.append(f"        {col_type} {col_name} {pk}".strip())
        mermaid_lines.append("    }")

    for table in tables:
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fkeys = cursor.fetchall()
        for fk in fkeys:
            ref_table = fk[2]
            mermaid_lines.append(f"    {table} }}|..|{{{{ {ref_table} : \"fk\"")

    return "\n".join(mermaid_lines)


