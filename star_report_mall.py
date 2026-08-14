#!/usr/bin/env python3
import requests
import json
import csv
import os
import subprocess
from datetime import datetime

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNTQzIiwiZXhwIjoxNzg3ODg5Nzg2fQ.TXUNgdu27rmmiu-dzVtjqGHFykMel7cHDe13D-y25tI"
BASE_URL = "https://wxxcx.whaleidea.cn/material-report/"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
PAGE_SIZE = 20


def fetch_all_data():
    all_items = []
    total_cost = 0
    page = 1
    total_pages = None

    while True:
        url = f"{BASE_URL}?page={page}&page_size={PAGE_SIZE}"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        items = data.get("items", [])
        if not items:
            break

        all_items.extend(items)
        total_cost = float(data.get("total_cost", 0))
        total = data.get("total", 0)

        if total_pages is None:
            total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
            print(f"总记录数: {total}, 总页数: {total_pages}")

        print(f"  第{page}/{total_pages}页, 获取{len(items)}条 (累计{len(all_items)})")

        if page >= total_pages:
            break
        page += 1

    print(f"全量获取完成: {len(all_items)}条, 总消耗: {total_cost:.2f}")
    return all_items, total_cost


def filter_mall_records(records):
    return [r for r in records if r.get("product_name") and "抖音商城" in str(r.get("product_name", ""))]


def calc_total_cost(records):
    return sum(float(r.get("stat_cost", 0)) for r in records)


def filter_cost_over(records, threshold):
    return [r for r in records if float(r.get("stat_cost", 0)) > threshold]


def save_csv(records, filename):
    filepath = f"/workspace/{filename}.csv"
    if not records:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write("")
        print(f"CSV已保存(空): {filepath}")
        return filepath

    keys = list(records[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)
    print(f"CSV已保存: {filepath} ({len(records)}条)")
    return filepath


def build_markdown_message(over_threshold_records, mall_total_cost):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append("## 【消耗预警】星广报表抖音商城消耗统计")
    lines.append("")
    lines.append(f"**统计时间：{now}**")
    lines.append("")

    if over_threshold_records:
        lines.append("| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for r in over_threshold_records:
            nickname = r.get("aweme_name", "")
            title = (r.get("video_title", "") or "")[:50]
            cost = float(r.get("stat_cost", 0))
            url = r.get("video_play_link", "")
            date = r.get("stat_date", "")
            link_text = f"[观看]({url})" if url else ""
            lines.append(f"| {nickname} | {title} | {cost:.2f} | {link_text} | {date} |")
    else:
        lines.append("暂无消耗超过2000元的记录。")

    lines.append("")
    lines.append(f"共{len(over_threshold_records)}条记录消耗超过2000元")
    lines.append(f"抖音商城总消耗：{mall_total_cost:.2f}元")

    return "\n".join(lines)


def send_lark_message(md_content):
    """Send markdown message to Feishu group via lark-cli"""
    try:
        with open("/workspace/lark_message.md", "w", encoding="utf-8") as f:
            f.write(md_content)

        result = subprocess.run(
            ["lark-cli", "im", "send", "--chat-id", "oc_74cf357efbbda7b35af5078abcb29bdb",
             "--content", md_content, "--msg-type", "interactive"],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            print("飞书消息发送成功")
            return True
        else:
            print(f"飞书消息发送失败: {result.stderr}")
            result2 = subprocess.run(
                ["lark-cli", "im", "send", "--chat-id", "oc_74cf357efbbda7b35af5078abcb29bdb",
                 "--content", md_content, "--msg-type", "text"],
                capture_output=True, text=True, timeout=30
            )
            if result2.returncode == 0:
                print("飞书消息发送成功(text)")
                return True
            print(f"备用方案也失败: {result2.stderr}")
            return False
    except Exception as e:
        print(f"发送飞书消息异常: {e}")
        return False


def main():
    print("=" * 50)
    print("星广报表抖音商城消耗统计")
    print("=" * 50)

    print("\n[1] 正在获取全量数据...")
    all_records, total_cost = fetch_all_data()

    if not all_records:
        print("未获取到任何数据，结束任务。")
        return

    print("\n[2] 筛选抖音商城记录...")
    mall_records = filter_mall_records(all_records)
    print(f"抖音商城记录数: {len(mall_records)}")

    if not mall_records:
        print("无抖音商城记录，结束任务。")
        return

    mall_total_cost = calc_total_cost(mall_records)
    print(f"抖音商城总消耗: {mall_total_cost:.2f}元")

    if mall_total_cost <= 0:
        print("总消耗<=0，结束任务不发消息。")
        return

    print("\n[3] 筛选消耗>2000的记录...")
    over_threshold_records = filter_cost_over(mall_records, 2000)
    print(f"消耗>2000的记录数: {len(over_threshold_records)}")

    print("\n[4] 保存CSV...")
    csv_path = save_csv(over_threshold_records, "mall_cost_over_2000")

    print("\n[5] 构建飞书消息...")
    md_content = build_markdown_message(over_threshold_records, mall_total_cost)
    print(md_content)

    print("\n[6] 发送飞书消息...")
    send_success = send_lark_message(md_content)

    print("\n" + "=" * 50)
    print("执行结果：")
    print(f"  总记录数: {len(all_records)}")
    print(f"  抖音商城记录数: {len(mall_records)}")
    print(f"  消耗>2000记录数: {len(over_threshold_records)}")
    print(f"  抖音商城总消耗: {mall_total_cost:.2f}元")
    print(f"  飞书发送状态: {'成功' if send_success else '失败'}")
    print("=" * 50)

    # Save analysis results
    result = {
        "total_records": len(all_records),
        "mall_records_count": len(mall_records),
        "over_2000_count": len(over_threshold_records),
        "mall_total_cost": mall_total_cost,
        "send_status": "success" if send_success else "failed",
        "md_content": md_content
    }
    with open("/workspace/analysis_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n分析结果已保存: /workspace/analysis_result.json")


if __name__ == "__main__":
    main()