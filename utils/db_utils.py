import sqlite3
import pandas as pd
import traceback

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")  # Enable FK constraints
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def execute_schema(conn, schema_sql):
    try:
        print("Executing schema:\n", schema_sql)
        conn.executescript(schema_sql)
        conn.commit()
        print("Schema executed successfully.")
        return True
    except Exception as e:
        print("Schema execution failed!")
        print(traceback.format_exc())
        return False

def insert_dataframe(conn, table_name, df, if_exists="append"):
    try:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        return True
    except Exception as e:
        print(f"Insert error for table `{table_name}`:")
        print(traceback.format_exc())
        return False
