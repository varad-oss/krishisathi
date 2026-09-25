with open("backend/tests/test_p03_outbreaks.py", "r") as f:
    content = f.read()

import re
content = content.replace("@pytest.fixture", "import pytest_asyncio\n@pytest_asyncio.fixture")

with open("backend/tests/test_p03_outbreaks.py", "w") as f:
    f.write(content)

