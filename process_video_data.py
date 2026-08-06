#!/usr/bin/env python3
import json
import csv
from datetime import datetime
from collections import defaultdict

# Read the extracted data
with open('/tmp/browser-use/evaluate_script-2026-08-06T02-05-22-301.log', 'r') as f:
    content = f.read()
    # Remove the "Result: " prefix
    if content.startswith('Result: '):
        content = content[8:]
    result = json.loads(content)

data = result['data']

# Filter out empty rows
valid_data = [row for row in data if row.get('视频ID') and row['视频ID'].strip()]

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')

# Filter today's uploads
today_data = [row for row in valid_data if row.get('上传时间', '').startswith(today)]

print(f"Total valid rows: {len(valid_data)}")
print(f"Today's uploads: {len(today_data)}")

# Group by 后期 (editor)
editor_stats = defaultdict(lambda: {
    'count': 0,
    'status_count': defaultdict(int)
})

for row in today_data:
    editor = row.get('后期', '').strip()
    if not editor:
        editor = '未知'
    
    editor_stats[editor]['count'] += 1
    
    # Count 星广审核状态
    status = row.get('星广审核状态', '').strip()
    if not status:
        status = '待审核'
    
    editor_stats[editor]['status_count'][status] += 1

# Print summary
print("\n=== 按后期统计 ===")
for editor, stats in sorted(editor_stats.items()):
    print(f"\n{editor}: {stats['count']}条")
    for status, count in stats['status_count'].items():
        print(f"  - {status}: {count}条")

# Save detailed data to CSV
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
csv_file = f'/workspace/self_video_daily_by_editor_{timestamp}.csv'

fieldnames = ['视频ID', '标题', '编导', '后期', '星广审核状态', '上传时间', '素材ID（巨量）', '素材ID（凡创）', 
              '订单ID', '订单名称', '下单账户名称', '任务名称', '抖音号', '抖音昵称', 
              '内部审核状态', '发布状态', '团队来源', '素材来源', '素材分类', '创建人']

with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for row in today_data:
        writer.writerow(row)

print(f"\n详细数据已保存到: {csv_file}")

# Prepare summary data for Feishu message
summary_data = []
all_statuses = set()
for editor, stats in editor_stats.items():
    all_statuses.update(stats['status_count'].keys())

# Sort statuses: prioritize specific statuses
status_priority = ['持续计费中', '审核未通过', '已通过', '待审核']
other_statuses = [s for s in all_statuses if s not in status_priority]
sorted_statuses = status_priority + other_statuses

for editor, stats in sorted(editor_stats.items()):
    row_data = {
        '后期': editor,
        '上传数量': stats['count']
    }
    
    for status in sorted_statuses:
        count = stats['status_count'].get(status, 0)
        if status in status_priority:
            row_data[status] = count
        else:
            row_data['其他'] = row_data.get('其他', 0) + count
    
    # Ensure all priority statuses have values
    for status in status_priority:
        if status not in row_data:
            row_data[status] = 0
    
    if '其他' not in row_data:
        row_data['其他'] = 0
    
    summary_data.append(row_data)

# Save summary as JSON for Feishu message
summary_json = {
    'date': today,
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
    'total_count': len(today_data),
    'editors': summary_data,
    'status_list': ['持续计费中', '审核未通过', '其他']
}

with open('/tmp/video_summary.json', 'w') as f:
    json.dump(summary_json, f, ensure_ascii=False, indent=2)

print(f"\n汇总数据已保存到: /tmp/video_summary.json")
print(f"总计: {len(today_data)}条素材")