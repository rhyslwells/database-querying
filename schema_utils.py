def get_table_columns(conn, table_name):
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]
    
def generate_schema_from_csv(table_name, df):
    type_map = {
        'int64': 'INTEGER',
        'float64': 'REAL',
        'object': 'TEXT',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TEXT'
    }
    columns = []
    for col, dtype in df.dtypes.items():
        col_type = type_map.get(str(dtype), 'TEXT')
        columns.append(f"{col} {col_type}")
    schema = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n);"
    return schema
