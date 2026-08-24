import re, json

with open('awesome-mcp-servers.md', encoding='utf-8') as f:
    lines = f.readlines()

# Map line ranges to category names based on headers found
headers = []
for i, l in enumerate(lines):
    m = re.match(r'^### .*?</a>(.+)$', l.strip())
    if m:
        headers.append((i, m.group(1).strip()))

def category_for(i):
    cat = "Uncategorized"
    for idx, name in headers:
        if idx <= i:
            cat = name
        else:
            break
    return cat

WANTED_CATS = {
    "Databases", "File Systems", "Developer Tools", "Cloud Platforms",
    "Security", "Command Line", "Browser Automation", "Communication",
    "Search & Data Extraction", "Code Execution", "Monitoring", "Knowledge & Memory",
}

entry_re = re.compile(r'^\s*-\s*\[([^\]]+)\]\((https://github\.com/[^)]+)\)')
install_re = re.compile(r'`((?:npx|uvx|pipx?|docker|npm|deno|go install|cargo install|bunx)[^`]{0,140})`')

candidates = []
for i, l in enumerate(lines):
    m = entry_re.match(l)
    if not m:
        continue
    cat = category_for(i)
    if cat not in WANTED_CATS:
        continue
    name, url = m.group(1), m.group(2)
    installs = install_re.findall(l)
    if not installs:
        continue
    candidates.append({"name": name, "url": url, "category": cat, "installs": installs, "line": l.strip()})

print(f"Total candidates with inline install commands: {len(candidates)}")
by_cat = {}
for c in candidates:
    by_cat.setdefault(c['category'], []).append(c)
for cat, items in by_cat.items():
    print(cat, len(items))

with open('candidates.json', 'w', encoding='utf-8') as f:
    json.dump(candidates, f, indent=2)
