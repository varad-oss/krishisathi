import re

with open("backend/routers/diagnose.py", "r") as f:
    content = f.read()

# Add a check for file size and content type
content = content.replace(
    "contents = await file.read()",
    "if file.content_type not in ['image/jpeg', 'image/png', 'image/webp']:\n            raise HTTPException(status_code=415, detail='Unsupported media type')\n        contents = await file.read()\n        if len(contents) > 5 * 1024 * 1024:\n            raise HTTPException(status_code=413, detail='Image too large (max 5MB)')"
)

with open("backend/routers/diagnose.py", "w") as f:
    f.write(content)
