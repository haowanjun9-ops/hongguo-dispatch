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
    lines = snapshot_data.split('\n')
    cells = []
    for line in lines:
        if '- role: cell' in line:
            match = re.search(r'name: (.+)$', line)
            if match:
                cells.append(match.group(1))
    start_idx = 3
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
        cost_str = str(cost_str).replace(',', '').strip()
        return float(cost_str)
    except (ValueError, TypeError):
        return 0.0


def filter_mall_records(records):
    """筛选「产品名称」包含"抖音商城"的记录"""
    return [r for r in records if '抖音商城' in (r.get('产品名称', '') or '')]


def calc_total_cost(records):
    """计算总消耗"""
    return sum(parse_cost(r.get('消耗', 0)) for r in records)


def filter_cost_over(records, threshold):
    """筛选消耗超过阈值的记录"""
    return [r for r in records if parse_cost(r.get('消耗', 0)) > threshold]


def save_csv(records, base_name):
    """保存记录为CSV文件"""
    if not records:
        print(f"无数据可保存: {base_name}")
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{timestamp}.csv"
    filepath = Path("/workspace") / filename
    keys = list(records[0].keys())
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)
    print(f"CSV已保存: {filepath}")
    return str(filepath)


def build_markdown_message(over_threshold_records, mall_total_cost, current_time=None):
    """构造飞书markdown消息"""
    if current_time is None:
        current_time = datetime.now()
    date_str = current_time.strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append("## 【消耗预警】星广报表抖音商城消耗统计")
    lines.append("")
    lines.append(f"> 统计时间：{date_str}")
    lines.append("")
    lines.append("| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
    lines.append("|---|---|---|---|---|")
    for r in over_threshold_records:
        nickname = r.get('抖音号昵称', '-')
        title = (r.get('标题', '') or '').replace('|', '/').replace('\n', ' ')
        cost = r.get('消耗', '0')
        link = r.get('视频播放链接', '')
        link_md = f"[观看]({link})" if link else "-"
        date = r.get('数据统计日期', '-')
        lines.append(f"| {nickname} | {title} | {cost} | {link_md} | {date} |")
    lines.append("")
    lines.append(f"共{len(over_threshold_records)}条记录消耗超过2000元")
    lines.append(f"抖音商城总消耗：{mall_total_cost:.2f}元")
    return "\n".join(lines)


def main():
    print("开始处理星广报表数据...")


if __name__ == '__main__':
    main()
