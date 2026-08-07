#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐页提取并实时筛选的方案
"""
import json
import csv
from datetime import datetime

# 全局数据存储
filtered_data = []

def process_page_result(json_str):
    """处理每页的提取结果"""
    global filtered_data

    try:
        result = json.loads(json_str)

        if 'error' in result:
            print(f"Error: {result['error']}")
            return

        data = result.get('data', [])
        page = result.get('page', '?')

        # 筛选消耗>2000的记录
        page_filtered = [row for row in data if row.get('cost', 0) > 2000]

        if page_filtered:
            filtered_data.extend(page_filtered)
            print(f"Page {page}: Extracted {len(data)} records, Found {len(page_filtered)} with cost>2000, Total filtered: {len(filtered_data)}")
        else:
            print(f"Page {page}: Extracted {len(data)} records, No cost>2000 found")

    except Exception as e:
        print(f"Error processing page: {e}")

def save_filtered_data():
    """保存筛选后的数据"""
    global filtered_data

    if not filtered_data:
        print("No filtered data to save")
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"

    fieldnames = ['materialId', 'title', 'taskId', 'taskName', 'douyinNickname',
                  'douyinId', 'videoUrl', 'accountName', 'cost', 'productName', 'date']

    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_data)

        print(f"\\n✓ Saved {len(filtered_data)} filtered records to {filename}")
        return True

    except Exception as e:
        print(f"✗ Error saving CSV: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("逐页提取并实时筛选方案")
    print("=" * 60)
    print()
    print("处理流程:")
    print("1. 从第1页开始")
    print("2. 提取当前页数据")
    print("3. 筛选消耗>2000的记录")
    print("4. 点击下一页")
    print("5. 重复2-4直到最后一页")
    print("6. 保存筛选后的数据")
    print()
    print("=" * 60)