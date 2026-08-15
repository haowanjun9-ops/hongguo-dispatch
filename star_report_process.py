#!/usr/bin/env python3
import json, csv
from datetime import datetime

HEADERS = ['素材ID', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', '抖音号',
           '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期']

LARK_CHAT_ID = "oc_74cf357efbbda7b35af5078abcb29bdb"


def extract_table_data(snapshot_text):
    records = []
    lines = snapshot_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('素材ID'):
            continue
        if line.startswith('汇总'):
            continue
        parts = line.split('|||')
        if len(parts) >= 9:
            record = {}
            for i, h in enumerate(HEADERS):
                if i < len(parts):
                    record[h] = parts[i].strip()
                else:
                    record[h] = ''
            if record.get('素材ID') and record['素材ID'] not in ('', '汇总'):
                records.append(record)
    return records


def filter_mall_records(records):
    filtered = []
    for r in records:
        product = r.get('产品名称', '')
        account = r.get('下单账户名称', '')
        title = r.get('标题', '')
        if '抖音商城' in product or '抖音商城' in account or '抖音商城' in title:
            filtered.append(r)
    return filtered


def calc_total_cost(records):
    total = 0.0
    for r in records:
        try:
            cost = float(r.get('消耗', '0'))
            total += cost
        except (ValueError, TypeError):
            pass
    return round(total, 2)


def filter_cost_over(records, threshold):
    result = []
    for r in records:
        try:
            cost = float(r.get('消耗', '0'))
            if cost > threshold:
                result.append(r)
        except (ValueError, TypeError):
            pass
    result.sort(key=lambda x: float(x.get('消耗', '0')), reverse=True)
    return result


def save_csv(records, filename):
    filepath = f"/workspace/{filename}.csv"
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for r in records:
            writer.writerow(r)
    return filepath


def build_markdown_message(records, mall_total_cost):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []
    lines.append(f"## 【消耗预警】星广报表抖音商城消耗统计")
    lines.append(f"")
    lines.append(f"统计时间：{now}")
    lines.append(f"")
    lines.append(f"| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
    lines.append(f"| --- | --- | --- | --- | --- |")
    
    for r in records:
        nickname = r.get('抖音号昵称', '')
        title = r.get('标题', '').replace('|', '｜')
        cost = r.get('消耗', '')
        url = r.get('视频播放链接', '')
        date = r.get('数据统计日期', '')
        
        link = f"[观看]({url})" if url else ''
        lines.append(f"| {nickname} | {title} | {cost} | {link} | {date} |")
    
    lines.append(f"")
    lines.append(f"共{len(records)}条记录消耗超过2000元")
    lines.append(f"抖音商城总消耗：{mall_total_cost}元")
    
    return '\n'.join(lines)


def main():
    snapshot_file = '/workspace/star_report_snapshot.txt'
    
    with open(snapshot_file, 'r', encoding='utf-8') as f:
        snapshot_text = f.read()
    
    records = extract_table_data(snapshot_text)
    print(f"Total records parsed: {len(records)}")
    
    mall_records = filter_mall_records(records)
    print(f"Mall records (抖音商城): {len(mall_records)}")
    
    if not mall_records:
        print("No mall records found. Exiting without sending message.")
        return
    
    mall_total_cost = calc_total_cost(mall_records)
    print(f"Mall total cost: {mall_total_cost}")
    
    if mall_total_cost <= 0:
        print("Total cost <= 0. Exiting without sending message.")
        return
    
    over_threshold = filter_cost_over(mall_records, 2000)
    print(f"Records with cost > 2000: {len(over_threshold)}")
    
    if not over_threshold:
        print("No records exceed 2000 threshold. Exiting without sending message.")
        return
    
    csv_path = save_csv(over_threshold, "mall_cost_over_2000")
    print(f"CSV saved: {csv_path}")
    
    md_content = build_markdown_message(over_threshold, mall_total_cost)
    print(f"Markdown message built.")
    print("---MESSAGE START---")
    print(md_content)
    print("---MESSAGE END---")
    
    # Write markdown to file for lark-cli to read
    md_path = '/workspace/mall_report_md.txt'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Markdown written to: {md_path}")


if __name__ == '__main__':
    main()
