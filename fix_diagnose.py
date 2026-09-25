import re

with open("backend/routers/diagnose.py", "r") as f:
    content = f.read()

replacement = """        contents = bytearray()
        max_size = 5 * 1024 * 1024
        while chunk := await file.read(1024 * 1024):
            contents.extend(chunk)
            if len(contents) > max_size:
                raise HTTPException(status_code=413, detail='Image too large (max 5MB)')
        contents = bytes(contents)"""

content = re.sub(
    r'        contents = await file\.read\(\)\n        if len\(contents\) > 5 \* 1024 \* 1024:\n            raise HTTPException\(status_code=413, detail=\'Image too large \(max 5MB\)\'\)',
    replacement,
    content
)

with open("backend/routers/diagnose.py", "w") as f:
    f.write(content)
