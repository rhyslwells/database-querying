import eralchemy
from PIL import Image
import os

def render_er_diagram(sqlite_file):
    output_file = "er_diagram.png"
    try:
        eralchemy.render_er(f"sqlite:///{sqlite_file}", output_file)
        if os.path.exists(output_file):
            return Image.open(output_file)
    except Exception as e:
        print(f"ER diagram generation error: {e}")
    return None
