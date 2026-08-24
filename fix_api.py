import re

with open("frontend/src/lib/api.ts", "r") as f:
    api = f.read()

# Update getAdvisory signature
api = api.replace(
    "export async function getAdvisory(query: string, latitude: number, longitude: number, cropType?: string, language: string = 'en') {",
    "export async function getAdvisory(query: string, latitude: number, longitude: number, cropType?: string, language: string = 'en', imageBase64?: string) {"
)

# Update payload
new_payload = """
  const payload: any = {
    query,
    latitude,
    longitude,
    language
  };
  if (cropType) payload.crop_type = cropType;
  if (imageBase64) payload.image_base64 = imageBase64;

  const res = await fetch(`${API_BASE}/api/advisory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
"""

api = re.sub(
    r"const res = await fetch\(`\$\{API_BASE\}/api/advisory`, \{\s*method: 'POST',\s*headers: \{ 'Content-Type': 'application/json' \},\s*body: JSON\.stringify\(\{ query, latitude, longitude, crop_type: cropType, language \}\)\s*\}\);",
    new_payload.strip(),
    api
)

with open("frontend/src/lib/api.ts", "w") as f:
    f.write(api)
