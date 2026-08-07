#!/usr/bin/env python3
"""
提取所有页面数据并构建飞书消息
"""
import csv
import json
from datetime import datetime
import subprocess

# 所有提取的数据（分步提取后汇总）
# 这里只包含第一页的数据作为示例
all_extracted_data = [
    {"cost":2409.82,"douyinId":"38139081311","douyinNickname":"小余爱追剧","materialId":"7665252172604293120","orderAccount":"红果KOC-鲸鱼-站内-拉新-1","productName":"","starTaskId":"7626972396727304228","starTaskName":"红果-NG星广ad-短剧综述AI-鲸鱼","statDate":"2026-08-07","title":"碎片时间解闷，打开红果畅快刷短剧 #红果短剧 #AI #HWJLYM","videoLink":"https://douyin.com/video/7665251894918466879"},
    {"cost":1290.86,"douyinId":"38139081311","douyinNickname":"小余爱追剧","materialId":"7665251108878778395","orderAccount":"红果KOC-鲸鱼-站内-拉新-1","productName":"","starTaskId":"7626972396727304228","starTaskName":"红果-NG星广ad-短剧综述AI-鲸鱼","statDate":"2026-08-07","title":"居家休闲神器，红果海量短剧随便看 #红果短剧 #AI #HWJLYM","videoLink":"https://douyin.com/video/7665251159195618602"}
]

def filter_high_cost(data, threshold=2000):
    """筛选消耗超过阈值的记录"""
    return [item for item in data if item.get('cost', 0) > threshold]

def save_to_csv(data, filename):
    """保存数据到CSV"""
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

def build_feishu_message(high_cost_data):
    """构建飞书消息"""
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
        title_short = item['title'][:30] + "..." if len(item['title']) > 30 else item['title']
        # 构建markdown链接
        video_link = f"[观看]({item['videoLink']})"
        
        message_lines.append(
            f"| {item['douyinNickname']} | {title_short} | {item['cost']} | {video_link} | {item['statDate']} |"
        )
    
    message_lines.append(f"\n共{len(high_cost_data)}条记录消耗超过2000元")
    
    return "\n".join(message_lines)

def send_feishu_message(message):
    """发送飞书消息"""
    try:
        result = subprocess.run(
            [
                'lark-cli', 'im', '+messages-send',
                '--as', 'user',
                '--chat-id', 'oc_74cf357efbbda7b35af5078abcb29bdb',
                '--markdown', message
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("="*60)
    print("鲸准3.0星广报表数据处理")
    print("="*60)
    
    # 筛选消耗超过2000的记录
    high_cost_data = filter_high_cost(all_extracted_data, 2000)
    
    print(f"总记录数: {len(all_extracted_data)}")
    print(f"消耗超过2000的记录: {len(high_cost_data)} 条")
    
    if not high_cost_data:
        print("\n无超2000消耗数据")
        return
    
    # 保存到CSV
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_file = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"
    save_to_csv(high_cost_data, csv_file)
    print(f"\n数据已保存到: {csv_file}")
    
    # 构建飞书消息
    feishu_message = build_feishu_message(high_cost_data)
    
    print("\n飞书消息内容:")
    print(feishu_message)
    
    # 发送飞书消息
    print("\n正在发送飞书消息...")
    success, stdout, stderr = send_feishu_message(feishu_message)
    
    if success:
        print("✓ 飞书消息发送成功！")
    else:
        print("✗ 飞书消息发送失败")
        if stderr:
            print(f"错误: {stderr}")
    
    print(f"\n任务完成！共筛选出 {len(high_cost_data)} 条消耗超过2000的记录")

if __name__ == "__main__":
    main()