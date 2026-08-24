import re

with open("frontend/src/app/dashboard/page.tsx", "r") as f:
    dash = f.read()

# Find YAxis and add tickFormatter
dash = dash.replace("<YAxis\n                      axisLine={false}\n                      tickLine={false}\n                      domain={[0, 1]}\n                      tick={{ fontSize: 10, fill: '#9ca3af' }}\n                    />", "<YAxis\n                      axisLine={false}\n                      tickLine={false}\n                      domain={[0, 1]}\n                      tick={{ fontSize: 10, fill: '#9ca3af' }}\n                      tickFormatter={(value) => formatNumber(value, language)}\n                    />")

dash = dash.replace("<YAxis \n                      yAxisId=\"left\"\n                      axisLine={false}\n                      tickLine={false}\n                      tick={{ fontSize: 10, fill: '#9ca3af' }}\n                    />", "<YAxis \n                      yAxisId=\"left\"\n                      axisLine={false}\n                      tickLine={false}\n                      tick={{ fontSize: 10, fill: '#9ca3af' }}\n                      tickFormatter={(value) => formatNumber(value, language)}\n                    />")

with open("frontend/src/app/dashboard/page.tsx", "w") as f:
    f.write(dash)
