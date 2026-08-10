#!/usr/bin/env python3
"""
星广报表数据处理和飞书消息发送
"""
import json
import csv
import os
import subprocess
from datetime import datetime

def process_json_data(json_file):
    """从JSON文件读取并筛选数据"""
    if not os.path.exists(json_file):
        print(f"错误: 文件 {json_file} 不存在")
        return []

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 筛选消耗>2000的记录
    filtered_data = []
    for item in data:
        try:
            # 清理消耗字符串
            cost_str = item['消耗']
            if isinstance(cost_str, (int, float)):
                cost = float(cost_str)
            else:
                # 清理字符串
                cost_str = str(cost_str).replace('¥', '').replace('￥', '').replace(',', '').replace('，', '').replace('元', '').strip()
                cost = float(cost_str)

            if cost > 2000:
                item['消耗值'] = cost
                filtered_data.append(item)
        except Exception as e:
            # 尝试提取数字
            try:
                import re
                numbers = re.findall(r'\d+\.?\d*', str(item['消耗']))
                if numbers:
                    cost = float(numbers[0])
                    if cost > 2000:
                        item['消耗值'] = cost
                        filtered_data.append(item)
            except:
                pass

    return filtered_data

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    if not data:
        return None

    fieldnames = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', '抖音号',
                  '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期']

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ CSV文件已保存: {filename}")
    return filename

def generate_feishu_message(filtered_data):
    """生成飞书消息内容"""
    if not filtered_data:
        return None

    # 统计时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    # 构建Markdown表格
    message_lines = [
        "## 【消耗预警】星广报表实时消耗>2000",
        f"统计时间：{current_time}",
        "",
        "| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |",
        "|-----------|------|------|---------|------|"
    ]

    for item in filtered_data[:20]:  # 最多显示20条
        nickname = item.get('抖音号昵称', '')
        title = item.get('标题', '')[:30]  # 截取前30个字符
        cost = item.get('消耗', '')
        video_link = item.get('视频播放链接', '')
        date = item.get('数据统计日期', '')

        # 格式化视频链接
        video_link_formatted = f"[观看]({video_link})" if video_link else ''

        message_lines.append(
            f"| {nickname} | {title} | {cost} | {video_link_formatted} | {date} |"
        )

    # 添加汇总
    message_lines.append("")
    message_lines.append(f"共 **{len(filtered_data)}** 条记录消耗超过2000元")

    return '\n'.join(message_lines)

def send_feishu_message(chat_id, message):
    """发送飞书消息"""
    try:
        # 构建lark-cli命令
        cmd = [
            'lark-cli', 'im', '+messages-send',
            '--as', 'user',
            '--chat-id', chat_id,
            '--markdown', message
        ]

        print(f"\n发送飞书消息...")
        print(f"目标群聊: {chat_id}")

        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ 飞书消息发送成功")
            return True
        else:
            print(f"❌ 飞书消息发送失败: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 发送飞书消息时出错: {e}")
        return False

def main():
    print("=== 星广报表数据处理 ===\n")

    # 检查是否有数据文件
    json_file = '/workspace/star_report_filtered_data.json'

    if not os.path.exists(json_file):
        # 尝试其他可能的文件名
        possible_files = [
            '/workspace/filtered_data.json',
            '/workspace/all_data.json',
            '/workspace/star_report_data.json'
        ]

        for f in possible_files:
            if os.path.exists(f):
                json_file = f
                break

    if not os.path.exists(json_file):
        print("⚠️ 未找到数据文件")
        print("请先运行浏览器控制台脚本提取数据，并将数据保存为JSON文件")
        print(f"或将提取的数据保存到: {json_file}")
        return

    print(f"读取数据文件: {json_file}")

    # 处理数据
    filtered_data = process_json_data(json_file)

    if not filtered_data:
        print("\n⚠️ 无超2000消耗数据")
        return

    print(f"✅ 筛选出 {len(filtered_data)} 条消耗>2000的记录")

    # 保存CSV
    current_time = datetime.now().strftime('%H%M%S')
    csv_filename = f'/workspace/star_report_cost_over_2000_2026-08-10_{current_time}.csv'
    save_to_csv(filtered_data, csv_filename)

    # 生成飞书消息
    message = generate_feishu_message(filtered_data)

    if message:
        print("\n生成的飞书消息:")
        print("-" * 80)
        print(message)
        print("-" * 80)

        # 发送飞书消息
        chat_id = 'oc_74cf357efbbda7b35af5078abcb29bdb'
        send_feishu_message(chat_id, message)

    print(f"\n✨ 任务完成!")
    print(f"- 筛选记录数: {len(filtered_data)}")
    print(f"- CSV文件: {csv_filename}")

if __name__ == "__main__":
    main()