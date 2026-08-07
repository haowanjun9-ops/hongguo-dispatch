#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import csv
import os
from datetime import datetime

# 用于存储从浏览器提取的数据
all_data = []

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    if not data:
        print("No data to save")
        return
    
    fieldnames = ['materialId', 'title', 'taskId', 'taskName', 'douyinNickname', 
                  'douyinId', 'videoUrl', 'accountName', 'cost', 'productName', 'date']
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Saved {len(data)} records to {filename}")

def filter_cost_over_2000(data):
    """筛选消耗>2000的记录"""
    filtered = [row for row in data if row['cost'] > 2000]
    return filtered

def main():
    # 这个脚本将接收从浏览器提取的数据
    # 数据将通过标准输入传入
    pass

if __name__ == '__main__':
    main()