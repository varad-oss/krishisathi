import re

with open("backend/routers/states.py", "r") as f:
    content = f.read()

content = content.replace(
    "from fastapi import APIRouter, HTTPException, Depends",
    "from fastapi import APIRouter, HTTPException, Depends\nfrom core.security import require_system_role, Principal"
)

content = content.replace(
    "async def post_exchange_signal(signal: RegionalAgriSignal):",
    "async def post_exchange_signal(signal: RegionalAgriSignal, principal: Principal = Depends(require_system_role)):"
)

with open("backend/routers/states.py", "w") as f:
    f.write(content)
