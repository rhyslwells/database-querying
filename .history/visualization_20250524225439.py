import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import streamlit as st

def render_er_diagram(db_file):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Fetch tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]

        G = nx.DiGraph()

        # Add tables as nodes
        for table in tables:
            G.add_node(table)

        # Add edges for foreign keys
        for table in tables:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fkeys = cursor.fetchall()
            for fkey in fkeys:
                # fkey format: (id, seq, table, from, to, on_update, on_delete, match)
                _, _, ref_table, _, _, _, _, _ = fkey
                G.add_edge(table, ref_table)

        # Draw graph
        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=3000, font_size=12, arrowsize=20)

        # Save to BytesIO and return bytes
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return buf

    except Exception as e:
        st.error(f"Error generating ER diagram: {e}")
        return None
