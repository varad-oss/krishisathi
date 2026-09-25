with open("backend/tests/test_security.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "test_valid_audio_webm" in line:
        lines[i+2] = '    res = client.post("/api/advisory/voice", json={"audio_base64": base64.b64encode(bytes([0x1A, 0x45, 0xdf, 0xa3, 0x61, 0x62, 0x63])).decode(), "latitude": 0, "longitude": 0, "language": "en"})\n'
        break

with open("backend/tests/test_security.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
