#!/usr/bin/env python3
import json, re, sys

log_file = "/tmp/browser-use/evaluate_script-2026-08-15T08-29-07-327.log"
with open(log_file, 'r') as f:
    content = f.read()

m = re.search(r'Result: "(.*)"', content, re.DOTALL)
if not m:
    print("No match")
    sys.exit(1)

raw = m.group(1)
data = json.loads('"' + raw + '"')

# Remove PAGE headers and filter rows
lines = data.split('\n')
clean_lines = []
for line in lines:
    line = line.strip()
    if not line:
        continue
    if line.startswith('--- PAGE'):
        continue
    clean_lines.append(line)

output_path = "/workspace/star_report_snapshot.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(clean_lines))

print(f"Total lines: {len(clean_lines)}")
# Show sample
for l in clean_lines[:3]:
    print(l[:200])
