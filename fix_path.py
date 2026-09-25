import os

files = ["backend/tests/test_dashboard_crop_health.py", "backend/tests/test_p02_regression.py"]

for f in files:
    with open(f, "r") as file:
        content = file.read()
    
    if "sys.path.insert" not in content:
        imports = "import sys\nimport os\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n"
        content = imports + content
        with open(f, "w") as file:
            file.write(content)

