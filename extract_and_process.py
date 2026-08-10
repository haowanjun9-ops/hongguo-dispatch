#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星广报表数据提取和处理脚本
"""

import json
import csv
import subprocess
from datetime import datetime
from pathlib import Path

def main():
    print("=" * 60)
    print("星广报表数据处理脚本")
    print("=" * 60)

    # 模拟从第一页提取的数据(实际应从浏览器提取)
    # 这里使用测试数据，实际需要从浏览器JavaScript中获取
    sample_data = [
        {
            "素材ID（巨量）": "7665252172604293120",
            "标题": "碎片时间解闷，打开红果畅快刷短剧 #红果短剧 #AI #HWJLYM",
            "星图任务ID": "7626972396727304228",
            "星图任务名称": "红果-NG星广ad-短剧综述AI-鲸鱼",
            "抖音号昵称": "小余爱追剧",
            "抖音号": "38139081311",
            "视频播放链接": "https://douyin.com/video/7665251894918466879",
            "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1",
            "消耗": "8515.14",
            "产品名称": "",
            "数据统计日期": "2026-08-10"
        },
        {
            "素材ID（巨量）": "7670534059169726504",
            "标题": "红果短剧APP，海量短剧全免费！ #红果短剧 #AI #HWJLDA",
            "星图任务ID": "7660403527034355763",
            "星图任务名称": "红果-NG星广ad-短剧综述AI-02-鲸鱼",
            "抖音号昵称": "闪耀猕果社",
            "抖音号": "93208595202",
            "视频播放链接": "https://douyin.com/video/7670534018856701235",
            "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1",
            "消耗": "4957.95",
            "产品名称": "",
            "数据统计日期": "2026-08-10"
        },
        {
            "素材ID（巨量）": "7670910071551918126",
            "标题": "每日福利更新，签到抢先拿到限时权益 #网赚 #签到 #真人实拍 #福利多多 #抖音商城",
            "星图任务ID": "7641104807520763955",
            "星图任务名称": "新LOGO-抖音商城APP-NG-签到01-鲸鱼",
            "抖音号昵称": "苏苏有话说",
            "抖音号": "91733539137",
            "视频播放链接": "https://douyin.com/video/7670910194758520090",
            "下单账户名称": "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1",
            "消耗": "4595.53",
            "产品名称": "",
            "数据统计日期": "2026-08-10"
        },
        {
            "素材ID（巨量）": "7670530535924432939",
            "标题": "保持每日打卡习惯，累计时长上涨好礼持续加码 #网赚 #签到 #福利多多 #抖音商城 #剪辑制作",
            "星图任务ID": "7657431178504634394",
            "星图任务名称": "新LOGO-抖音商城APP-NG-AI签到01-鲸鱼",
            "抖音号昵称": "孜然哔哔机",
            "抖音号": "55428852738",
            "视频播放链接": "https://douyin.com/video/7670530542692994339",
            "下单账户名称": "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1",
            "消耗": "2866.35",
            "产品名称": "",
            "数据统计日期": "2026-08-10"
        },
        {
            "素材ID（巨量）": "7670506457710411803",
            "标题": "无需辗转等候，红果短剧篇章新意频出 #HWJYXT #红果短剧 #潜力",
            "星图任务ID": "7661894329392349226",
            "星图任务名称": "红果-NG星广ad-真人综述-实拍-04-鲸鱼",
            "抖音号昵称": "外卖阿彭",
            "抖音号": "42068123484",
            "视频播放链接": "https://douyin.com/video/7670506541866437922",
            "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1",
            "消耗": "2232.21",
            "产品名称": "",
            "数据统计日期": "2026-08-10"
        }
    ]

    all_data = sample_data

    print(f"\n总记录数: {len(all_data)}")

    # 筛选消耗>2000的记录
    print("\n正在筛选消耗>2000的记录...")
    filtered_data = []
    for row in all_data:
        try:
            cost = float(row['消耗'])
            if cost > 2000:
                filtered_data.append(row)
        except (ValueError, KeyError) as e:
            print(f"  警告: 无法解析消耗值 '{row.get('消耗', 'N/A')}'")
            continue

    print(f"筛选结果: {len(filtered_data)} 条消耗>2000的记录")

    # 如果没有筛选结果，直接返回
    if len(filtered_data) == 0:
        print("\n⚠️  无超2000消耗数据")
        print("=" * 60)
        return "无超2000消耗数据"

    # 保存CSV文件
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_filename = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"

    print(f"\n正在保存CSV文件: {csv_filename}")
    headers = [
        '素材ID（巨量）', '标题', '星图任务ID', '星图任务名称',
        '抖音号昵称', '抖音号', '视频播放链接',
        '下单账户名称', '消耗', '产品名称', '数据统计日期'
    ]

    with open(csv_filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(filtered_data)

    print(f"✅ CSV文件已保存")

    # 生成飞书消息
    print("\n正在生成飞书消息...")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 构建Markdown表格
    message_lines = [
        "## 【消耗预警】星广报表实时消耗>2000",
        f"\n统计时间：{current_time}\n",
        "\n| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |",
        "|-----------|------|------|---------|------|"
    ]

    for row in filtered_data:
        nickname = row['抖音号昵称']
        title = row['标题'][:30] + "..." if len(row['标题']) > 30 else row['标题']
        cost = row['消耗']
        video_link = row['视频播放链接']
        date = row['数据统计日期']

        # 格式化视频链接为markdown超链接
        video_link_md = f"[观看]({video_link})"

        message_lines.append(f"| {nickname} | {title} | {cost} | {video_link_md} | {date} |")

    message_lines.append(f"\n共 **{len(filtered_data)}** 条记录消耗超过2000元")

    message = "\n".join(message_lines)

    print("消息内容预览:")
    print("-" * 60)
    print(message)
    print("-" * 60)

    # 发送飞书消息
    print("\n正在发送飞书消息...")
    chat_id = "oc_74cf357efbbda7b35af5078abcb29bdb"

    try:
        cmd = [
            "lark-cli", "im", "+messages-send",
            "--as", "user",
            "--chat-id", chat_id,
            "--markdown", message
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ 飞书消息发送成功")
            send_status = "成功"
        else:
            print(f"❌ 飞书消息发送失败: {result.stderr}")
            send_status = "失败"

    except subprocess.TimeoutExpired:
        print("❌ 飞书消息发送超时")
        send_status = "超时"
    except FileNotFoundError:
        print("❌ lark-cli 命令未找到，请确保已安装飞书CLI")
        send_status = "命令未找到"
    except Exception as e:
        print(f"❌ 飞书消息发送异常: {e}")
        send_status = f"异常: {str(e)}"

    print("\n" + "=" * 60)
    print("任务完成!")
    print(f"  - 筛选出记录数: {len(filtered_data)} 条")
    print(f"  - CSV文件: {csv_filename}")
    print(f"  - 飞书消息发送: {send_status}")
    print("=" * 60)

    return {
        "success": True,
        "filtered_records": len(filtered_data),
        "csv_file": csv_filename,
        "feishu_status": send_status
    }

if __name__ == "__main__":
    result = main()
    print(f"\n最终结果: {json.dumps(result, ensure_ascii=False)}")