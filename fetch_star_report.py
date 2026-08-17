import urllib.request
import urllib.parse
import csv
import json
from datetime import datetime

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNTQzIiwiZXhwIjoxNzg4MTU2MTc3fQ.e_aWRoLI-U8VksLfSSVhIK9Sp6Gajpe0ISY1zeOOLK4"
BASE_URL = "https://wxxcx.whaleidea.cn/material-report/"
PAGE_SIZE = 20
THRESHOLD = 2000

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

def fetch_page(page):
    params = urllib.parse.urlencode({"page": page, "page_size": PAGE_SIZE})
    url = f"{BASE_URL}?{params}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

all_items = []
page = 1
total = None

while True:
    data = fetch_page(page)
    
    if total is None:
        total = data.get("total", 0)
        print(f"Total records: {total}")
    
    items = data.get("items", [])
    if not items:
        break
    
    all_items.extend(items)
    print(f"Page {page}: fetched {len(items)} items (total: {len(all_items)}/{total})")
    
    if len(all_items) >= total:
        break
    
    page += 1

print(f"\nTotal fetched: {len(all_items)}")

# Filter for cost > 2000
high_cost = []
for item in all_items:
    try:
        cost = float(item.get("stat_cost", 0))
        if cost > THRESHOLD:
            high_cost.append(item)
    except (ValueError, TypeError):
        pass

print(f"Records with cost > {THRESHOLD}: {len(high_cost)}")

# Save CSV if there are results
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M")
stat_time = now.strftime("%Y-%m-%d %H:%M")

if high_cost:
    csv_path = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"
    fieldnames = [
        "素材ID（巨量）", "标题", "星图任务ID", "星图任务名称",
        "抖音号昵称", "抖音号", "视频播放链接", "下单账户名称",
        "消耗", "产品名称", "数据统计日期"
    ]
    
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        for item in high_cost:
            row = [
                item.get("material_id", ""),
                item.get("video_title", ""),
                item.get("star_task_id", ""),
                item.get("star_task_name", ""),
                item.get("aweme_name", ""),
                item.get("aweme_id", ""),
                item.get("video_play_link", ""),
                item.get("team_source", ""),
                item.get("stat_cost", ""),
                item.get("product_name", ""),
                item.get("stat_date", "")
            ]
            writer.writerow(row)
    
    print(f"CSV saved: {csv_path}")
    
    # Generate markdown message for Feishu
    md_lines = [
        f"## 【消耗预警】星广报表实时消耗>2000",
        f"统计时间：{stat_time}",
        "",
        "| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |",
        "|-----------|------|------|---------|------|"
    ]
    
    for item in high_cost:
        nick = item.get("aweme_name", "")
        title = item.get("video_title", "")[:50]
        cost = item.get("stat_cost", "")
        link = item.get("video_play_link", "")
        date = item.get("stat_date", "")
        md_lines.append(f"| {nick} | {title} | {cost} | [观看]({link}) | {date} |")
    
    md_lines.append("")
    md_lines.append(f"共{len(high_cost)}条记录消耗超过2000元")
    
    md_content = "\n".join(md_lines)
    
    # Save markdown to file for later use
    md_path = f"/workspace/star_report_cost_over_2000_{timestamp}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"Markdown saved: {md_path}")
    print("\n" + "="*50)
    print("FEISHU MESSAGE PREVIEW:")
    print("="*50)
    print(md_content)
else:
    print("No records with cost > 2000. No Feishu message needed.")
    print(f"\nSummary: Total {len(all_items)} records fetched, 0 records with cost > 2000")
