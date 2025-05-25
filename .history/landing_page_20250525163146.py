import streamlit as st

def app():
    st.title("Welcome to the SQLite Streamlit App")

import streamlit as st

def app():
    st.title("Welcome to the SQLite Streamlit App")

    st.markdown("""
    ### Overview

    This application provides two workflows to interact with SQLite databases entirely within your browser:

    1. **Upload Existing DB**  
       Upload a `.db` SQLite database file and run SQL queries on it instantly, without any setup.

    2. **Build DB from CSV**  
       Create a SQLite database from CSV files and run SQL queries on it.

    --- 

    ### How to Use This App

    1. Select a workflow from the sidebar navigation.  
    2. For **Upload Existing DB**, upload your `.db` file and start querying immediately.  
    3. For **Build DB from CSV**, provide an SQL schema and CSV files to build your database from scratch.  
    4. Use the query editor to explore data or run custom SQL queries.  
    5. Visualize your database structure with the ER diagram button.  
    6. Download the current state of your database anytime.

    ---

    ### Supported Features

    - In-memory SQLite databases for fast, temporary operations.  
    - Schema visualization using Mermaid ER diagrams.  
    - CSV upload with column validation and data insertion.  
    - Interactive SQL query editor with instant feedback.  
    - Database download to save your work externally.

    ---

    ### Important Notes

    - Databases exist only in memory and will be lost when you close or refresh the browser.  
    - File size limits and browser memory constraints apply.  
    - Ensure your schema and CSV files are correctly formatted to avoid errors.  
    - Large datasets may impact performance.

    ---

    ### Use Cases

    - Quickly inspect and query SQLite databases without installing software.  
    - Prototype new database schemas and data loads.  
    - Educational tool for learning SQL and relational database concepts.

    ---

    For detailed documentation and updates, visit the [project repository](https://github.com/yourproject).

    If you encounter issues or have questions, please contact the developer.

    """)

