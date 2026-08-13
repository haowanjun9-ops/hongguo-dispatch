#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鲸准3.0星广报表数据提取脚本（抖音商城版）
功能：
- 提取星广报表数据，筛选产品名称含"抖音商城"的记录
- 统计抖音商城总消耗
- 筛选消耗>2000的商城记录明细
- 生成CSV文件并发送飞书消息
定时：每4小时一次（8:00/12:00/16:00/20:00）
"""

import json
import csv
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

CHAT_ID = "oc_74cf357efbbda7b35af5078abcb29bdb"
CSV_OUTPUT_DIR = Path("/workspace")


def extract_table_data(snapshot_data):
    """从页面快照数据中提取表格数据"""
    records = []
    lines = snapshot_data.split('\n')
    cells = []

    for line in lines:
        if '- role: cell' in line:
            match = re.search(r'name: (.+)$', line)
            if match:
                cells.append(match.group(1))

    start_idx = 3
    row_size = 11

    i = start_idx
    while i + row_size <= len(cells):
        row = cells[i:i + row_size]
        if len(row) == row_size:
            record = {
                '素材ID（巨量）': row[0],
                '标题': row[1],
                '星图任务ID': row[2],
                '星图任务名称': row[3],
                '抖音号昵称': row[4],
                '抖音号': row[5],
                '视频播放链接': row[6],
                '下单账户名称': row[7],
                '消耗': row[8],
                '产品名称': row[9],
                '数据统计日期': row[10]
            }
            records.append(record)
        i += row_size

    return records


def parse_cost(cost_str):
    """解析消耗字段为浮点数"""
    try:
        cost_str = str(cost_str).replace(',', '').strip()
        return float(cost_str)
    except Exception:
        return 0.0


def filter_mall_records(records):
    """筛选产品名称包含'抖音商城'的记录"""
    return [r for r in records if '抖音商城' in str(r.get('产品名称', ''))]


def filter_cost_over(records, threshold=2000):
    """筛选消耗超过指定阈值的记录"""
    return [r for r in records if parse_cost(r.get('消耗', '0')) > threshold]


def calc_total_cost(records):
    """计算记录的总消耗"""
    return sum(parse_cost(r.get('消耗', '0')) for r in records)


def save_csv(records, suffix="mall_cost_over_2000"):
    """保存记录到CSV文件，返回文件路径"""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M")
    filename = f"star_report_{suffix}_{timestamp}.csv"
    filepath = CSV_OUTPUT_DIR / filename

    if records:
        headers = list(records[0].keys())
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(records)
        print(f"CSV已保存: {filepath}")
    else:
        print("无记录，未生成CSV")
    return filepath


def build_markdown_message(over_threshold_records, mall_total_cost):
    """构造飞书markdown消息"""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")

    lines = [
        "## 【消耗预警】星广报表抖音商城消耗统计",
        f"统计时间：{timestamp}",
        "",
        "| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |",
        "|-----------|------|------|---------|------|",
    ]

    for r in over_threshold_records:
        nickname = str(r.get('抖音号昵称', '')).replace('|', '\\|')
        title = str(r.get('标题', '')).replace('|', '\\|')
        cost_val = parse_cost(r.get('消耗', '0'))
        cost_str = f"{cost_val:,.2f}"
        video_url = str(r.get('视频播放链接', '')).strip()
        date_str = str(r.get('数据统计日期', ''))

        if video_url:
            link_str = f"[观看]({video_url})"
        else:
            link_str = "-"

        lines.append(f"| {nickname} | {title} | {cost_str} | {link_str} | {date_str} |")

    lines.append("")
    lines.append(f"共{len(over_threshold_records)}条记录消耗超过2000元")
    lines.append(f"抖音商城总消耗：{mall_total_cost:,.2f}元")

    return "\n".join(lines)


def send_lark_message(markdown_content):
    """通过lark-cli发送飞书消息"""
    cmd = [
        "lark-cli", "im", "+messages-send",
        "--as", "user",
        "--chat-id", CHAT_ID,
        "--markdown", markdown_content
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("飞书消息发送成功")
            return True, result.stdout
        else:
            print(f"飞书消息发送失败: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"发送飞书消息异常: {e}")
        return False, str(e)


def process_data(snapshot_data):
    """
    处理数据的主入口
    Args:
        snapshot_data: 浏览器工具提取的页面快照文本（包含cell信息）
    Returns:
        dict: {status, message, over_threshold_count, mall_total_cost, csv_path, lark_sent}
    """
    print(f"开始处理星广报表数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    records = extract_table_data(snapshot_data)
    print(f"提取表格记录数: {len(records)}")

    mall_records = filter_mall_records(records)
    print(f"抖音商城记录数: {len(mall_records)}")

    if not mall_records:
        print("无抖音商城记录，任务结束")
        return {
            "status": "skip_no_mall_data",
            "message": "无抖音商城消耗数据",
            "over_threshold_count": 0,
            "mall_total_cost": 0,
            "csv_path": None,
            "lark_sent": False
        }

    mall_total_cost = calc_total_cost(mall_records)
    print(f"抖音商城总消耗: {mall_total_cost:,.2f}")

    if mall_total_cost <= 0:
        print("抖音商城总消耗为0，任务结束，不发消息")
        return {
            "status": "skip_zero_cost",
            "message": "抖音商城总消耗为0，不发消息",
            "over_threshold_count": 0,
            "mall_total_cost": 0,
            "csv_path": None,
            "lark_sent": False
        }

    over_threshold_records = filter_cost_over(mall_records, 2000)
    print(f"商城消耗>2000的记录数: {len(over_threshold_records)}")

    csv_path = save_csv(over_threshold_records, "mall_cost_over_2000")

    md_message = build_markdown_message(over_threshold_records, mall_total_cost)
    print("飞书消息内容预览:")
    print("=" * 50)
    print(md_message)
    print("=" * 50)

    lark_ok, lark_output = send_lark_message(md_message)

    result = {
        "status": "sent" if lark_ok else "send_failed",
        "message": "飞书消息已发送" if lark_ok else f"飞书消息发送失败: {lark_output}",
        "over_threshold_count": len(over_threshold_records),
        "mall_total_cost": mall_total_cost,
        "csv_path": str(csv_path) if csv_path.exists() else None,
        "lark_sent": lark_ok
    }
    print(f"处理结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    return result


def main():
    print("=" * 60)
    print("鲸准3.0星广报表 - 抖音商城消耗统计脚本")
    print("定时频率: 8:00 / 12:00 / 16:00 / 20:00")
    print("=" * 60)
    print("\n使用方式：")
    print("1. 通过浏览器自动化工具登录并访问 https://apex.whaleidea.cn/star/report")
    print("2. 点击查询按钮，逐页翻页并使用browser工具获取页面快照")
    print("3. 将快照文本保存，调用 process_data(snapshot_data) 处理")
    print("\n或作为模块导入使用：")
    print("  from extract_star_report import process_data")
    print("  result = process_data(snapshot_text)")
    print()


if __name__ == '__main__':
    main()
