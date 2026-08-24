import re

with open("frontend/src/app/dashboard/page.tsx", "r") as f:
    dash = f.read()

# Fix the date
dash = dash.replace("{ob.date}", "{formatDate(ob.date, language)}")

# Fix YAxis
# Currently:
#                     <YAxis
#                       axisLine={false}
#                       tickLine={false}
#                       tick={{ fontSize: 12, fill: "#6b7280" }}
#                     />
replacement = """<YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 12, fill: "#6b7280" }}
                      tickFormatter={(value) => formatNumber(value, language)}
                    />"""

dash = re.sub(r'<YAxis\s+axisLine=\{false\}\s+tickLine=\{false\}\s+tick=\{\{\s*fontSize:\s*12,\s*fill:\s*"#6b7280"\s*\}\}\s*/>', replacement, dash, flags=re.MULTILINE)

with open("frontend/src/app/dashboard/page.tsx", "w") as f:
    f.write(dash)

