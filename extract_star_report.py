#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鲸准3.0星广报表数据提取脚本
提取所有消耗>2000的记录并生成CSV文件
"""

import json
import csv
import re
from datetime import datetime
from pathlib import Path

def extract_table_data(snapshot_data):
    """从页面快照数据中提取表格数据"""
    records = []

    # 解析快照数据
    # 表格结构:素材ID(巨量)、标题、星图任务ID、星图任务名称、抖音号昵称、抖音号、视频播放链接、下单账户名称、消耗、产品名称、数据统计日期
    # 每行11个cell元素

    lines = snapshot_data.split('\n')
    cells = []

    # 提取所有cell元素
    for line in lines:
        if '- role: cell' in line:
            # 提取name值
            match = re.search(r'name: (.+)$', line)
            if match:
                cells.append(match.group(1))

    # 跳过汇总行(前3个cell)
    # 每行11个cell
    start_idx = 3  # 跳过汇总行
    row_size = 11

    i = start_idx
    while i + row_size <= len(cells):
        row = cells[i:i+row_size]
        if len(row) == row_size:
            record = {
                '素材ID（巨量）': row[0],
                '标题': row[1],
                '星图任务ID': row[2],
                '星图任务名称': row[3],
                '抖音号昵称': row[4],
                '抖音号': row[5],
                '视频播放链接': row[6],
                '下单账户名称': row[7],
                '消耗': row[8],
                '产品名称': row[9],
                '数据统计日期': row[10]
            }
            records.append(record)
        i += row_size

    return records

def parse_cost(cost_str):
    """解析消耗字段为浮点数"""
    try:
        # 移除可能的逗号和空格
        cost_str = cost_str.replace(',', '').strip()
        return float(cost_str)
    except:
        return 0.0

def main():
    print("开始处理星广报表数据...")
    print("注意:此脚本需要浏览器自动化工具配合使用")
    print("\n请使用浏览器工具逐页提取数据,然后在此脚本中处理")

if __name__ == '__main__':
    main()