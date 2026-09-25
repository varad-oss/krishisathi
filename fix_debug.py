import re

with open("backend/routers/debug.py", "r") as f:
    content = f.read()

replacement = """    return {
        "earth_engine_library_installed": EE_AVAILABLE,
        "earth_engine_authenticated": getattr(earth_engine_service, 'initialized', False),
        "pipeline_mode": "LIVE" if getattr(earth_engine_service, 'initialized', False) else "UNAVAILABLE",
        "note": "Requires ee.Initialize() with valid credentials to return LIVE mode."
    }"""

content = re.sub(r'    return \{\n.*?"note": "For noncommercial / research use.*?\n    \}', replacement, content, flags=re.DOTALL)

with open("backend/routers/debug.py", "w") as f:
    f.write(content)
