import json, urllib.request, time

with open('batch2_40.json', encoding='utf-8') as f:
    items = json.load(f)

def repo_path(url):
    return url.replace('https://github.com/', '').rstrip('/')

for it in items:
    rp = repo_path(it['url'])
    slug = rp.replace('/', '__')
    fn = f"readmes/{slug}.md"
    ok = False
    for branch in ['main', 'master']:
        for readme in ['README.md', 'readme.md']:
            u = f"https://raw.githubusercontent.com/{rp}/{branch}/{readme}"
            try:
                req = urllib.request.Request(u, headers={'User-Agent': 'curl/8'})
                data = urllib.request.urlopen(req, timeout=10).read()
                if data:
                    with open(fn, 'wb') as out:
                        out.write(data)
                    ok = True
                    break
            except Exception:
                pass
        if ok:
            break
    it['readme_fetched'] = ok
    it['readme_file'] = fn if ok else None
    print(it['url'], ok)
    time.sleep(0.15)

with open('batch2_40.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, indent=2)
