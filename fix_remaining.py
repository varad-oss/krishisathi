import re

def fix_file(filepath, replacements):
    with open(filepath, "r") as f:
        content = f.read()
    for old, new in replacements.items():
        content = content.replace(old, new)
    with open(filepath, "w") as f:
        f.write(content)

# Map page fixes
map_fixes = {
    "{data.region}": "{t(data.region, language)}",
    "{data.health_status}": "{t(data.health_status, language)}",
    "Risk: {data.drought_risk}": "{t('Risk:', language)} {t(data.drought_risk, language)}",
    "{data.primary_crop}": "{t(data.primary_crop, language)}"
}
fix_file("frontend/src/app/map/page.tsx", map_fixes)

# Chat page fixes
chat_fixes = {
    # Fix initial message in chat/page.tsx
    # We want to replace `{msg.content}` with `{msg.role === 'assistant' && msg.id === '1' ? t(msg.content, language) : msg.content}` for the user message, or rather the assistant message.
    # Actually, let's just do `t(msg.content, language)` in the ReactMarkdown for assistant messages since t() returns the original string if not found in the dictionary, which is safe for Gemini responses!
    # Wait, earlier I saw ReactMarkdown had `{msg.content}`. Let's make sure it's `{t(msg.content, language)}`.
}
with open("frontend/src/app/chat/page.tsx", "r") as f:
    chat_content = f.read()
chat_content = chat_content.replace("<ReactMarkdown remarkPlugins={[remarkGfm]}>\n                      {msg.content}\n                    </ReactMarkdown>", "<ReactMarkdown remarkPlugins={[remarkGfm]}>\n                      {t(msg.content, language)}\n                    </ReactMarkdown>")
chat_content = chat_content.replace("{alert.disease}", "{t(alert.disease, language)}")
chat_content = chat_content.replace("{alert.message}", "{t(alert.message, language)}")
with open("frontend/src/app/chat/page.tsx", "w") as f:
    f.write(chat_content)

# Dashboard page fixes
# "Indian States Network" -> "Indian States Network" is already translated (I hope). But let's check:
# {state.name}
# {state.top_crop}
# x-axis graph names
with open("frontend/src/app/dashboard/page.tsx", "r") as f:
    dash_content = f.read()

# Graph: XAxis dataKey="region"
# We can't translate XAxis directly without mapping the data array first!
dash_content = dash_content.replace("data={filteredHealth}", "data={filteredHealth.map(h => ({...h, region: t(h.region, language)}))}")

dash_content = dash_content.replace("{state.name}", "{t(state.name, language)}")
dash_content = dash_content.replace("{state.top_crop}", "{t(state.top_crop, language)}")
dash_content = dash_content.replace("{sig.severity}", "{t(sig.severity, language)}")
dash_content = dash_content.replace("{sig.message}", "{t(sig.message, language)}")

with open("frontend/src/app/dashboard/page.tsx", "w") as f:
    f.write(dash_content)

