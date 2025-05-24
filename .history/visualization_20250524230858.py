import sqlite3
import streamlit as st
import streamlit_mermaid

def generate_mermaid_er(conn):
    cursor = conn.cursor()
    
    # Get tables excluding SQLite internal tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    mermaid_lines = ["erDiagram"]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        cols = cursor.fetchall()  # (cid, name, type, notnull, dflt_value, pk)
        
        mermaid_lines.append(f"  {table} {{")
        col_dict = {}
        for col in cols:
            col_name = col[1]
            col_type = col[2].upper()
            is_pk = col[5]
            pk_text = " PK" if is_pk else ""
            mermaid_lines.append(f"    {col_type} {col_name}{pk_text}")
            col_dict[col_name] = is_pk
        mermaid_lines.append("  }")

        # Store PK info per table to check relationship types
        table_pk_info = col_dict

        # Fetch foreign key relationships
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fkeys = cursor.fetchall()  # (id, seq, table, from, to, on_update, on_delete, match)

        for fk in fkeys:
            from_col = fk[3]
            ref_table = fk[2]
            ref_col = fk[4]

            if table_pk_info.get(from_col, 0) == 1:
                # FK column is also PK → 1:1 relationship
                mermaid_lines.append(f"  {table} ||--|| {ref_table} : \"{from_col} → {ref_col}\"")
            else:
                # Standard 1:M relationship
                mermaid_lines.append(f"  {table} }|--|| {ref_table} : \"{from_col} → {ref_col}\"")

    return "\n".join(mermaid_lines)
