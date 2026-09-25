import re

with open("frontend/src/lib/api.ts", "r") as f:
    c = f.read()

c = c.replace(
    "return data.regions.map((region: any) => ({",
    "// eslint-disable-next-line @typescript-eslint/no-explicit-any\n      return data.regions.map((region: any) => ({"
)

with open("frontend/src/lib/api.ts", "w") as f:
    f.write(c)
