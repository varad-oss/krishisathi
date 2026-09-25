with open("backend/core/security.py", "r") as f:
    content = f.read()

content = content.replace(
    'except jwt.PyJWTError as e:\n        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")',
    'except jwt.PyJWTError:\n        raise HTTPException(status_code=401, detail="Invalid token")'
)

with open("backend/core/security.py", "w") as f:
    f.write(content)
