#!/usr/bin/env python3
"""
星广报表数据提取脚本
- 使用 lark-cli 发送飞书消息
"""
import csv
import json
import sys
from datetime import datetime

# 从浏览器提取到的原始数据（分页面）
# 格式：每页是一个扁平的 cells 数组，按11列分组
# headers = ['素材ID（巨量）','标题','星图任务ID','星图任务名称','抖音号昵称','抖音号','视频播放链接','下单账户名称','消耗','产品名称','数据统计日期']

HEADERS = [
    '素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', '抖音号',
    '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期'
]

def parse_cells_to_rows(cells, skip_summary=True):
    """将cells数组按11列解析成行对象，跳过汇总行"""
    rows = []
    start = 11 if skip_summary else 0  # skip first 11 cells (summary row)
    for i in range(start, len(cells), 11):
        chunk = cells[i:i+11]
        if len(chunk) < 11:
            break
        row = {}
        for j, h in enumerate(HEADERS):
            row[h] = chunk[j] if j < len(chunk) else ''
        # 跳过全空行
        if any(row[h] for h in HEADERS if h != '消耗'):
            rows.append(row)
    return rows

def filter_cost_over(rows, threshold=2000):
    """筛选消耗超过阈值的行"""
    result = []
    for r in rows:
        try:
            cost = float(r['消耗'].replace(',', '').strip())
            if cost > threshold:
                r['_消耗数值'] = cost
                result.append(r)
        except (ValueError, TypeError):
            continue
    return result

def save_csv(rows, filepath):
    """保存为CSV文件"""
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for r in rows:
            # 移除内部使用的字段
            clean = {k: v for k, v in r.items() if not k.startswith('_')}
            writer.writerow(clean)

def build_markdown_message(rows, stat_time):
    """构建飞书markdown消息"""
    lines = []
    lines.append('## 【消耗预警】星广报表实时消耗>2000')
    lines.append(f'统计时间：{stat_time}')
    lines.append('')
    lines.append('| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |')
    lines.append('|-----------|------|------|---------|------|')
    for r in rows:
        nickname = r.get('抖音号昵称', '').replace('|', '\\|')
        title = r.get('标题', '').replace('|', '\\|')
        # 标题过长截断
        if len(title) > 50:
            title = title[:50] + '...'
        cost = r.get('消耗', '')
        video_url = r.get('视频播放链接', '').strip('"').strip("'")
        date = r.get('数据统计日期', '')
        link_md = f'[观看]({video_url})' if video_url else ''
        lines.append(f'| {nickname} | {title} | {cost} | {link_md} | {date} |')
    lines.append('')
    lines.append(f'共{len(rows)}条记录消耗超过2000元')
    return '\n'.join(lines)

if __name__ == '__main__':
    # 测试数据（实际数据从浏览器通过stdin注入或参数传入）
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = sys.stdin.read()
    
    if not input_data.strip():
        print('NO_DATA')
        sys.exit(0)
    
    try:
        pages = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(f'JSON_ERROR: {e}')
        sys.exit(1)
    
    all_rows = []
    for page_cells in pages:
        rows = parse_cells_to_rows(page_cells)
        all_rows.extend(rows)
    
    print(f'总记录数（不含汇总）: {len(all_rows)}')
    
    over_2000 = filter_cost_over(all_rows, 2000)
    print(f'消耗>2000的记录数: {len(over_2000)}')
    
    if not over_2000:
        print('NO_OVER_2000')
        sys.exit(0)
    
    # 按消耗降序排序
    over_2000.sort(key=lambda x: x['_消耗数值'], reverse=True)
    
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H-%M')
    stat_time = now.strftime('%Y-%m-%d %H:%M')
    
    csv_path = f'/workspace/star_report_cost_over_2000_{date_str}_{time_str}.csv'
    save_csv(over_2000, csv_path)
    print(f'CSV_PATH: {csv_path}')
    
    md = build_markdown_message(over_2000, stat_time)
    print('MARKDOWN_START')
    print(md)
    print('MARKDOWN_END')
