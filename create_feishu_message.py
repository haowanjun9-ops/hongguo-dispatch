#!/usr/bin/env python3
import json

# Read summary data
with open('/tmp/video_summary.json', 'r') as f:
    summary = json.load(f)

# Build markdown message
date = summary['date']
timestamp = summary['timestamp']
total_count = summary['total_count']
editors = summary['editors']

# Create message
message_lines = [
    "## 【每日统计】自产视频后期素材上传+审核状态",
    f"统计时间：{timestamp}",
    f"日期：{date}",
    "",
    "| 后期 | 上传数量 | 持续计费中 | 审核未通过 | 其他 |",
    "|------|---------|-----------|------------|------|"
]

# Add editor rows
for editor_data in editors:
    editor_name = editor_data['后期']
    count = editor_data['上传数量']
    status_billing = editor_data.get('持续计费中', 0)
    status_failed = editor_data.get('审核未通过', 0)
    status_other = editor_data.get('其他', 0)
    
    message_lines.append(f"| {editor_name} | {count} | {status_billing} | {status_failed} | {status_other} |")

# Add total row
message_lines.append(f"合计：{total_count}条素材")

# Join message
message = '\n'.join(message_lines)

print(message)
print("\n" + "="*50)

# Write message to file for sending
with open('/tmp/feishu_message.md', 'w') as f:
    f.write(message)

print("消息已保存到 /tmp/feishu_message.md")