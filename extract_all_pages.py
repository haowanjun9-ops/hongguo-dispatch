#!/usr/bin/env python3
"""
分步提取所有页面数据
"""
import json
import csv
from datetime import datetime

# 存储所有数据
all_data = []

def save_page_data(page_data):
    """保存页面数据"""
    global all_data
    all_data.extend(page_data)

def save_high_cost_to_csv(threshold=2000):
    """筛选并保存高消耗数据"""
    high_cost = [item for item in all_data if item.get('cost', 0) > threshold]
    
    if not high_cost:
        print("无超2000消耗数据")
        return None
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_file = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"
    
    field_mapping = {
        '素材ID（巨量）': 'materialId',
        '标题': 'title',
        '星图任务ID': 'starTaskId',
        '星图任务名称': 'starTaskName',
        '抖音号昵称': 'douyinNickname',
        '抖音号': 'douyinId',
        '视频播放链接': 'videoLink',
        '下单账户名称': 'orderAccount',
        '消耗': 'cost',
        '产品名称': 'productName',
        '数据统计日期': 'statDate'
    }
    
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = list(field_mapping.keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in high_cost:
            row = {}
            for cn_key, en_key in field_mapping.items():
                row[cn_key] = item.get(en_key, '')
            writer.writerow(row)
    
    print(f"已保存 {len(high_cost)} 条记录到 {csv_file}")
    return csv_file, len(high_cost)

if __name__ == "__main__":
    # 这个脚本将配合浏览器自动化使用
    # 数据将通过browser_evaluate提取并传入
    pass