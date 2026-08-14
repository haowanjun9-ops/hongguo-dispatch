import json
import csv
import os
import requests
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNTQzIiwiZXhwIjoxNzg3OTA0NDc0fQ.EE8ejsv_1WzVlFz1i_uOzs34s0D2IBqe1pX0yYTqRvU"
API_BASE = "https://wxxcx.whaleidea.cn/material-report/"
FEISHU_CHAT_ID = "oc_74cf357efbbda7b35af5078abcb29bdb"
FEISHU_USER_TOKEN = os.environ.get("LARKSUITE_CLI_USER_ACCESS_TOKEN", "")


def fetch_all_data():
    """从API获取所有数据"""
    all_items = []
    page = 1
    page_size = 100

    while True:
        url = f"{API_BASE}?page={page}&page_size={page_size}"
        headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}

        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"  API错误: {resp.status_code} {resp.text[:200]}")
            break

        data = resp.json()
        items = data.get("items", [])
        all_items.extend(items)
        print(f"  第{page}页: 获取{len(items)}条, 累计{len(all_items)}条")

        total = data.get("total", 0)
        if len(all_items) >= total or len(items) == 0:
            break
        page += 1

    return all_items


def extract_table_data(items):
    """从API items解析为统一格式记录"""
    records = []
    for item in items:
        record = {
            "素材ID": item.get("material_id", ""),
            "标题": item.get("video_title", ""),
            "星图任务ID": item.get("star_task_id", ""),
            "星图任务名称": item.get("star_task_name", ""),
            "抖音号昵称": item.get("aweme_name", ""),
            "抖音号": item.get("aweme_id", ""),
            "视频播放链接": item.get("video_play_link", ""),
            "下单账户名称": item.get("product_name", ""),
            "消耗": item.get("stat_cost", "0"),
            "产品名称": item.get("product_name", ""),
            "数据统计日期": item.get("stat_date", ""),
        }
        records.append(record)
    return records


def filter_mall_records(records):
    """筛选包含'抖音商城'的记录"""
    mall_records = []
    for r in records:
        product_name = r.get("产品名称", "")
        account_name = r.get("下单账户名称", "")
        if "抖音商城" in product_name or "抖音商城" in account_name:
            mall_records.append(r)
    return mall_records


def calc_total_cost(mall_records):
    """计算商城总消耗"""
    total = 0.0
    for r in mall_records:
        try:
            cost = float(r.get("消耗", 0))
            total += cost
        except (ValueError, TypeError):
            pass
    return round(total, 2)


def filter_cost_over(records, threshold):
    """筛选消耗超过阈值的记录"""
    result = []
    for r in records:
        try:
            cost = float(r.get("消耗", 0))
            if cost > threshold:
                result.append(r)
        except (ValueError, TypeError):
            pass
    result.sort(key=lambda x: float(x.get("消耗", 0)), reverse=True)
    return result


def save_csv(records, filename):
    """保存CSV"""
    filepath = f"/workspace/{filename}.csv"
    headers = [
        "抖音号昵称", "标题", "消耗", "视频播放链接", "日期",
        "产品名称", "下单账户名称", "素材ID", "星图任务ID", "星图任务名称", "抖音号"
    ]
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            row = {
                "抖音号昵称": r.get("抖音号昵称", ""),
                "标题": r.get("标题", ""),
                "消耗": r.get("消耗", ""),
                "视频播放链接": r.get("视频播放链接", ""),
                "日期": r.get("数据统计日期", ""),
                "产品名称": r.get("产品名称", ""),
                "下单账户名称": r.get("下单账户名称", ""),
                "素材ID": r.get("素材ID", ""),
                "星图任务ID": r.get("星图任务ID", ""),
                "星图任务名称": r.get("星图任务名称", ""),
                "抖音号": r.get("抖音号", ""),
            }
            writer.writerow(row)
    return filepath


