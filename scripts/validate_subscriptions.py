import json
from pathlib import Path
from urllib.parse import urlparse, unquote
ROOT = Path(__file__).resolve().parents[1]
lists = []
for filename in ('LiangYou-Original-Icons.json', 'LiangYou-Emby-Icons.json'):
    data = json.loads((ROOT / filename).read_text(encoding='utf-8'))
    icons = data['icons']
    assert isinstance(icons, list) and len(icons) >= 5, filename
    for icon in icons:
        assert isinstance(icon.get('name'), str) and icon['name'].strip(), filename
        url = urlparse(icon['url'])
        assert url.scheme == 'https' and url.netloc, icon['name']
        prefix = '/MaddestAlistar/LiangYou-IconLibrary/main/'
        if url.netloc == 'raw.githubusercontent.com' and url.path.startswith(prefix):
            local = (ROOT / unquote(url.path[len(prefix):])).resolve()
            assert local.is_relative_to(ROOT) and local.is_file(), str(local)
    lists.append(icons)
    print(f'{filename}: valid JSON, {len(icons)} entries, local images exist')
assert lists[0][:5] == lists[1][:5], 'Pinned five icons differ'
full = {(x['name'], x['url']) for x in lists[1]}
assert all((x['name'], x['url']) in full for x in lists[0]), 'Original entry missing from full catalog'
print('PASS: both subscriptions agree; pinned icons preserved')
