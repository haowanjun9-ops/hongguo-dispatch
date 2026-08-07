#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化批量提取脚本 - 批处理控制器
通过subprocess循环执行数据提取
"""
import json
import csv
import sys
from datetime import datetime

# 数据存储
all_data = []
filtered_data = []

def save_progress():
    """保存进度"""
    with open('/workspace/extraction_progress.json', 'w') as f:
        json.dump({
            'total_records': len(all_data),
            'filtered_records': len(filtered_data),
            'timestamp': datetime.now().isoformat()
        }, f)

def process_result(json_str):
    """处理提取结果"""
    global all_data, filtered_data

    try:
        result = json.loads(json_str)

        if 'error' in result:
            print(f"Error: {result['error']}")
            return False

        page = result.get('page', 1)
        data = result.get('data', [])

        all_data.extend(data)

        # 筛选
        page_filtered = [row for row in data if row.get('cost', 0) > 2000]
        filtered_data.extend(page_filtered)

        print(f"Page {page}: {len(data)} records, {len(page_filtered)} with cost>2000")
        print(f"Total: {len(all_data)} records, {len(filtered_data)} filtered")

        # 每10页保存一次进度
        if page % 10 == 0:
            save_progress()

        return True

    except Exception as e:
        print(f"Error processing result: {e}")
        return False

def save_final_results():
    """保存最终结果"""
    global all_data, filtered_data

    # 保存所有数据
    with open('/workspace/all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Saved {len(all_data)} total records")

    # 保存筛选后的数据
    if filtered_data:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"

        fieldnames = ['materialId', 'title', 'taskId', 'taskName', 'douyinNickname',
                      'douyinId', 'videoUrl', 'accountName', 'cost', 'productName', 'date']

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_data)

        print(f"✓ Saved {len(filtered_data)} filtered records to {filename}")
        return filename

    print("✗ No filtered records to save")
    return None

if __name__ == '__main__':
    print("=" * 70)
    print("星广报表数据批量提取控制器")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("此脚本通过主程序调用，处理每一页的提取结果")
    print()
    print("使用方法:")
    print("1. 主程序提取数据后调用 process_result()")
    print("2. 完成后调用 save_final_results()")
    print("=" * 70)