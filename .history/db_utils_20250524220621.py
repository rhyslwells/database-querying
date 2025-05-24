import sqlite3
import pandas as pd

def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def execute_schema(conn, schema_sql):
    try:
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        return True
    except Exception as e:
        print(f"Schema execution error: {e}")
        return False

def insert_dataframe(conn, table_name, df):
    try:
        df.to_sql(table_name, conn, if_exists='append', index=False)
        return True
    except Exception as e:
        print(f"Insert error: {e}")
        return False
