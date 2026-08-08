#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
筛选消耗>2000的记录，保存CSV并生成飞书消息内容
"""
import json
import csv
from datetime import datetime

# 读取分页数据文件
PAGE_DATA_FILES = [
    '/workspace/page1_data.json',
]

def load_all_records():
    all_records = []
    for f in PAGE_DATA_FILES:
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                all_records.extend(data)
        except Exception as e:
            print(f"Warning: failed to load {f}: {e}")
    return all_records

def filter_over_2000(records):
    result = []
    for r in records:
        # 跳过汇总行
        if r.get('素材ID（巨量）') == '汇总':
            continue
        cost = float(r.get('消耗', 0))
        if cost > 2000:
            result.append(r)
    # 按消耗降序排列
    result.sort(key=lambda x: float(x.get('消耗', 0)), reverse=True)
    return result

def save_csv(records):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M")
    csv_path = f"/workspace/star_report_cost_over_2000_{date_str}.csv"
    
    headers = ['素材ID（巨量）','标题','星图任务ID','星图任务名称','抖音号昵称','抖音号','视频播放链接','下单账户名称','消耗','产品名称','数据统计日期']
    
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in records:
            writer.writerow({h: r.get(h, '') for h in headers})
    
    print(f"[CSV] Saved {len(records)} records to {csv_path}")
    return csv_path

def format_cost(cost_val):
    cost = float(cost_val)
    # 保留2位小数，带千分位
    return f"{cost:,.2f}"

def escape_md_pipe(text):
    return str(text).replace('|', '\\|').replace('\n', ' ').replace('\r', '')

def generate_markdown(records):
    now = datetime.now()
    stat_time = now.strftime("%Y-%m-%d %H:%M")
    
    lines = []
    lines.append("## 【消耗预警】星广报表实时消耗>2000")
    lines.append(f"统计时间：{stat_time}")
    lines.append("| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
    lines.append("|-----------|------|------|---------|------|")
    
    for r in records:
        nickname = escape_md_pipe(r.get('抖音号昵称', ''))
        title = escape_md_pipe(r.get('标题', ''))
        # 标题如果太长，截断到50字
        if len(title) > 50:
            title = title[:50] + "..."
        cost = format_cost(r.get('消耗', 0))
        video_url = r.get('视频播放链接', '')
        link_md = f"[观看]({video_url})" if video_url else ""
        date = escape_md_pipe(r.get('数据统计日期', ''))
        
        lines.append(f"| {nickname} | {title} | {cost} | {link_md} | {date} |")
    
    lines.append(f"共{len(records)}条记录消耗超过2000元")
    
    return "\\n".join(lines)

def main():
    print("[1] Loading records...")
    records = load_all_records()
    print(f"    Total loaded: {len(records)}")
    
    print("[2] Filtering cost > 2000...")
    over_2000 = filter_over_2000(records)
    print(f"    Records with cost > 2000: {len(over_2000)}")
    
    if not over_2000:
        print("    No data over 2000. Exiting.")
        print("RESULT:EMPTY")
        return
    
    for i, r in enumerate(over_2000):
        print(f"    [{i+1}] {r.get('抖音号昵称')}: {format_cost(r.get('消耗'))} - {r.get('标题')[:30]}")
    
    print("[3] Saving CSV...")
    csv_path = save_csv(over_2000)
    
    print("[4] Generating Markdown...")
    md = generate_markdown(over_2000)
    
    # 保存markdown到文件供后续使用
    md_file = "/workspace/feishu_message.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md.replace('\\n', '\n'))
    print(f"    Markdown saved to {md_file}")
    
    print(f"\nCSV_PATH:{csv_path}")
    print(f"COUNT:{len(over_2000)}")
    print("MARKDOWN_START")
    print(md)
    print("MARKDOWN_END")

if __name__ == "__main__":
    main()
