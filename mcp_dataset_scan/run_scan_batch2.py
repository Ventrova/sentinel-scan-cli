import json, subprocess, os

with open('manifests_meta_batch2.json', encoding='utf-8') as f:
    meta = json.load(f)

os.makedirs('results', exist_ok=True)

for m in meta:
    slug = os.path.basename(m['manifest_file']).replace('.json', '')
    out_json = f"results/{slug}_result.json"
    out_txt = f"results/{slug}_stdout.txt"
    proc = subprocess.run(
        ['python3', '../sentinel_scan.py', 'mcp', '--manifest', m['manifest_file'], '--output', out_json],
        cwd=os.getcwd(), capture_output=True, text=True
    )
    with open(out_txt, 'w', encoding='utf-8') as f:
        f.write(proc.stdout + "\n---STDERR---\n" + proc.stderr)
    print(slug, proc.returncode)
