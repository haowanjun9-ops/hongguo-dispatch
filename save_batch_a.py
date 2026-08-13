import json
import sys

# 读取stdin数据
raw = sys.stdin.read()
# 提取Batch A JSON
start = raw.find('===BATCH_A_JSON_START===')
end = raw.find('===BATCH_A_JSON_END===')
if start == -1 or end == -1:
    print("ERROR: markers not found")
    sys.exit(1)

json_str = raw[start + len('===BATCH_A_JSON_START==='):end]
# 解析外层数组（字符串数组，每个元素是JSON字符串）
str_arr = json.loads(json_str)
# 解析每个字符串为对象
pages = [json.loads(s) if isinstance(s, str) else s for s in str_arr]
print(f"Parsed {len(pages)} pages")
total_rows = sum(len(p['rows']) for p in pages)
print(f"Total rows in batch A: {total_rows}")

with open('/workspace/raw_pages_batchA.json', 'w', encoding='utf-8') as f:
    json.dump(pages, f, ensure_ascii=False, indent=2)
print("Saved to /workspace/raw_pages_batchA.json")
