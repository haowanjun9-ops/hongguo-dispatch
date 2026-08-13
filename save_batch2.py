#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys

raw = sys.stdin.read()
start = raw.find('===BATCH2_START===')
end = raw.find('===BATCH2_END===')
if start == -1 or end == -1:
    print("ERROR: markers not found")
    sys.exit(1)

json_str = raw[start + len('===BATCH2_START==='):end]
try:
    result = json.loads(json_str)
except Exception as e:
    print(f"ERROR parsing batch2 JSON: {e}")
    print("First 200 chars of json_str:", json_str[:200])
    sys.exit(1)

# pages数组中的元素是字符串，需要再次解析为对象
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
print(f"Batch 2 parsed: {len(pages)} pages, {total_rows} data rows")

page_nums = [p.get('page', 0) for p in pages]
print(f"Page numbers range: min={min(page_nums) if page_nums else 0}, max={max(page_nums) if page_nums else 0}")

with open('/workspace/raw_pages_batch2.json', 'w', encoding='utf-8') as f:
    json.dump(pages, f, ensure_ascii=False, indent=2)
print("Saved to /workspace/raw_pages_batch2.json")