def build_markdown_message(over_threshold_records, mall_total_cost):
    """构造飞书markdown消息"""
    now = datetime.now(BJT)
    timestamp = now.strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append("## 【消耗预警】星广报表抖音商城消耗统计")
    lines.append("")
    lines.append(f"统计时间：{timestamp}")
    lines.append("")

    if not over_threshold_records:
        lines.append("暂无消耗超过2000元的记录。")
        lines.append("")
    else:
        lines.append("| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for r in over_threshold_records:
            nickname = r.get("抖音号昵称", "")
            title = r.get("标题", "").replace("|", "\\|")
            cost = r.get("消耗", "")
            url = r.get("视频播放链接", "")
            date = r.get("数据统计日期", "")
            link_text = f"[观看]({url})" if url else ""
            lines.append(f"| {nickname} | {title} | {cost} | {link_text} | {date} |")

    lines.append("")
    lines.append(f"共{len(over_threshold_records)}条记录消耗超过2000元；抖音商城总消耗：{mall_total_cost}元")

    return "\n".join(lines)


def send_lark_message(md_content):
    """发送飞书消息到指定群"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    headers = {
        "Authorization": f"Bearer {FEISHU_USER_TOKEN}",
        "Content-Type": "application/json"
    }

    # Try sending as text first
    payload = {
        "receive_id": FEISHU_CHAT_ID,
        "msg_type": "text",
        "content": json.dumps({"text": md_content})
    }

    try:
        resp = requests.post(url, params=params, headers=headers, json=payload, timeout=10)
        result = resp.json()
        if resp.status_code == 200 and result.get("code") == 0:
            return True, "飞书文本消息发送成功"
        else:
            # Try as post (rich text)
            payload_post = {
                "receive_id": FEISHU_CHAT_ID,
                "msg_type": "post",
                "content": json.dumps({
                    "zh_cn": {
                        "title": "【消耗预警】星广报表抖音商城消耗统计",
                        "content": [[{"tag": "text", "text": md_content}]]
                    }
                })
            }
            resp2 = requests.post(url, params=params, headers=headers, json=payload_post, timeout=10)
            result2 = resp2.json()
            if resp2.status_code == 200 and result2.get("code") == 0:
                return True, "飞书富文本消息发送成功"
            return False, f"飞书返回错误: {result.get('msg', str(result))}"
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 50)
    print("星广报表抖音商城消耗统计")
    print("=" * 50)

    # Step 1: Fetch data from API
    print("\n[1] 从API获取数据...")
    items = fetch_all_data()
    print(f"  获取完成：{len(items)} 条记录")

    if not items:
        print("  无数据，结束")
        return

    # Step 2: Parse records
    print("\n[2] 解析记录...")
    records = extract_table_data(items)
    print(f"  解析完成：{len(records)} 条记录")

    # Step 3: Filter mall records
    print("\n[3] 筛选抖音商城记录...")
    mall_records = filter_mall_records(records)
    print(f"  抖音商城记录：{len(mall_records)} 条")

    if not mall_records:
        print("  无抖音商城记录，结束不发消息")
        return

    # Step 4: Calculate total cost
    print("\n[4] 计算商城总消耗...")
    mall_total_cost = calc_total_cost(mall_records)
    print(f"  抖音商城总消耗：{mall_total_cost} 元")

    if mall_total_cost <= 0:
        print("  总消耗<=0，结束不发消息")
        return

    # Step 5: Filter cost over threshold
    print("\n[5] 筛选消耗>2000的明细...")
    over_threshold_records = filter_cost_over(mall_records, 2000)
    print(f"  消耗>2000的记录：{len(over_threshold_records)} 条")

    # Step 6: Save CSV
    print("\n[6] 保存CSV...")
    csv_path = save_csv(over_threshold_records, "mall_cost_over_2000")
    print(f"  CSV已保存：{csv_path}")

    # Step 7: Build markdown
    print("\n[7] 构造markdown消息...")
    md_content = build_markdown_message(over_threshold_records, mall_total_cost)
    print(f"  消息长度：{len(md_content)} 字符")

    # Step 8: Send Feishu message
    print("\n[8] 发送飞书消息...")
    success, msg = send_lark_message(md_content)
    print(f"  发送结果：{success} - {msg}")

    # Summary
    print("\n" + "=" * 50)
    print("执行摘要：")
    print(f"  筛选出超2000记录数：{len(over_threshold_records)}")
    print(f"  商城总消耗金额：{mall_total_cost} 元")
    print(f"  飞书发送状态：{'成功' if success else '失败'} ({msg})")
    print("=" * 50)


if __name__ == "__main__":
    main()