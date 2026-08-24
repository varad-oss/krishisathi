import re

with open("frontend/src/lib/api.ts", "r") as f:
    api = f.read()

new_get_advisory = """export async function getAdvisory(
  query: string, 
  lat: number, 
  lng: number, 
  cropType: string | undefined,
  language: string,
  imageBase64?: string
): Promise<AdvisoryResponse> {
  try {
    const payload: any = {
      query,
      latitude: lat,
      longitude: lng,
      language
    };
    if (cropType) payload.crop_type = cropType;
    if (imageBase64) payload.image_base64 = imageBase64;
    
    const response = await fetch(`${API_BASE}/api/advisory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) return mockAdvisory;
    const data = await response.json();
    return {
      query: query,
      answer: data.advisory_text || data.answer || 'No advisory available.',
      timestamp: new Date().toISOString(),
    };
  } catch (error) {"""

api = re.sub(
    r'export async function getAdvisory\(\s*query: string,\s*lat: number,\s*lng: number,\s*language: string\s*\): Promise<AdvisoryResponse> \{\s*try \{\s*const response = await fetch\(`\$\{API_BASE\}/api/advisory`, \{\s*method: \'POST\',\s*headers: \{ \'Content-Type\': \'application/json\' \},\s*body: JSON\.stringify\(\{ query, latitude: lat, longitude: lng, language \}\),\s*\}\);\s*if \(!response\.ok\) return mockAdvisory;\s*const data = await response\.json\(\);\s*return \{\s*query: query,\s*answer: data\.advisory_text \|\| data\.answer \|\| \'No advisory available\.\',\s*timestamp: new Date\(\)\.toISOString\(\),\s*\};\s*\} catch \(error\) \{',
    new_get_advisory.strip(),
    api
)

with open("frontend/src/lib/api.ts", "w") as f:
    f.write(api)
