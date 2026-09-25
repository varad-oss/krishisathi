with open("backend/tests/test_security.py", "r") as f:
    c = f.read()

import re
c = re.sub(r'b".*?\\xa3abc"', 'b"\\\\x1A\\\\x45\\\\xdf\\\\xa3abc"', c)

with open("backend/tests/test_security.py", "w") as f:
    f.write(c)
