from db_utils import create_connection, execute_schema

schema_path = "sample_daata/schema.sql"
with open(schema_path, "r", encoding="utf-8") as f:
    schema_sql = f.read()

conn = create_connection("test_manual.db")
execute_schema(conn, schema_sql)
