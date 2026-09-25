from sqlalchemy import text

with open("backend/models/schema.py", "r") as f:
    content = f.read()

import re

# Add text to imports if not there
if "from sqlalchemy import" in content and "text" not in content:
    content = content.replace("from sqlalchemy import Column, ", "from sqlalchemy import Column, text, ")

# Add __table_args__
table_args = """    __table_args__ = (
        Index(
            "uq_active_outbreak",
            "disease",
            "grid_id",
            unique=True,
            sqlite_where=text("status = 'active'"),
            postgresql_where=text("status = 'active'")
        ),
    )"""

content = re.sub(r"    __table_args__ = \([\s\S]+?,\n    \)", table_args, content)

with open("backend/models/schema.py", "w") as f:
    f.write(content)

