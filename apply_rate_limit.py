import re

def update_file(path):
    with open(path, "r") as f:
        content = f.read()

    # Add import if missing
    if "from core.rate_limit import ai_rate_limit" not in content:
        content = content.replace(
            "from fastapi import",
            "from core.rate_limit import ai_rate_limit\nfrom fastapi import"
        )
    
    # Add dependency to APIRouter initialization
    if "dependencies=[Depends(ai_rate_limit)]" not in content:
        content = content.replace(
            "APIRouter(",
            "APIRouter(dependencies=[Depends(ai_rate_limit)], "
        )

    with open(path, "w") as f:
        f.write(content)

update_file("backend/routers/diagnose.py")
update_file("backend/routers/advisory.py")
