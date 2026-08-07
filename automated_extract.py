#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化数据提取主控脚本
通过MCP工具逐页控制浏览器
"""
import json
import csv
from datetime import datetime

# 全局数据存储
all_data = []
filtered_data = []
total_pages = 52

def process_page(json_str):
    """处理单页提取结果"""
    global all_data, filtered_data

    try:
        result = json.loads(json_str)

        if 'error' in result:
            return False, result['error']

        page = result.get('page', '?')
        data = result.get('data', result.get('rows', []))

        if not isinstance(data, list):
            return False, 'Invalid data format'

        # 保存所有数据
        all_data.extend(data)

        # 实时筛选消耗>2000的记录
        page_filtered = [row for row in data if row.get('cost', 0) > 2000]
        filtered_data.extend(page_filtered)

        print(f"✓ Page {page}: {len(data)} records, {len(page_filtered)} with cost>2000, Total: {len(all_data)}")

        return True, None

    except Exception as e:
        return False, str(e)

def save_results():
    """保存所有结果"""
    global all_data, filtered_data

    # 保存完整数据
    with open('/workspace/all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Saved {len(all_data)} records to all_data.json")

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

    return None

if __name__ == '__main__':
    print("=" * 70)
    print("星广报表数据自动化提取系统")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总页数: {total_pages}")
    print("=" * 70)
    print()
    print("准备就绪，等待主程序调用...")
    print()
    print("使用方法:")
    print("1. 调用 process_page() 处理每页数据")
    print("2. 调用 save_results() 保存最终结果")
    print("=" * 70)