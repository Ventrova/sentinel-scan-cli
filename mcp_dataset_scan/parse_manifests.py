import json, re

with open('final35.json', encoding='utf-8') as f:
    items = json.load(f)

def find_json_configs(text):
    # find fenced json blocks mentioning mcpServers or "command"
    blocks = re.findall(r'```(?:json)?\s*\n(.*?)```', text, re.DOTALL)
    configs = []
    for b in blocks:
        if '"command"' in b or 'mcpServers' in b:
            configs.append(b.strip())
    return configs

def extract_command_args(text, installs):
    # fallback: parse install command like "npx -y pkg" or "uvx pkg"
    cmd = installs[0]
    parts = cmd.split()
    command = parts[0]
    args = parts[1:]
    return command, args

results = []
for it in items:
    fn = it.get('readme_file')
    text = ''
    if fn:
        try:
            with open(fn, encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception:
            text = ''
    configs = find_json_configs(text)
    # look for literal env assignments near "env" blocks in the json configs
    has_full_json_config = len(configs) > 0
    # check for http:// remote url
    has_http_url = bool(re.search(r'"url"\s*:\s*"http://', text))
    # scope/permission wildcard mentions
    wildcard_scope = bool(re.search(r'"(scopes?|permissions?)"\s*:\s*(\[\s*"\*"|"(\*|admin:\*|full_access|all)")', text, re.IGNORECASE))
    command, args = extract_command_args(text, it['installs'])
    results.append({
        **it,
        'has_full_json_config': has_full_json_config,
        'num_json_configs_found': len(configs),
        'has_http_url_in_readme': has_http_url,
        'wildcard_scope_mentioned': wildcard_scope,
        'fallback_command': command,
        'fallback_args': args,
    })

with open('parsed35.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

for r in results:
    print(r['name'], '| json_configs:', r['num_json_configs_found'], '| http_url:', r['has_http_url_in_readme'], '| wildcard:', r['wildcard_scope_mentioned'])
