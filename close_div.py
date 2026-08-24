with open("frontend/src/app/chat/page.tsx", "r") as f:
    page = f.read()

page = page.replace("            </button>\n          </form>", "            </button>\n            </div>\n          </form>")

with open("frontend/src/app/chat/page.tsx", "w") as f:
    f.write(page)
