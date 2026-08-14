#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星广报表抖音商城消耗统计处理脚本
"""

import json
import csv
import os
import re
from datetime import datetime

# 全局存储所有页的数据
ALL_RECORDS = []
PAGE_HEADERS = []


def save_page_data(page_num, headers, rows):
    """保存单页数据到全局存储和文件"""
    global ALL_RECORDS, PAGE_HEADERS
    if headers and not PAGE_HEADERS:
        PAGE_HEADERS = headers
    
    ALL_RECORDS.extend(rows)
    
    # 同时保存到文件作为备份
    filename = f"/workspace/page_data/page_{page_num}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"page": page_num, "headers": headers, "rows": rows}, f, ensure_ascii=False, indent=2)
    
    print(f"[保存] 第{page_num}页, 本页{len(rows)}行, 累计{len(ALL_RECORDS)}行")


def extract_table_data(snapshot_text=None, json_data=None):
    """
    解析快照文本，提取表格数据
    支持两种方式：1) 快照文本  2) JSON数据
    """
    records = []
    
    if json_data:
        rows = json_data.get('rows', [])
        for row in rows:
            record = {}
            for key, val in row.items():
                if isinstance(val, dict):
                    record[key] = val.get('text', '')
                    if key == '视频播放链接':
                        record['视频链接URL'] = val.get('href', '') or val.get('text', '')
                else:
                    record[key] = str(val) if val else ''
            records.append(record)
    
    elif snapshot_text:
        # 从快照文本中解析（简单的正则解析）
        lines = snapshot_text.split('\n')
        current_record = {}
        in_record = False
        
        # 这里需要根据实际快照格式进行解析
        # 简化处理：将快照文本直接保存，后续再处理
        records = [{"_raw_snapshot": snapshot_text}]
    
    return records


def filter_mall_records(records):
    """筛选产品名称或相关字段包含抖音商城的记录"""
    mall_records = []
    
    keywords = ['抖音商城', '抖音商城版']
    
    for record in records:
        # 跳过汇总行
        material_id = record.get('素材ID（巨量）', '')
        if material_id == '汇总':
            continue
        
        is_mall = False
        # 检查多个字段：产品名称、星图任务名称、标题、下单账户名称
        for field in ['产品名称', '星图任务名称', '标题', '下单账户名称']:
            val = record.get(field, '')
            if val and any(kw in val for kw in keywords):
                is_mall = True
                break
        
        if is_mall:
            mall_records.append(record)
    
    return mall_records


def calc_total_cost(records):
    """计算总消耗"""
    total = 0.0
    for r in records:
        try:
            cost = float(r.get('消耗', '0') or 0)
            total += cost
        except (ValueError, TypeError):
            pass
    return round(total, 2)


def filter_cost_over(records, threshold):
    """筛选消耗超过阈值的记录"""
    result = []
    for r in records:
        try:
            cost = float(r.get('消耗', '0') or 0)
            if cost > threshold:
                result.append(r)
        except (ValueError, TypeError):
            pass
    # 按消耗降序排列
    result.sort(key=lambda x: float(x.get('消耗', '0') or 0), reverse=True)
    return result


def save_csv(records, filename_prefix):
    """保存CSV到/workspace"""
    if not records:
        print("没有数据需要保存CSV")
        return None
    
    filepath = f"/workspace/{filename_prefix}.csv"
    # 字段名
    fieldnames = ['抖音号昵称', '标题', '消耗', '视频链接URL', '数据统计日期']
    
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for r in records:
            writer.writerow({
                '抖音号昵称': r.get('抖音号昵称', ''),
                '标题': r.get('标题', ''),
                '消耗': r.get('消耗', ''),
                '视频链接URL': r.get('视频链接URL', r.get('视频播放链接', '')),
                '数据统计日期': r.get('数据统计日期', '')
            })
    
    print(f"[CSV保存] {filepath}, 共{len(records)}条记录")
    return filepath


def build_markdown_message(over_threshold_records, mall_total_cost):
    """构造Markdown消息"""
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M")
    
    lines = []
    lines.append(f"统计时间：{time_str}")
    lines.append("")
    lines.append("## 【消耗预警】星广报表抖音商城消耗统计")
    lines.append("")
    lines.append("| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
    lines.append("| --- | --- | --- | --- | --- |")
    
    for r in over_threshold_records:
        nickname = r.get('抖音号昵称', '')
        title = r.get('标题', '')
        # 截断过长标题
        if len(title) > 50:
            title = title[:47] + '...'
        cost = r.get('消耗', '')
        video_url = r.get('视频链接URL', r.get('视频播放链接', ''))
        date = r.get('数据统计日期', '')
        
        link_md = f"[观看]({video_url})" if video_url else ''
        
        lines.append(f"| {nickname} | {title} | {cost} | {link_md} | {date} |")
    
    lines.append("")
    lines.append(f"共{len(over_threshold_records)}条记录消耗超过2000元；抖音商城总消耗：{mall_total_cost}元")
    
    return "\\n".join(lines)


def merge_all_pages():
    """合并所有页的JSON数据"""
    all_records = []
    page_data_dir = "/workspace/page_data"
    if not os.path.exists(page_data_dir):
        print(f"目录不存在: {page_data_dir}")
        return []
    
    files = sorted(os.listdir(page_data_dir))
    for fname in files:
        if fname.endswith('.json') and fname.startswith('page_'):
            with open(os.path.join(page_data_dir, fname), 'r', encoding='utf-8') as f:
                data = json.load(f)
            records = extract_table_data(json_data=data)
            all_records.extend(records)
    
    print(f"合并完成，共{len(all_records)}条记录，来自{len([x for x in files if x.endswith('.json')])}页")
    return all_records


if __name__ == "__main__":
    import sys
    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == 'merge':
        records = merge_all_pages()
        mall_records = filter_mall_records(records)
        print(f"商城记录数: {len(mall_records)}")
        total = calc_total_cost(mall_records)
        print(f"商城总消耗: {total}")
        over2000 = filter_cost_over(mall_records, 2000)
        print(f"超2000记录数: {len(over2000)}")
        for r in over2000:
            print(f"  {r.get('抖音号昵称')} - {r.get('消耗')}")
        if over2000:
            save_csv(over2000, "mall_cost_over_2000")
            md = build_markdown_message(over2000, total)
            print("\\n=== Markdown消息 ===")
            print(md)
