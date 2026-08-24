import json, random

with open('candidates.json', encoding='utf-8') as f:
    candidates = json.load(f)

by_cat = {}
for c in candidates:
    by_cat.setdefault(c['category'], []).append(c)

# cap per category to keep diversity, proportional-ish
caps = {
    "Developer Tools": 8,
    "Knowledge & Memory": 8,
    "Security": 7,
    "Search & Data Extraction": 6,
    "Communication": 5,
    "Monitoring": 4,
    "Cloud Platforms": 4,
    "File Systems": 4,
    "Command Line": 3,
    "Databases": 3,
    "Browser Automation": 2,
    "Code Execution": 1,
}

selected = []
for cat, items in by_cat.items():
    cap = caps.get(cat, 3)
    selected.extend(items[:cap])

print("Selected:", len(selected))
with open('selected.json', 'w', encoding='utf-8') as f:
    json.dump(selected, f, indent=2)
for s in selected:
    print(s['category'], '|', s['name'], '|', s['installs'])
