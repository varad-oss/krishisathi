with open("backend/config.py", "r") as f:
    lines = f.readlines()

out = []
for line in lines:
    if "class Settings(BaseSettings):" in line:
        out.append(line)
        out.append("    ENVIRONMENT: str = \"development\"\n")
        out.append("    TRUST_REVERSE_PROXY: bool = False\n")
    else:
        out.append(line)

with open("backend/config.py", "w") as f:
    f.writelines(out)
