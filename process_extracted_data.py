#!/usr/bin/env python3
"""
完整的自动化脚本 - 使用browser工具分步执行
"""
import csv
import json
from datetime import datetime

# 存储所有数据
all_extracted_data = []

def save_page_data(page_num, data):
    """保存页面数据"""
    global all_extracted_data
    all_extracted_data.extend(data)
    print(f"第{page_num}页: {len(data)}条记录, 累计: {len(all_extracted_data)}条")

def save_high_cost_to_csv(threshold=2000):
    """筛选并保存高消耗数据"""
    high_cost = [item for item in all_extracted_data if item.get('cost', 0) > threshold]
    
    if not high_cost:
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
    
    return csv_file, len(high_cost)

# 第一页数据
page1_data = [
    {"cost":2409.82,"douyinId":"38139081311","douyinNickname":"小余爱追剧","materialId":"7665252172604293120","orderAccount":"红果KOC-鲸鱼-站内-拉新-1","productName":"","starTaskId":"7626972396727304228","starTaskName":"红果-NG星广ad-短剧综述AI-鲸鱼","statDate":"2026-08-07","title":"碎片时间解闷，打开红果畅快刷短剧 #红果短剧 #AI #HWJLYM","videoLink":"https://douyin.com/video/7665251894918466879"},
    {"cost":1290.86,"douyinId":"38139081311","douyinNickname":"小余爱追剧","materialId":"7665251108878778395","orderAccount":"红果KOC-鲸鱼-站内-拉新-1","productName":"","starTaskId":"7626972396727304228","starTaskName":"红果-NG星广ad-短剧综述AI-鲸鱼","statDate":"2026-08-07","title":"居家休闲神器，红果海量短剧随便看 #红果短剧 #AI #HWJLYM","videoLink":"https://douyin.com/video/7665251159195618602"}
]

save_page_data(1, page1_data)

# 筛选并保存
csv_file, count = save_high_cost_to_csv()

if csv_file:
    print(f"\n数据已保存到: {csv_file}")
    print(f"共筛选出 {count} 条消耗超过2000的记录")
else:
    print("\n无超2000消耗数据")

# 输出数据用于飞书消息
high_cost = [item for item in all_extracted_data if item.get('cost', 0) > 2000]
print("\n消耗超过2000的记录:")
for item in high_cost:
    print(f"  - {item['douyinNickname']}: {item['title'][:30]}... 消耗: {item['cost']}")