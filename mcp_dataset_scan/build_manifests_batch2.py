import json, re, os

with open('batch2_40.json', encoding='utf-8') as f:
    items = json.load(f)

os.makedirs('manifests', exist_ok=True)

def strip_json_comments(s):
    return re.sub(r'//.*', '', s)

def try_extract_server_block(jsontext):
    jsontext = strip_json_comments(jsontext)
    try:
        obj = json.loads(jsontext)
    except Exception:
        return None
    servers = obj.get('mcpServers') or obj.get('servers')
    if isinstance(servers, dict) and servers:
        name, cfg = next(iter(servers.items()))
        if isinstance(cfg, dict) and 'command' in cfg:
            return name, cfg
    if 'command' in obj:
        return 'server', obj
    return None

def find_json_blocks(text):
    return re.findall(r'```(?:json)?\s*\n(.*?)```', text, re.DOTALL)

manifests_meta = []
skipped = []
for it in items:
    if not it.get('readme_fetched'):
        skipped.append(it['url'])
        continue
    slug = it['url'].replace('https://github.com/', '').replace('/', '_')
    server_name = it['name'].split('/')[-1]
    cfg = None
    source = None
    text = ''
    if it.get('readme_file'):
        try:
            with open(it['readme_file'], encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception:
            text = ''
    for b in find_json_blocks(text):
        if '"command"' in b or 'mcpServers' in b:
            res = try_extract_server_block(b)
            if res:
                server_name, cfg = res
                source = 'published_json_config'
                break
    if cfg is None:
        if not it.get('installs'):
            skipped.append(it['url'])
            continue
        cmd = it['installs'][0]
        cmd = cmd.split('&&')[0].strip()
        parts = cmd.split()
        if not parts:
            skipped.append(it['url'])
            continue
        cfg = {'command': parts[0], 'args': parts[1:]}
        source = 'awesome_list_install_oneliner'

    manifest = {
        'name': f"community-{slug}",
        "mcpServers": {server_name: cfg}
    }
    fn = f"manifests/{slug}.json"
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    manifests_meta.append({
        'name': it['name'], 'url': it['url'], 'category': it['category'],
        'manifest_file': fn, 'config_source': source, 'server_config': cfg,
    })

with open('manifests_meta_batch2.json', 'w', encoding='utf-8') as f:
    json.dump(manifests_meta, f, indent=2)

print("built:", len(manifests_meta), "skipped:", len(skipped), skipped)
src_counts = {}
for m in manifests_meta:
    src_counts[m['config_source']] = src_counts.get(m['config_source'], 0) + 1
print(src_counts)
