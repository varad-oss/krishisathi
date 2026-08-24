import re

with open("frontend/src/app/dashboard/page.tsx", "r") as f:
    text = f.read()

# Replace formatNumber(stats.total_diagnoses) -> formatNumber(stats.total_diagnoses, language)
text = re.sub(r'formatNumber\(([^)]+)\)', r'formatNumber(\1, language)', text)
# Ensure we didn't do formatNumber(x, language, language)
text = text.replace(', language, language)', ', language)')

# Do the same for formatDate if it's used
text = re.sub(r'formatDate\(([^)]+)\)', r'formatDate(\1, language)', text)
text = text.replace(', language, language)', ', language)')

with open("frontend/src/app/dashboard/page.tsx", "w") as f:
    f.write(text)
