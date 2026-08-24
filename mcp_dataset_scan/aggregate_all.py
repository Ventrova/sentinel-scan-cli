import json, glob, os

TARGET_CLASSES = ["missing_provenance", "unpinned_remote_source", "hardcoded_credential", "overbroad_tool_scope"]

per_server = []
for fn in sorted(glob.glob('results/*_result.json')):
    with open(fn, encoding='utf-8') as f:
        data = json.load(f)
    findings = []
    for item in data.get('results', []):
        cls = item.get('heuristic')
        if cls:
            findings.append(cls)
    per_server.append({'manifest': fn, 'findings': findings, 'num_findings': len(findings)})

n = len(per_server)
hit_counts = {c: 0 for c in TARGET_CLASSES}
all_counts = {}
for s in per_server:
    present = set(s['findings'])
    for c in TARGET_CLASSES:
        if c in present:
            hit_counts[c] += 1
    for f in s['findings']:
        all_counts[f] = all_counts.get(f, 0) + 1

out = {
    'n': n,
    'hit_counts_target_classes': hit_counts,
    'all_heuristic_counts': all_counts,
    'per_server': per_server,
}
with open('aggregate_results_all.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)

print('n =', n)
print(json.dumps(hit_counts, indent=2))
for c in TARGET_CLASSES:
    pct = 100.0 * hit_counts[c] / n if n else 0
    print(f"{c}: {hit_counts[c]}/{n} = {pct:.1f}%")
