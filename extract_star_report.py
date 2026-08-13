#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鲸准3.0星广报表数据提取脚本
处理步骤：
a. extract_table_data(snapshot_text) 解析所有行
b. filter_mall_records(records) 筛选产品名称含"抖音商城"记录
c. 空或总消耗<=0则退出
d. calc_total_cost(mall_records) 计算总消耗
e. filter_cost_over(mall_records, 2000) 筛选>2000
f. save_csv(over_threshold, "mall_cost_over_2000") 保存CSV
g. build_markdown_message(over, total) 构造消息
h. send_lark_message(md_content) 发送到飞书群
"""

import json
import csv
import re
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/workspace')
DATA_FILE = WORKSPACE / 'star_report_data.json'


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
        row = cells[i:i + row_size]
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
    except Exception:
        return 0.0


def filter_mall_records(records):
    """筛选产品名称等字段包含「抖音商城」的记录"""
    def contains_mall(r):
        fields = [
            r.get('产品名称', ''),
            r.get('标题', ''),
            r.get('下单账户名称', ''),
            r.get('星图任务名称', '')
        ]
        return any('抖音商城' in str(f) for f in fields)

    return [r for r in records if contains_mall(r)]


def calc_total_cost(mall_records):
    """计算抖音商城总消耗"""
    return sum(parse_cost(r.get('消耗', 0)) for r in mall_records)


def filter_cost_over(records, threshold):
    """筛选消耗超过指定阈值的记录"""
    return [r for r in records if parse_cost(r.get('消耗', 0)) > threshold]


def save_csv(records, filename_prefix):
    """保存记录为CSV文件，返回文件路径"""
    if not records:
        return None
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = WORKSPACE / f'{filename_prefix}_{timestamp}.csv'
    fieldnames = [
        '素材ID（巨量）', '标题', '星图任务ID', '星图任务名称',
        '抖音号昵称', '抖音号', '视频播放链接', '下单账户名称',
        '消耗', '产品名称', '数据统计日期'
    ]
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)
    return str(filepath)


def build_markdown_message(over_threshold_records, mall_total_cost):
    """构造飞书markdown消息文本"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []
    lines.append(f'统计时间：{now}')
    lines.append('')
    lines.append('## 【消耗预警】星广报表抖音商城消耗统计')
    lines.append('')
    lines.append('| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |')
    lines.append('| --- | --- | --- | --- | --- |')
    for r in over_threshold_records:
        nick = (r.get('抖音号昵称') or '').replace('|', '\\|').strip()
        title = (r.get('标题') or '').replace('|', '\\|').strip()
        if len(title) > 40:
            title = title[:37] + '...'
        cost = r.get('消耗', '0.00')
        url = r.get('视频播放链接', '')
        link_md = f'[观看]({url})' if url else '-'
        date = r.get('数据统计日期', '')
        lines.append(f'| {nick} | {title} | {cost} | {link_md} | {date} |')
    lines.append('')
    lines.append(f'共{len(over_threshold_records)}条记录消耗超过2000元；抖音商城总消耗：{mall_total_cost:.2f}元')
    return '\n'.join(lines)


def main():
    print("=" * 60)
    print("星广报表抖音商城消耗统计处理开始")
    print("=" * 60)

    # 从JSON加载采集到的数据（浏览器端已筛选）
    if not DATA_FILE.exists():
        print(f'[ERROR] 数据文件不存在: {DATA_FILE}')
        return None

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        collected = json.load(f)

    over_threshold_records = collected.get('over2000Records', [])
    mall_total_cost = float(collected.get('mallTotalCost', 0))
    mall_records_count = collected.get('mallRowsCount', 0)

    print(f'采集总页数: {collected.get("pagesCollected")}/{collected.get("totalPages")}')
    print(f'总记录数: {collected.get("totalRows")}')
    print(f'抖音商城记录数: {mall_records_count}')
    print(f'抖音商城总消耗: {mall_total_cost:.2f}元')
    print(f'消耗>2000元记录数: {len(over_threshold_records)}')

    # c. 若商城记录为空或总消耗<=0，直接结束
    if mall_records_count == 0 or mall_total_cost <= 0:
        print('[INFO] 商城记录为空或总消耗<=0，不发送消息')
        return None

    # f. 保存CSV
    csv_path = save_csv(over_threshold_records, 'mall_cost_over_2000')
    if csv_path:
        print(f'[CSV] 已保存: {csv_path}')

    # g. 构造markdown
    md_content = build_markdown_message(over_threshold_records, mall_total_cost)
    print('[MARKDOWN] 消息内容预览:')
    print('-' * 60)
    print(md_content)
    print('-' * 60)

    # 保存markdown文本供后续使用
    md_file = WORKSPACE / 'lark_message.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f'[MARKDOWN] 已保存到: {md_file}')

    result = {
        'over_threshold_count': len(over_threshold_records),
        'mall_total_cost': round(mall_total_cost, 2),
        'csv_path': csv_path,
        'md_content': md_content,
        'md_file': str(md_file)
    }
    return result


if __name__ == '__main__':
    r = main()
    if r:
        print('\n=== 处理结果 ===')
        print(f'超2000记录数: {r["over_threshold_count"]}')
        print(f'商城总消耗: {r["mall_total_cost"]}元')
