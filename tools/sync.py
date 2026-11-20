"""Rebuild this preview site from the live review build.

Usage: python3 -I tools/sync.py <review index.html> <repo root>

1. Reads the instron-review-data JSON from the review build's index.html.
2. Writes every embedded image to assets/img/<first 10 hex of its hash>.<ext>.
3. Runs tools/build.py to regenerate all pages, shared CSS/JS and the live theme.
4. Deletes images, CSS and JS in assets/ that no page refers to any more.
Content is never edited by hand in this repo: change the review site, then sync.
"""
import sys, os, re, json, base64, subprocess, tempfile

src, root = sys.argv[1], os.path.abspath(sys.argv[2])
tools = os.path.dirname(os.path.abspath(__file__))

html = open(src, encoding='utf-8').read()
m = re.search(r'<script[^>]*id="instron-review-data"[^>]*>(.*?)</script>', html, re.S)
if not m:
    sys.exit('No instron-review-data block found - is this the review index.html?')
data = json.loads(m.group(1))

EXT = {'image/webp': 'webp', 'image/png': 'png', 'image/jpeg': 'jpg', 'image/svg+xml': 'svg', 'image/gif': 'gif'}
img_dir = os.path.join(root, 'assets', 'img'); os.makedirs(img_dir, exist_ok=True)
names = {}
for key, uri in data['assets'].items():
    short = key[len('__INSTRON_EMBED_ASSET_'):][:10]
    mime = uri[5:uri.index(';')]
    fn = f'{short}.{EXT[mime]}'
    names[key] = fn
    raw = base64.b64decode(uri.split(',', 1)[1])
    path = os.path.join(img_dir, fn)
    if not os.path.exists(path) or open(path, 'rb').read() != raw:
        open(path, 'wb').write(raw)

with tempfile.TemporaryDirectory() as tmp:
    dj, nj = os.path.join(tmp, 'data.json'), os.path.join(tmp, 'names.json')
    json.dump(data, open(dj, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(names, open(nj, 'w'))
    subprocess.run([sys.executable, '-I', os.path.join(tools, 'build.py'), dj, nj,
                    os.path.join(tools, 'theme.css'), root], check=True)

# prune assets nothing refers to any more
used = set()
for dirpath, _, files in os.walk(root):
    if '.git' in dirpath.split(os.sep):
        continue
    for f in files:
        if f.endswith(('.html', '.css')):
            used.update(re.findall(r'([0-9a-f]{10}\.(?:webp|png|jpg|svg|gif|css)|site-[0-9a-f]{10}\.js)',
                                   open(os.path.join(dirpath, f), encoding='utf-8', errors='ignore').read()))
removed = []
for sub in ('img', 'css', 'js'):
    d = os.path.join(root, 'assets', sub)
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if re.fullmatch(r'[0-9a-f]{10}\.\w+|site-[0-9a-f]{10}\.js', f) and f not in used:
            os.remove(os.path.join(d, f)); removed.append(f'{sub}/{f}')
print(f'{len(data["pages"])} pages, {len(names)} images; removed {len(removed)} unused files: {removed}')
