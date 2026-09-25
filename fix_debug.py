with open("backend/routers/debug.py", "r") as f:
    content = f.read()

content = content.replace("from fastapi import APIRouter", "from fastapi import APIRouter, Depends\nfrom core.security import require_system_role")
content = content.replace("@router.get(\"/earth-engine-status\")", "@router.get(\"/earth-engine-status\", dependencies=[Depends(require_system_role)])")

with open("backend/routers/debug.py", "w") as f:
    f.write(content)
