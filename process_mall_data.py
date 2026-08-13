#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星广报表抖音商城消耗统计 - 数据处理脚本
"""
import json
import csv
import os
import sys
from datetime import datetime

# ============ 第1-10页采集的原始数据 (199条) ============
RAW_DATA_JSON = r'''
[__RAW_DATA_PLACEHOLDER__]
'''

def extract_table_data(records_json_str):
    """a. 解析所有行"""
    # 实际数据已通过浏览器采集传入，这里直接解析
    if records_json_str.strip().startswith('['):
        return json.loads(records_json_str)
    return []

def filter_mall_records(records):
    """b. 筛选产品名称/标题/计划名包含'抖音商城'的记录"""
    result = []
    for r in records:
        product = r.get('product_name', '')
        title = r.get('title', '')
        plan = r.get('plan_name', '')
        if '抖音商城' in product or '抖音商城' in title or '抖音商城' in plan:
            if not product:
                r['product_name'] = '抖音商城'
            result.append(r)
    return result

def calc_total_cost(mall_records):
    """d. 计算商城总消耗"""
    total = 0.0
    for r in mall_records:
        try:
            total += float(r.get('cost', 0))
        except (ValueError, TypeError):
            pass
    return round(total, 2)

def filter_cost_over(records, threshold):
    """e. 筛选消耗超过阈值的明细"""
    result = []
    for r in records:
        try:
            cost = float(r.get('cost', 0))
            if cost > threshold:
                result.append(r)
        except (ValueError, TypeError):
            pass
    # 按消耗降序
    result.sort(key=lambda x: float(x.get('cost', 0)), reverse=True)
    return result

def save_csv(records, filename_prefix):
    """f. 保存CSV到/workspace"""
    filepath = f'/workspace/{filename_prefix}.csv'
    if not records:
        print(f'  记录为空，跳过CSV保存')
        return filepath
    
    fieldnames = ['抖音号昵称', '标题', '消耗', '视频链接', '日期', '产品名称', '计划名称']
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({
                '抖音号昵称': r.get('douyin_nickname', ''),
                '标题': r.get('title', ''),
                '消耗': r.get('cost', ''),
                '视频链接': r.get('video_url', ''),
                '日期': r.get('date', ''),
                '产品名称': r.get('product_name', ''),
                '计划名称': r.get('plan_name', '')
            })
    print(f'  CSV已保存至: {filepath}')
    return filepath

def build_markdown_message(over_threshold_records, mall_total_cost):
    """g. 构造markdown消息"""
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    lines = []
    lines.append(f'统计时间：{now_str}')
    lines.append('')
    lines.append('## 【消耗预警】星广报表抖音商城消耗统计')
    lines.append('')
    lines.append('| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |')
    lines.append('| --- | --- | --- | --- | --- |')
    
    for r in over_threshold_records:
        nickname = r.get('douyin_nickname', '').replace('|', '\\|')
        title = r.get('title', '').replace('|', '\\|')
        # 标题截断避免过长
        if len(title) > 60:
            title = title[:57] + '...'
        cost = r.get('cost', '')
        url = r.get('video_url', '')
        date = r.get('date', '')
        link_md = f'[观看]({url})' if url else ''
        lines.append(f'| {nickname} | {title} | {cost} | {link_md} | {date} |')
    
    lines.append('')
    n = len(over_threshold_records)
    lines.append(f'共{n}条记录消耗超过2000元；抖音商城总消耗：{mall_total_cost}元')
    
    return '\n'.join(lines)

def main(records_json_str):
    print('=== 星广报表抖音商城消耗统计 ===')
    print()
    
    # a. 解析所有行
    all_records = extract_table_data(records_json_str)
    print(f'a. 解析总行数: {len(all_records)}')
    
    # b. 筛选抖音商城记录
    mall_records = filter_mall_records(all_records)
    print(f'b. 抖音商城记录数: {len(mall_records)}')
    
    # c. 空记录或总消耗<=0直接结束
    if not mall_records:
        print('c. 商城记录为空，直接结束不发消息')
        return {
            'over_threshold_count': 0,
            'mall_total_cost': 0,
            'lark_sent': False,
            'skip_reason': 'no_mall_records'
        }
    
    mall_total = calc_total_cost(mall_records)
    print(f'c. 商城总消耗: {mall_total} 元')
    
    if mall_total <= 0:
        print('c. 总消耗<=0，直接结束不发消息')
        return {
            'over_threshold_count': 0,
            'mall_total_cost': 0,
            'lark_sent': False,
            'skip_reason': 'total_cost_zero'
        }
    
    # d. 总消耗（已在上面计算）
    print(f'd. 商城总消耗: {mall_total} 元')
    
    # e. 筛选消耗>2000的记录
    over_threshold = filter_cost_over(mall_records, 2000)
    print(f'e. 消耗>2000的记录数: {len(over_threshold)}')
    for i, r in enumerate(over_threshold):
        print(f'   {i+1}. {r.get("douyin_nickname")} - 消耗{r.get("cost")}元')
    
    # f. 保存CSV
    csv_path = save_csv(over_threshold, 'mall_cost_over_2000')
    
    # g. 构造markdown
    md_content = build_markdown_message(over_threshold, mall_total)
    print()
    print('g. Markdown消息预览:')
    print('-' * 60)
    print(md_content)
    print('-' * 60)
    
    # h. 输出md_content供后续发送飞书使用
    result = {
        'over_threshold_count': len(over_threshold),
        'mall_total_cost': mall_total,
        'csv_path': csv_path,
        'md_content': md_content,
        'mall_records_count': len(mall_records),
        'lark_sent_pending': True
    }
    
    # 将结果写入文件供主流程读取
    with open('/workspace/mall_data_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print()
    print(f'结果已写入 /workspace/mall_data_result.json')
    
    return result

if __name__ == '__main__':
    # 通过命令行参数传入JSON文件路径，或者使用默认的嵌入数据
    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            json_str = f.read()
        print(f'从文件 {sys.argv[1]} 加载数据')
    else:
        # 默认：读取环境中生成的raw_data文件
        data_path = '/workspace/raw_report_data.json'
        if os.path.exists(data_path):
            with open(data_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
            print(f'从文件 {data_path} 加载数据')
        else:
            json_str = '[]'
            print(f'警告: 未找到数据文件')
    
    main(json_str)
