import re

# dashboard page
with open("frontend/src/app/dashboard/page.tsx", "r") as f:
    dash = f.read()

dash = dash.replace("{s.name}", "{t(s.name, language)}")
dash = dash.replace("{s.top_crop}", "{t(s.top_crop, language)}")
dash = dash.replace("{s.active_alerts} Alerts", "{s.active_alerts} {t('Alerts', language)}")

# Fix severity in signals
dash = dash.replace("{sig.severity?.toUpperCase() || 'INFO'}", "{t(sig.severity?.toUpperCase() || 'INFO', language)}")
dash = dash.replace("toLocaleString('en-IN')", "toLocaleString(`${language}-IN`)")

# Add the missing translation for "No active cross-state signals."
dash = dash.replace("No active cross-state signals.", "{t('No active cross-state signals.', language)}")

# Wait, in the graph, XAxis is:
# data={filteredHealth.map(h => ({...h, region: t(h.region, language)}))}
# I already did this! Wait, the screenshot shows the graph with English labels!
# If I look at media_1787572136467.png (3rd image), the graph shows "Punjab", "Maharashtra", etc.
# Did I successfully apply the map change? Let me check line 282.

with open("frontend/src/app/dashboard/page.tsx", "w") as f:
    f.write(dash)

