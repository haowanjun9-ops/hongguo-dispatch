#!/usr/bin/env python3
"""
手动提取数据脚本 - 使用已打开的浏览器
通过browser_evaluate提取当前页数据
"""
import json
import csv
from datetime import datetime

# 当前页提取的数据(从browser_evaluate结果)
current_page_data = [
    {"cost":2409.82,"douyinId":"38139081311","douyinNickname":"小余爱追剧","materialId":"7665252172604293120","orderAccount":"红果KOC-鲸鱼-站内-拉新-1","productName":"","starTaskId":"7626972396727304228","starTaskName":"红果-NG星广ad-短剧综述AI-鲸鱼","statDate":"2026-08-07","title":"碎片时间解闷，打开红果畅快刷短剧 #红果短剧 #AI #HWJLYM","videoLink":"https://douyin.com/video/7665251894918466879"},
    {"cost":1290.86,"douyinId":"38139081311","douyinNickname":"小余爱追剧","materialId":"7665251108878778395","orderAccount":"红果KOC-鲸鱼-站内-拉新-1","productName":"","starTaskId":"7626972396727304228","starTaskName":"红果-NG星广ad-短剧综述AI-鲸鱼","statDate":"2026-08-07","title":"居家休闲神器，红果海量短剧随便看 #红果短剧 #AI #HWJLYM","videoLink":"https://douyin.com/video/7665251159195618602"}
]

def save_to_csv(data, filename):
    """保存数据到CSV"""
    if not data:
        return False
    
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
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = list(field_mapping.keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in data:
            row = {}
            for cn_key, en_key in field_mapping.items():
                row[cn_key] = item.get(en_key, '')
            writer.writerow(row)
    
    return True

def filter_high_cost(data, threshold=2000):
    """筛选消耗超过阈值的记录"""
    return [item for item in data if item.get('cost', 0) > threshold]

if __name__ == "__main__":
    # 筛选消耗超过2000的记录
    high_cost_data = filter_high_cost(current_page_data, 2000)
    
    print(f"当前页数据: {len(current_page_data)} 条")
    print(f"消耗超过2000的记录: {len(high_cost_data)} 条")
    
    if high_cost_data:
        # 保存到CSV
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        csv_file = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"
        
        if save_to_csv(high_cost_data, csv_file):
            print(f"数据已保存到: {csv_file}")
            
            # 打印数据详情
            print("\n消耗超过2000的记录:")
            for item in high_cost_data:
                print(f"  - {item['douyinNickname']}: {item['title'][:30]}... 消耗: {item['cost']}")
    else:
        print("无消耗超过2000的记录")