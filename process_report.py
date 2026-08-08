#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper script to accumulate star report data from browser operations.
Stores results in JSON format for later processing.
"""
import json
import os
import csv
from datetime import datetime

DATA_FILE = "/workspace/star_report_all_data.json"
CSV_FILE_TEMPLATE = "/workspace/star_report_cost_over_2000_{date}.csv"

def init_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"records": [], "pages_processed": []}, f, ensure_ascii=False, indent=2)

def add_records(records, page_num):
    init_data()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Add records (skip summary rows where 素材ID is "汇总")
    valid_records = [r for r in records if r.get("素材ID（巨量）") != "汇总"]
    data["records"].extend(valid_records)
    if page_num not in data["pages_processed"]:
        data["pages_processed"].append(page_num)
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Added {len(valid_records)} records from page {page_num}. Total: {len(data['records'])}, Pages: {sorted(data['pages_processed'])}")
    return len(data["records"])

def get_current_state():
    init_data()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def filter_over_2000():
    data = get_current_state()
    over_2000 = [r for r in data["records"] if float(r.get("消耗", 0)) > 2000]
    print(f"Total records: {len(data['records'])}, Records with cost > 2000: {len(over_2000)}")
    for r in over_2000[:5]:
        print(f"  - {r.get('抖音号昵称')}: {r.get('消耗')} | {r.get('标题')[:30]}")
    return over_2000

def save_csv_over_2000():
    records = filter_over_2000()
    if not records:
        print("No records with cost > 2000")
        return None
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H-%M")
    csv_path = CSV_FILE_TEMPLATE.format(date=date_str)
    
    headers = ['素材ID（巨量）','标题','星图任务ID','星图任务名称','抖音号昵称','抖音号','视频播放链接','下单账户名称','消耗','产品名称','数据统计日期']
    
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in records:
            writer.writerow({h: r.get(h, '') for h in headers})
    
    print(f"Saved {len(records)} records to {csv_path}")
    return csv_path, records

def reset_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    print("Reset data file")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "filter":
            filter_over_2000()
        elif cmd == "save_csv":
            save_csv_over_2000()
        elif cmd == "reset":
            reset_data()
        elif cmd == "state":
            data = get_current_state()
            print(f"Total records: {len(data['records'])}")
            print(f"Pages processed: {sorted(data['pages_processed'])}")
    else:
        print("Usage: python process_report.py [filter|save_csv|reset|state]")
