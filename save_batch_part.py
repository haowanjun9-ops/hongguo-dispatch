#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import os

raw = sys.stdin.read()
start = raw.find('===BATCHPART_START===')
end = raw.find('===BATCHPART_END===')
out_name = sys.argv[1] if len(sys.argv) > 1 else 'raw_pages_part.json'
if start == -1 or end == -1:
    print("ERROR: markers not found")
    sys.exit(1)

json_str = raw[start + len('===BATCHPART_START==='):end]
try:
    result = json.loads(json_str)
except Exception as e:
    print(f"ERROR parsing part JSON: {e}")
    print("First 200 chars of json_str:", json_str[:200])
    sys.exit(1)

pages = []
for i, p in enumerate(result.get('pages', [])):
    if isinstance(p, str):
        try:
            pages.append(json.loads(p))
        except Exception as e:
            print(f"WARNING: page {i} parse error: {e}, first 100 chars: {p[:100]}")
    else:
        pages.append(p)

total_rows = sum(len(p.get('rows', [])) for p in pages)
page_nums = [p.get('page', 0) for p in pages]
print(f"Part parsed: {len(pages)} pages, {total_rows} rows")
print(f"Page numbers: {page_nums}")

out_path = os.path.join('/workspace', out_name)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(pages, f, ensure_ascii=False, indent=2)
print(f"Saved to {out_path}")
