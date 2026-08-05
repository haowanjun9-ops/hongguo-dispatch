#!/usr/bin/env python3
"""
处理第一页数据并筛选消耗超过2000的记录
"""

import json
import csv
import subprocess
from datetime import datetime

# 第一页数据
first_page_data = [
  {"accountName":"抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1","cost":13881.14,"date":"2026-08-05","douyinId":"42513895368","materialId":"7660509756013215754","nickname":"智能效率社","productName":"","taskId":"7657431178504634394","taskName":"新LOGO-抖音商城APP-NG-AI签到01-鲸鱼","title":"点击视频下方链接，就能领红包 #抖音商城 #福利多多 #剪辑制作 #签到 #网赚","videoLink":"https://douyin.com/video/7660509798789696787"},
  {"accountName":"红果KOC-鲸鱼-站内-拉新-1","cost":10597.21,"date":"2026-08-05","douyinId":"38139081311","materialId":"7665252172604293120","nickname":"小余爱追剧","productName":"","taskId":"7626972396727304228","taskName":"红果-NG星广ad-短剧综述AI-鲸鱼","title":"碎片时间解闷，打开红果畅快刷短剧 #红果短剧 #AI #HWJLYM","videoLink":"https://douyin.com/video/7665251894918466879"},
  {"accountName":"红果KOC-鲸鱼-站内-拉新-1","cost":3124.7,"date":"2026-08-05","douyinId":"38139081311","materialId":"7665251108878778395","nickname":"小余爱追剧","productName":"","taskId":"7626972396727304228","taskName":"红果-NG星广ad-短剧综述AI-鲸鱼","title":"居家休闲神器，红果海量短剧随便看 #红果短剧 #AI #HWJLYM","videoLink":"https://douyin.com/video/7665251159195618602"}
]

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    fieldnames = [
        'materialId', 'title', 'taskId', 'taskName', 'nickname',
        'douyinId', 'videoLink', 'accountName', 'cost', 'productName', 'date'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"数据已保存到: {filename}")

def send_feishu_message(data):
    """发送飞书消息"""
    if not data:
        print("无数据需要发送")
        return False
    
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
        title = row.get('title', '')
        # 截断过长的标题
        if len(title) > 30:
            title = title[:30] + '...'
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
    
    print("准备发送飞书消息...")
    print(f"消息内容:\n{message}")
    
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
    # 筛选消耗超过2000的数据
    filtered_data = [row for row in first_page_data if row.get('cost', 0) > 2000]
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
    send_success = send_feishu_message(filtered_data)
    
    # 返回简要结果
    status = "成功" if send_success else "失败"
    return f"共筛选出{len(filtered_data)}条，飞书消息发送{status}"

if __name__ == "__main__":
    result = main()
    print(result)