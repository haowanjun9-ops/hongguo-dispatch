#!/usr/bin/env python3
"""
鲸准3.0星广报表数据处理脚本
每小时消耗超2000数据统计
"""

import json
import csv
import subprocess
from datetime import datetime
from typing import List, Dict

# 全局变量存储所有数据
all_data = []

def save_to_csv(data: List[Dict], filename: str):
    """保存数据到CSV文件"""
    if not data:
        return
    
    fieldnames = [
        'materialId', 'title', 'taskId', 'taskName', 'nickname',
        'douyinId', 'videoLink', 'accountName', 'cost', 'productName', 'date'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"数据已保存到: {filename}")

def filter_high_cost_data(data: List[Dict], threshold: float = 2000) -> List[Dict]:
    """筛选消耗超过阈值的数据"""
    filtered = [row for row in data if row.get('cost', 0) > threshold]
    return filtered

def send_feishu_message(data: List[Dict]):
    """发送飞书消息"""
    if not data:
        print("无数据需要发送")
        return
    
    # 统计时间
    now = datetime.now()
    stat_time = now.strftime("%Y-%m-%d %H:%M")
    
    # 构建Markdown消息
    message = f"""## 【消耗预警】星广报表实时消耗>2000
统计时间：{stat_time}
| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |
|-----------|------|------|---------|------|
"""
    
    # 添加表格数据行
    for row in data:
        nickname = row.get('nickname', '')
        title = row.get('title', '')[:30] + '...' if len(row.get('title', '')) > 30 else row.get('title', '')
        cost = row.get('cost', 0)
        video_link = row.get('videoLink', '')
        date = row.get('date', '')
        
        # 格式化视频链接为markdown超链接
        video_link_md = f"[观看]({video_link})" if video_link else ''
        
        message += f"| {nickname} | {title} | {cost} | {video_link_md} | {date} |\n"
    
    message += f"\n共{len(data)}条记录消耗超过2000元"
    
    # 发送飞书消息
    chat_id = "oc_74cf357efbbda7b35af5078abcb29bdb"
    cmd = [
        "lark-cli", "im", "+messages-send",
        "--as", "user",
        "--chat-id", chat_id,
        "--markdown", message
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"飞书消息发送成功")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"飞书消息发送失败: {e.stderr}")
        return False

def main():
    """主函数"""
    global all_data
    
    # 从JSON文件读取数据（由浏览器脚本提取）
    try:
        with open('/workspace/star_report_data.json', 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    except FileNotFoundError:
        print("未找到数据文件，请先提取数据")
        return
    
    print(f"共读取 {len(all_data)} 条数据")
    
    # 筛选消耗超过2000的数据
    filtered_data = filter_high_cost_data(all_data, 2000)
    print(f"筛选出消耗超过2000的记录: {len(filtered_data)} 条")
    
    # 如果没有符合条件的记录，直接结束
    if not filtered_data:
        print("无超2000消耗数据")
        return "无超2000消耗数据"
    
    # 保存CSV文件
    now = datetime.now()
    csv_filename = f"/workspace/star_report_cost_over_2000_{now.strftime('%Y-%m-%d_%H-%M')}.csv"
    save_to_csv(filtered_data, csv_filename)
    
    # 发送飞书消息
    send_feishu_message(filtered_data)
    
    # 返回简要结果
    return f"共筛选出{len(filtered_data)}条，飞书消息发送成功"

if __name__ == "__main__":
    result = main()
    if result:
        print(result)