with open('backend/config.py', 'r') as f:
    content = f.read()

if "JWT_SECRET" not in content:
    content = content.replace(
        "    GEMINI_AGENT_MODEL: str = \"gemini-3.8-flash\"",
        "    GEMINI_AGENT_MODEL: str = \"gemini-3.8-flash\"\n    JWT_SECRET: Optional[str] = None\n    REDIS_URL: Optional[str] = None\n    RATE_LIMIT_GLOBAL: int = 100\n    RATE_LIMIT_AI: int = 10"
    )

with open('backend/config.py', 'w') as f:
    f.write(content)
