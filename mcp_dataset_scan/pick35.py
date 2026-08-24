import json
with open('selected.json', encoding='utf-8') as f:
    sel = json.load(f)
# trim to 35, keep category diversity - already capped reasonably; just cut some categories a bit more
trim_caps = {
    "Developer Tools": 6, "Knowledge & Memory": 6, "Security": 6,
    "Search & Data Extraction": 4, "Communication": 4, "Monitoring": 3,
    "Cloud Platforms": 3, "File Systems": 3, "Command Line": 2,
    "Databases": 3, "Browser Automation": 2, "Code Execution": 1,
}
by_cat = {}
for c in sel:
    by_cat.setdefault(c['category'], []).append(c)
out = []
for cat, items in by_cat.items():
    out.extend(items[:trim_caps.get(cat,3)])
print(len(out))
with open('final35.json','w',encoding='utf-8') as f:
    json.dump(out, f, indent=2)
