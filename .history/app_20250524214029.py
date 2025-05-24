import streamlit as st
import sqlite3
import pandas as pd

st.title("SQLite Query Interface")

# Connect to SQLite database (adjust the path as needed)
conn = sqlite3.connect('my_database.db')

# Text area for SQL query input with default query
query = st.text_area("Enter your SQL query:", "SELECT * FROM my_table LIMIT 10")

if st.button("Run Query"):
    try:
        # Run the query and load results into a DataFrame
        df = pd.read_sql_query(query, conn)
        
        # Show query results
        st.dataframe(df)
        
        st.success(f"Query executed successfully, {len(df)} rows returned.")
    except Exception as e:
        st.error(f"Error executing query: {e}")

# Close the connection on app exit
# (Optional since app usually runs persistently)
# conn.close()
