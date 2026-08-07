#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取星广报表数据的脚本
"""
import json
import csv
import os
from datetime import datetime

# 存储所有数据
ALL_DATA = []

def process_page_data(page_num, data):
    """处理页面数据"""
    global ALL_DATA
    ALL_DATA.extend(data)
    print(f"Page {page_num}: Extracted {len(data)} records, Total: {len(ALL_DATA)}")

def filter_cost_over_2000(data):
    """筛选消耗>2000的记录"""
    filtered = [row for row in data if row['cost'] > 2000]
    return filtered

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    if not data:
        print("No data to save")
        return False
    
    fieldnames = ['materialId', 'title', 'taskId', 'taskName', 'douyinNickname', 
                  'douyinId', 'videoUrl', 'accountName', 'cost', 'productName', 'date']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"✓ Saved {len(data)} records to {filename}")
        return True
    except Exception as e:
        print(f"✗ Error saving CSV: {e}")
        return False

def get_current_timestamp():
    """获取当前时间戳"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M")

def get_current_date():
    """获取当前日期"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d")

if __name__ == '__main__':
    # 测试
    test_data = [
        {
            'materialId': '123',
            'title': '测试标题',
            'taskId': '456',
            'taskName': '测试任务',
            'douyinNickname': '测试昵称',
            'douyinId': '789',
            'videoUrl': 'http://test.com',
            'accountName': '测试账户',
            'cost': 3000.5,
            'productName': '测试产品',
            'date': '2026-08-07'
        }
    ]
    
    filtered = filter_cost_over_2000(test_data)
    print(f"Filtered: {len(filtered)} records")
    
    save_to_csv(test_data, '/workspace/test.csv')