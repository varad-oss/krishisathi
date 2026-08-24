with open("frontend/src/app/dashboard/page.tsx", "r") as f:
    text = f.read()

text = text.replace("{stats.active_outbreaks}", "{formatNumber(stats.active_outbreaks, language)}")
text = text.replace("{stats.languages_served}", "{formatNumber(stats.languages_served, language)}")
text = text.replace("{s.active_alerts} {t('Alerts', language)}", "{formatNumber(s.active_alerts, language)} {t('Alerts', language)}")

with open("frontend/src/app/dashboard/page.tsx", "w") as f:
    f.write(text)
