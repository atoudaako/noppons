"""render.py が出力した hits.json(口パクのタイミング)を index.html に埋め込み直す。"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
page = os.path.join(HERE, '..', '..', 'index.html')
hits = json.load(open(os.path.join(HERE, 'hits.json')))
html = open(page, encoding='utf-8').read()
new, n = re.subn(r'const HITS_RAW=\{.*?\};', 'const HITS_RAW=' + json.dumps(hits, separators=(',', ':')) + ';', html, count=1, flags=re.S)
assert n == 1, 'index.html に const HITS_RAW が見つかりません'
open(page, 'w', encoding='utf-8').write(new)
print('index.html の口パクタイミングを更新しました')
