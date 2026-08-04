import requests
import json
import csv
import time
from datetime import datetime

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNTQzIiwiZXhwIjoxNzg3MDY5ODk4fQ.ji0bfMVcYvbzamb97gWUASFA-hKN0NEix8B1FTeiEXQ"
BASE_URL = "https://wxxcx.whaleidea.cn/material-report/"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
PAGE_SIZE = 100

# Use today's date
today = datetime.now().strftime("%Y-%m-%d")
start_date = today
end_date = today

params_base = {
    "start_date": start_date,
    "end_date": end_date,
}

print(f"Fetching data for {today}...")

# First request to get total count
params = {**params_base, "page": 1, "page_size": PAGE_SIZE}
resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
data = resp.json()
total = data["total"]
total_cost = data.get("total_cost", "0")
print(f"Total records: {total}, Total cost: {total_cost}")

# Filter first page
filtered_records = []
items = data.get("items", [])
for item in items:
    try:
        cost = float(item.get("stat_cost", 0))
        if cost > 2000:
            filtered_records.append(item)
    except (ValueError, TypeError):
        pass

# Fetch remaining pages
total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
for page in range(2, total_pages + 1):
    params["page"] = page
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
        data = resp.json()
        items = data.get("items", [])
        
        for item in items:
            try:
                cost = float(item.get("stat_cost", 0))
                if cost > 2000:
                    filtered_records.append(item)
            except (ValueError, TypeError):
                pass
        
        if page % 5 == 0:
            print(f"Progress: Page {page}/{total_pages}, filtered so far: {len(filtered_records)}")
    except Exception as e:
        print(f"Error on page {page}: {e}")
        time.sleep(2)
        continue

print(f"\nTotal records with stat_cost > 2000: {len(filtered_records)}")

# Save to CSV if there are filtered records
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
csv_filename = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"

if filtered_records:
    fieldnames = list(filtered_records[0].keys())
    
    with open(csv_filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_records)
    
    print(f"Saved CSV to: {csv_filename}")
    
    # Print summary
    print("\n=== Records with cost > 2000 ===")
    for r in filtered_records:
        print(f"  昵称: {r.get('aweme_name', 'N/A')} | 消耗: {r.get('stat_cost', 'N/A')} | 日期: {r.get('stat_date', 'N/A')}")
        print(f"    标题: {r.get('video_title', 'N/A')[:80]}")
        print(f"    链接: {r.get('video_play_link', 'N/A')}")
        print()
else:
    print("No records with stat_cost > 2000. No CSV will be saved.")
    csv_filename = None

# Save summary JSON
result = {
    "total_records_today": total,
    "total_cost_today": total_cost,
    "filtered_count": len(filtered_records),
    "csv_file": csv_filename,
    "filtered_records": filtered_records,
}

json_filename = f"/workspace/star_report_summary_{timestamp}.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\nSummary saved to: {json_filename}")
print(f"\nFINAL_RESULT: filtered_count={len(filtered_records)}, csv={csv_filename}")
