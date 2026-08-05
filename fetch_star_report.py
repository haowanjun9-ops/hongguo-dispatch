#!/usr/bin/env python3
import requests
import csv
import re
import time
from datetime import datetime

API_BASE = "https://wxxcx.whaleidea.cn"
LOGIN_URL = f"{API_BASE}/auth/login"
REPORT_URL = f"{API_BASE}/material-report/"
USERNAME = "haowanjun@whalewh.cn"
PASSWORD = "?!]d<yI0"
OUTPUT_DIR = "/workspace"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "https://apex.whaleidea.cn",
    "Referer": "https://apex.whaleidea.cn/",
}


def login(session):
    print("[1] 正在登录...")
    try:
        resp = session.post(
            LOGIN_URL,
            json={"user_name": USERNAME, "user_password": PASSWORD},
            headers={**HEADERS, "Content-Type": "application/json"},
            timeout=30,
        )
        print(f"    登录响应状态码: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            if token:
                session.headers["Authorization"] = f"Bearer {token}"
                print("    登录成功")
                return True
            else:
                print("    响应中未找到 access_token")
                return False
        else:
            print(f"    登录失败，状态码: {resp.status_code}")
            print(f"    响应: {resp.text[:300]}")
            return False
    except Exception as e:
        print(f"    登录异常: {e}")
        return False


def fetch_all_data(session):
    print("\n[2] 正在获取数据...")
    all_records = []
    page = 1
    page_size = 100
    total_fetched = None

    while True:
        params = {"page": page, "page_size": page_size}
        try:
            resp = session.get(REPORT_URL, params=params, headers=HEADERS, timeout=30)
            print(f"    第 {page} 页: 状态码 {resp.status_code}")

            if resp.status_code == 401 or resp.status_code == 403:
                print("    认证失败 (401/403)")
                break

            if resp.status_code != 200:
                print(f"    非预期状态码: {resp.status_code}")
                print(f"    响应: {resp.text[:500]}")
                break

            data = resp.json()
            items = data.get("items", [])
            total = data.get("total", 0)

            if total_fetched is None:
                total_fetched = total
                print(f"    总计: {total} 条记录")

            print(f"    本页获取 {len(items)} 条")
            all_records.extend(items)

            if len(all_records) >= total:
                print(f"    已获取全部数据 ({len(all_records)}/{total})")
                break

            if len(items) < page_size:
                print(f"    本页记录数 ({len(items)}) < page_size ({page_size})，已获取全部数据")
                break

            page += 1

            time.sleep(0.2)

        except requests.exceptions.RequestException as e:
            print(f"    请求异常: {e}")
            break
        except Exception as e:
            print(f"    解析异常: {e}")
            import traceback
            traceback.print_exc()
            break

    return all_records


def get_field_value(record, *field_names):
    for name in field_names:
        if name in record and record[name] is not None:
            return record[name]
    return ""


def parse_cost(val):
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).replace(",", "").replace("¥", "").replace("￥", "").strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0


def filter_and_save(records):
    print(f"\n[3] 正在过滤和保存数据...")
    filtered = []

    for record in records:
        cost = parse_cost(get_field_value(record, "stat_cost", "消耗", "cost"))
        if cost > 2000:
            row = {
                "素材ID（巨量）": str(get_field_value(record, "material_id")),
                "标题": str(get_field_value(record, "video_title", "title")),
                "星图任务ID": str(get_field_value(record, "star_task_id")),
                "星图任务名称": str(get_field_value(record, "star_task_name")),
                "抖音号昵称": str(get_field_value(record, "aweme_name", "nickname")),
                "抖音号": str(get_field_value(record, "aweme_id")),
                "视频播放链接": str(get_field_value(record, "video_play_link")),
                "下单账户名称": str(get_field_value(record, "bd_name", "account_name")),
                "消耗": cost,
                "产品名称": str(get_field_value(record, "product_name")),
                "数据统计日期": str(get_field_value(record, "stat_date", "date")),
            }
            filtered.append(row)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_path = f"{OUTPUT_DIR}/star_report_cost_over_2000_{timestamp}.csv"

    if filtered:
        fieldnames = list(filtered[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered)
        print(f"    已保存 {len(filtered)} 条记录到: {csv_path}")
    else:
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0].keys()) if records else [])
            if records:
                writer.writeheader()
        print(f"    无符合条件的记录，创建空 CSV: {csv_path}")

    return csv_path


def main():
    print("=" * 60)
    print("星图报表数据抓取脚本")
    print("=" * 60)

    session = requests.Session()

    login_ok = login(session)
    print(f"\n登录结果: {'成功' if login_ok else '失败'}")

    if not login_ok:
        print("\n登录失败，脚本终止。")
        return

    records = fetch_all_data(session)
    print(f"\n总共获取记录数: {len(records)}")

    if not records:
        print("未获取到任何数据")
        return

    csv_path = filter_and_save(records)

    filtered_count = 0
    for r in records:
        cost = parse_cost(get_field_value(r, "stat_cost", "消耗", "cost"))
        if cost > 2000:
            filtered_count += 1

    print("\n" + "=" * 60)
    print("汇总报告")
    print("=" * 60)
    print(f"登录状态: {'成功' if login_ok else '失败'}")
    print(f"获取记录总数: {len(records)}")
    print(f"消耗 > 2000 的记录数: {filtered_count}")
    print(f"CSV 文件路径: {csv_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()