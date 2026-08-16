import requests
import json
import csv
import os
from datetime import datetime

BASE_URL = "https://wxxcx.whaleidea.cn/material-report/"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNTQzIiwiZXhwIjoxNzg4MDYyNTEyfQ.dZySUzX6BMoBUP63de2BpeWOhQ7vDrL9FyGhw50Hxqg"
PAGE_SIZE = 100
OUTPUT_DIR = "/workspace"


def fetch_all_data():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    all_items = []
    page = 1
    total = None

    while True:
        params = {"page": page, "page_size": PAGE_SIZE}
        resp = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if total is None:
            total = data.get("total", 0)
            print(f"Total records: {total}")

        items = data.get("items", [])
        if not items:
            break

        all_items.extend(items)
        print(f"Fetched page {page}: {len(items)} items (total so far: {len(all_items)})")

        if len(all_items) >= total:
            break

        page += 1

    return all_items


def extract_table_data(snapshot_text=None):
    records = fetch_all_data()
    print(f"Total records fetched: {len(records)}")
    return records


def filter_mall_records(records):
    mall_records = []
    for r in records:
        product_name = r.get("product_name", "")
        if "抖音商城" in product_name:
            mall_records.append(r)
    print(f"Mall records (product_name contains 抖音商城): {len(mall_records)}")
    return mall_records


def calc_total_cost(mall_records):
    total = 0.0
    for r in mall_records:
        cost_str = r.get("stat_cost", "0") or "0"
        try:
            total += float(cost_str)
        except (ValueError, TypeError):
            pass
    print(f"Total mall cost: {total:.2f}")
    return total


def filter_cost_over(mall_records, threshold):
    result = []
    for r in mall_records:
        cost_str = r.get("stat_cost", "0") or "0"
        try:
            cost = float(cost_str)
        except (ValueError, TypeError):
            cost = 0.0
        if cost > threshold:
            result.append(r)
    print(f"Records with cost > {threshold}: {len(result)}")
    return result


def save_csv(records, filename):
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.csv")
    if not records:
        print(f"No records to save to {filepath}")
        return filepath

    fieldnames = [
        "抖音号昵称", "标题", "消耗", "视频链接", "日期",
        "product_name", "material_id", "aweme_id", "star_task_id"
    ]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            cost_str = r.get("stat_cost", "0") or "0"
            try:
                cost = float(cost_str)
                cost_display = f"{cost:.2f}"
            except (ValueError, TypeError):
                cost_display = cost_str

            row = {
                "抖音号昵称": r.get("aweme_name", ""),
                "标题": r.get("video_title", ""),
                "消耗": cost_display,
                "视频链接": r.get("video_play_link", ""),
                "日期": r.get("stat_date", ""),
                "product_name": r.get("product_name", ""),
                "material_id": r.get("material_id", ""),
                "aweme_id": r.get("aweme_id", ""),
                "star_task_id": r.get("star_task_id", ""),
            }
            writer.writerow(row)

    print(f"Saved {len(records)} records to {filepath}")
    return filepath


def build_markdown_message(over_threshold_records, mall_total_cost):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append(f"## 【消耗预警】星广报表抖音商城消耗统计")
    lines.append(f"")
    lines.append(f"统计时间：{now}")
    lines.append(f"")
    lines.append(f"| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
    lines.append(f"| --- | --- | --- | --- | --- |")

    for r in over_threshold_records:
        nickname = r.get("aweme_name", "")
        title = r.get("video_title", "")
        cost_str = r.get("stat_cost", "0") or "0"
        try:
            cost = float(cost_str)
            cost_display = f"{cost:.2f}"
        except (ValueError, TypeError):
            cost_display = cost_str
        video_url = r.get("video_play_link", "")
        stat_date = r.get("stat_date", "")

        short_title = title[:30] + "..." if len(title) > 30 else title
        video_link = f"[观看]({video_url})" if video_url else ""

        lines.append(f"| {nickname} | {short_title} | {cost_display} | {video_link} | {stat_date} |")

    lines.append(f"")
    lines.append(f"共{len(over_threshold_records)}条记录消耗超过2000元")
    lines.append(f"抖音商城总消耗：{mall_total_cost:.2f}元")

    return "\n".join(lines)


def main():
    print("=" * 50)
    print("星广报表抖音商城消耗统计")
    print("=" * 50)

    # Step 1: Fetch all data
    print("\n[1] Fetching data from API...")
    records = extract_table_data()

    # Step 2: Filter mall records
    print("\n[2] Filtering 抖音商城 records...")
    mall_records = filter_mall_records(records)

    # Step 3: Check if we should continue
    if not mall_records:
        print("\n[3] No mall records found. Exiting.")
        return {"success": True, "skip": "no_mall_records"}

    mall_total_cost = calc_total_cost(mall_records)
    if mall_total_cost <= 0:
        print("\n[3] Total cost <= 0. Exiting.")
        return {"success": True, "skip": "zero_cost"}

    # Step 4: Filter records with cost > 2000
    print("\n[4] Filtering records with cost > 2000...")
    over_threshold = filter_cost_over(mall_records, 2000)

    # Step 5: Save CSV
    print("\n[5] Saving CSV...")
    csv_path = save_csv(over_threshold, "mall_cost_over_2000")

    # Step 6: Build markdown message
    print("\n[6] Building markdown message...")
    md_content = build_markdown_message(over_threshold, mall_total_cost)

    # Save the markdown for later use
    md_path = os.path.join(OUTPUT_DIR, "mall_report_message.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Markdown saved to {md_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Total records: {len(records)}")
    print(f"  Mall records: {len(mall_records)}")
    print(f"  Mall total cost: {mall_total_cost:.2f}")
    print(f"  Records with cost > 2000: {len(over_threshold)}")
    print(f"  CSV saved: {csv_path}")
    print(f"  Markdown saved: {md_path}")
    print("=" * 50)

    return {
        "success": True,
        "total_records": len(records),
        "mall_records": len(mall_records),
        "mall_total_cost": mall_total_cost,
        "over_threshold_count": len(over_threshold),
        "csv_path": csv_path,
        "md_path": md_path,
        "md_content": md_content,
    }


if __name__ == "__main__":
    result = main()
    # Save result as JSON for next step
    with open(os.path.join(OUTPUT_DIR, "mall_report_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
