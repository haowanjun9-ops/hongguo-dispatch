#!/usr/bin/env python3
"""
分步提取数据 - 配合浏览器使用
"""
import json
import csv
from datetime import datetime
import time

# 存储所有数据
all_data = []

def save_page_data(page_data):
    """保存页面数据"""
    global all_data
    all_data.extend(page_data)
    print(f"已提取 {len(page_data)} 条记录，累计 {len(all_data)} 条")

def save_high_cost_to_csv(threshold=2000):
    """筛选并保存高消耗数据"""
    high_cost = [item for item in all_data if item.get('cost', 0) > threshold]
    
    if not high_cost:
        print("\n无超2000消耗数据")
        return None, 0
    
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
    
    print(f"\n已保存 {len(high_cost)} 条记录到 {csv_file}")
    return csv_file, len(high_cost)

# 当前页数据 (从 browser_evaluate 结果中粘贴)
current_page_json = """
[
  {"cost":2409.82,"douyinId":"38139081311","douyinNickname":"小余爱追剧","materialId":"7665252172604293120","orderAccount":"红果KOC-鲸鱼-站内-拉新-1","productName":"","starTaskId":"7626972396727304228","starTaskName":"红果-NG星广ad-短剧综述AI-鲸鱼","statDate":"2026-08-07","title":"碎片时间解闷，打开红果畅快刷短剧 #红果短剧 #AI #HWJLYM","videoLink":"https://douyin.com/video/7665251894918466879"}
]
"""

# 解析并保存
page_data = json.loads(current_page_json)
save_page_data(page_data)

# 最终处理
csv_file, count = save_high_cost_to_csv()
if csv_file:
    print(f"\n任务完成！共筛选出 {count} 条消耗超过2000的记录")