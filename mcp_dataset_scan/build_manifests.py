import json, re, os

with open('parsed35.json', encoding='utf-8') as f:
    items = json.load(f)

os.makedirs('manifests', exist_ok=True)

def strip_json_comments(s):
    s = re.sub(r'//.*', '', s)
    return s

def try_extract_server_block(jsontext):
    jsontext = strip_json_comments(jsontext)
    try:
        obj = json.loads(jsontext)
    except Exception:
        return None
    # find mcpServers dict
    servers = obj.get('mcpServers') or obj.get('servers')
    if isinstance(servers, dict) and servers:
        # take first entry
        name, cfg = next(iter(servers.items()))
        if isinstance(cfg, dict) and 'command' in cfg:
            return name, cfg
    if 'command' in obj:
        return 'server', obj
    return None

def find_json_blocks(text):
    return re.findall(r'```(?:json)?\s*\n(.*?)```', text, re.DOTALL)

manifests_meta = []
for it in items:
    slug = it['url'].replace('https://github.com/', '').replace('/', '_')
    server_name = it['name'].split('/')[-1]
    cfg = None
    source = None
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
        # fallback: tokenize the install command from the awesome-list one-liner
        cmd = it['installs'][0]
        # strip trailing junk like "&& coldstart init" -- take first command only
        cmd = cmd.split('&&')[0].strip()
        parts = cmd.split()
        cfg = {'command': parts[0], 'args': parts[1:]}
        source = 'awesome_list_install_oneliner'

    manifest = {
        'name': f"community-{slug}",
        "mcpServers": {
            server_name: cfg
        }
    }
    fn = f"manifests/{slug}.json"
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    manifests_meta.append({
        'name': it['name'], 'url': it['url'], 'category': it['category'],
        'manifest_file': fn, 'config_source': source, 'server_config': cfg,
    })

with open('manifests_meta.json', 'w', encoding='utf-8') as f:
    json.dump(manifests_meta, f, indent=2)

src_counts = {}
for m in manifests_meta:
    src_counts[m['config_source']] = src_counts.get(m['config_source'], 0) + 1
print(src_counts)
