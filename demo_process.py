#!/usr/bin/env python3
"""
测试星广报表数据处理和飞书消息发送
"""
import json
import csv
import subprocess
from datetime import datetime

def process_data(json_file):
    """处理JSON数据"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 筛选消耗>2000的记录
    filtered_data = []
    for item in data:
        try:
            cost_str = str(item['消耗']).replace('¥', '').replace(',', '').strip()
            cost = float(cost_str)

            if cost > 2000:
                item['消耗值'] = cost
                filtered_data.append(item)
                print(f"✓ {item['抖音号昵称']}: ¥{item['消耗']} > 2000")
        except Exception as e:
            print(f"⚠ 解析失败: {item.get('消耗', 'N/A')}")

    return filtered_data

def save_csv(data, filename):
    """保存CSV文件"""
    fieldnames = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', '抖音号',
                  '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期']

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

    print(f"\n✅ CSV已保存: {filename}")

def generate_message(filtered_data):
    """生成飞书消息"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    lines = [
        "## 【消耗预警】星广报表实时消耗>2000",
        f"统计时间：{current_time}",
        "",
        "| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |",
        "|-----------|------|------|---------|------|"
    ]

    for item in filtered_data:
        nickname = item.get('抖音号昵称', '')
        title = item.get('标题', '')[:30]
        cost = item.get('消耗', '')
        video_link = item.get('视频播放链接', '')
        date = item.get('数据统计日期', '')

        video_link_formatted = f"[观看]({video_link})" if video_link else ''

        lines.append(f"| {nickname} | {title} | {cost} | {video_link_formatted} | {date} |")

    lines.append("")
    lines.append(f"共 **{len(filtered_data)}** 条记录消耗超过2000元")

    return '\n'.join(lines)

def send_message(chat_id, message):
    """发送飞书消息"""
    print(f"\n📱 发送飞书消息到群聊: {chat_id}")

    try:
        result = subprocess.run(
            ['lark-cli', 'im', '+messages-send', '--as', 'user', '--chat-id', chat_id, '--markdown', message],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ 飞书消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

def main():
    print("=== 星广报表数据处理测试 ===\n")

    # 处理演示数据
    print("📊 处理数据:")
    filtered_data = process_data('/workspace/demo_data.json')

    print(f"\n筛选结果: {len(filtered_data)} 条消耗>2000的记录\n")

    if not filtered_data:
        print("⚠️ 无超2000消耗数据")
        return

    # 保存CSV
    current_time = datetime.now().strftime('%H%M%S')
    csv_file = f'/workspace/star_report_cost_over_2000_2026-08-10_{current_time}.csv'
    save_csv(filtered_data, csv_file)

    # 生成消息
    message = generate_message(filtered_data)

    print("\n📝 生成的飞书消息:")
    print("=" * 80)
    print(message)
    print("=" * 80)

    # 发送消息
    chat_id = 'oc_74cf357efbbda7b35af5078abcb29bdb'
    send_message(chat_id, message)

    print(f"\n✨ 任务完成!")
    print(f"- 筛选记录数: {len(filtered_data)}")
    print(f"- CSV文件: {csv_file}")

if __name__ == "__main__":
    main()