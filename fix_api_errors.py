import re
with open("frontend/src/lib/api.ts", "r") as f:
    content = f.read()

# Update fetchWithFallback
new_fallback = """
async function fetchWithFallback<T>(url: string, options: RequestInit, fallback: T): Promise<T> {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      if (IS_DEMO_MODE) {
        console.warn(`API call failed: ${url}, using fallback data.`);
        return fallback;
      }
      let errMsg = `Service unavailable: ${response.statusText}`;
      if (response.status === 429) errMsg = "Too many requests. Please slow down.";
      if (response.status === 413) errMsg = "Payload too large.";
      if (response.status === 401 || response.status === 403) errMsg = "Access denied.";
      throw new ApiError(errMsg, response.status);
    }
    return await response.json() as T;
"""
content = re.sub(r'async function fetchWithFallback.*?return await response\.json\(\) as T;', new_fallback.strip(), content, flags=re.DOTALL)

with open("frontend/src/lib/api.ts", "w") as f:
    f.write(content)
