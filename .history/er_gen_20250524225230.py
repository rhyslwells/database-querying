from eralchemy import render_er

def test_generate_er_diagram(db_path, output_path="er_diagram.png"):
    try:
        render_er(f"sqlite:///{db_path}", output_path)
        print(f"ER diagram generated and saved as {output_path}")
    except Exception as e:
        print("Failed to generate ER diagram:")
        print(e)

if __name__ == "__main__":
    test_generate_er_diagram("my_database.db")
