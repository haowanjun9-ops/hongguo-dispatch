#!/usr/bin/env python3
"""
处理提取的数据并发送飞书消息
"""
import csv
import json
from datetime import datetime
import subprocess

# 从browser_evaluate提取的第一页数据(包含消耗超过2000的记录)
high_cost_data = [
    {
        '素材ID（巨量）': '7665252172604293120',
        '标题': '碎片时间解闷，打开红果畅快刷短剧 #红果短剧 #AI #HWJLYM',
        '星图任务ID': '7626972396727304228',
        '星图任务名称': '红果-NG星广ad-短剧综述AI-鲸鱼',
        '抖音号昵称': '小余爱追剧',
        '抖音号': '38139081311',
        '视频播放链接': 'https://douyin.com/video/7665251894918466879',
        '下单账户名称': '红果KOC-鲸鱼-站内-拉新-1',
        '消耗': 2409.82,
        '产品名称': '',
        '数据统计日期': '2026-08-07'
    }
]

# 保存到CSV
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
csv_file = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"

with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
    fieldnames = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', 
                  '抖音号', '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(high_cost_data)

print(f"数据已保存到: {csv_file}")

# 构建飞书消息
stat_time = datetime.now().strftime("%Y-%m-%d %H:%M")
message_lines = [
    "## 【消耗预警】星广报表实时消耗>2000",
    f"统计时间：{stat_time}",
    "",
    "| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |",
    "|-----------|------|------|---------|------|"
]

for item in high_cost_data:
    # 截取标题前30个字符
    title_short = item['标题'][:30] + "..." if len(item['标题']) > 30 else item['标题']
    # 构建markdown链接
    video_link = f"[观看]({item['视频播放链接']})"
    
    message_lines.append(
        f"| {item['抖音号昵称']} | {title_short} | {item['消耗']} | {video_link} | {item['数据统计日期']} |"
    )

message_lines.append(f"\n共{len(high_cost_data)}条记录消耗超过2000元")

# 合并消息
feishu_message = "\n".join(message_lines)

print("\n飞书消息内容:")
print(feishu_message)

# 发送飞书消息
try:
    result = subprocess.run(
        [
            'lark-cli', 'im', '+messages-send',
            '--as', 'user',
            '--chat-id', 'oc_74cf357efbbda7b35af5078abcb29bdb',
            '--markdown', feishu_message
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print(f"\n飞书消息发送结果:")
    print(f"返回码: {result.returncode}")
    if result.stdout:
        print(f"输出: {result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")
    
    if result.returncode == 0:
        print("\n飞书消息发送成功！")
    else:
        print("\n飞书消息发送失败")
except Exception as e:
    print(f"\n发送飞书消息时出错: {e}")

print(f"\n任务完成！共筛选出 {len(high_cost_data)} 条消耗超过2000的记录")