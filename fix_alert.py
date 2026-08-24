import re

with open("frontend/src/app/chat/page.tsx", "r") as f:
    chat = f.read()

# I will just replace `{t(alert.message, language)}` with the template
# Wait, let's verify if `alert` has `distance_km` and `location`. Yes, from backend!
replacement = """{t('High risk of', language)} {t(alert.disease, language)} {t('detected', language)} {alert.distance_km}{t('km away in', language)} {t(alert.location, language)}."""

chat = chat.replace("{t(alert.message, language)}", replacement)

with open("frontend/src/app/chat/page.tsx", "w") as f:
    f.write(chat)
