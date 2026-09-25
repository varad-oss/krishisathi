import re
with open("frontend/src/lib/api.ts", "r") as f:
    content = f.read()

def replace_error(match):
    prefix = match.group(1)
    return prefix + """
      let errMsg = 'Service is temporarily unavailable.';
      if (response.status === 429) errMsg = 'Too many requests. Please slow down.';
      if (response.status === 413) errMsg = 'Payload too large.';
      if (response.status === 401 || response.status === 403) errMsg = 'Access denied.';
      throw new ApiError(errMsg, response.status);
    }
"""

content = re.sub(r'(if \(!response\.ok\) \{\s*if \(IS_DEMO_MODE\) return [^;]+;)\s*throw new ApiError\([^\)]+\);\s*\}', replace_error, content)

with open("frontend/src/lib/api.ts", "w") as f:
    f.write(content)
