#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星广报表抖音商城消耗统计处理脚本
"""

import re
import csv
import json
import os
import sys
from datetime import datetime
import urllib.request
import urllib.parse

# ========== 飞书配置 ==========
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_CHAT_ID = "oc_74cf357efbbda7b35af5078abcb29bdb"

# 表头列索引（根据页面实际列顺序，数据行中"产品名称"列为空，仅显示10列）
HEADERS_DISPLAYED = [
    "素材ID（巨量）", "标题", "星图任务ID", "星图任务名称",
    "抖音号昵称", "抖音号", "视频播放链接", "下单账户名称",
    "消耗", "数据统计日期"
]
# 完整逻辑列（产品名称补空）
HEADERS = HEADERS_DISPLAYED[:9] + ["产品名称", "数据统计日期"]

def extract_table_data(snapshot_text):
    """
    从页面快照文本中解析所有表格行数据
    每行10个cell（产品名称列为空不显示）
    """
    records = []
    
    lines = snapshot_text.split('\n')
    cells = []
    
    for line in lines:
        m = re.search(r'role:\s*cell\s+name:\s*(.+?)\s+ref:', line)
        if m:
            val = m.group(1).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            cells.append(val)
    
    # 每页有汇总行（3个cell: 汇总, 总消耗, 日期），但后面的页没有
    # 策略：检测每10个cell为一条记录。但首先跳过开头的"汇总"行（如果存在）
    col_count = len(HEADERS_DISPLAYED)  # 10
    
    # 去掉汇总行（前3个cell为：汇总 + 金额 + 日期）
    clean_cells = []
    i = 0
    while i < len(cells):
        # 检测是否是汇总行模式：开头是"汇总"
        if cells[i] == '汇总' and i + 2 < len(cells):
            # 跳过3个
            i += 3
            continue
        clean_cells.append(cells[i])
        i += 1
    
    # 每10个为一条记录
    for idx in range(0, len(clean_cells), col_count):
        row = clean_cells[idx:idx + col_count]
        if len(row) == col_count:
            record = {
                "素材ID（巨量）": row[0],
                "标题": row[1],
                "星图任务ID": row[2],
                "星图任务名称": row[3],
                "抖音号昵称": row[4],
                "抖音号": row[5],
                "视频播放链接": row[6],
                "下单账户名称": row[7],
                "消耗": row[8],
                "产品名称": "",  # 数据行中产品名称列无cell
                "数据统计日期": row[9]
            }
            records.append(record)
    
    return records


def filter_mall_records(records):
    """筛选「产品名称」或「标题」包含"抖音商城"的记录"""
    mall_records = []
    for r in records:
        product_name = r.get("产品名称", "")
        title = r.get("标题", "")
        task_name = r.get("星图任务名称", "")
        if "抖音商城" in product_name or "抖音商城" in title or "抖音商城" in task_name:
            mall_records.append(r)
    return mall_records


def calc_total_cost(mall_records):
    """计算商城总消耗"""
    total = 0.0
    for r in mall_records:
        try:
            cost = float(r.get("消耗", "0").replace(",", ""))
            total += cost
        except (ValueError, TypeError):
            pass
    return round(total, 2)


def filter_cost_over(records, threshold):
    """筛选消耗超过阈值的记录"""
    result = []
    for r in records:
        try:
            cost = float(r.get("消耗", "0").replace(",", ""))
            if cost > threshold:
                result.append(r)
        except (ValueError, TypeError):
            pass
    # 按消耗降序排列
    result.sort(key=lambda x: float(x.get("消耗", "0").replace(",", "")), reverse=True)
    return result


def save_csv(records, filename_prefix):
    """保存CSV到/workspace目录"""
    if not records:
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"/workspace/{filename_prefix}_{timestamp}.csv"
    
    csv_headers = ["抖音号昵称", "标题", "消耗", "视频播放链接", "数据统计日期", "产品名称", "星图任务名称"]
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers, extrasaction='ignore')
        writer.writeheader()
        for r in records:
            writer.writerow({
                "抖音号昵称": r.get("抖音号昵称", ""),
                "标题": r.get("标题", ""),
                "消耗": r.get("消耗", ""),
                "视频播放链接": r.get("视频播放链接", ""),
                "数据统计日期": r.get("数据统计日期", ""),
                "产品名称": r.get("产品名称", ""),
                "星图任务名称": r.get("星图任务名称", "")
            })
    
    print(f"CSV已保存: {filepath}")
    return filepath


def build_markdown_message(over_threshold_records, mall_total_cost):
    """构造飞书markdown消息"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = []
    lines.append(f"统计时间：{now}")
    lines.append("")
    lines.append("## 【消耗预警】星广报表抖音商城消耗统计")
    lines.append("")
    
    if over_threshold_records:
        # Markdown表格
        lines.append("| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
        lines.append("| --- | --- | --- | --- | --- |")
        
        for r in over_threshold_records:
            nickname = r.get("抖音号昵称", "").replace("|", "\\|")
            title = r.get("标题", "").replace("|", "\\|")[:50]  # 限制长度
            cost = r.get("消耗", "0")
            video_url = r.get("视频播放链接", "").strip('"')
            date = r.get("数据统计日期", "")
            
            link_md = f"[观看]({video_url})" if video_url else ""
            lines.append(f"| {nickname} | {title} | {cost} | {link_md} | {date} |")
        
        lines.append("")
    
    lines.append(f"共{len(over_threshold_records)}条记录消耗超过2000元；抖音商城总消耗：{mall_total_cost}元")
    
    return "\n".join(lines)


def get_feishu_token():
    """获取飞书tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("code") == 0:
                return result.get("tenant_access_token")
    except Exception as e:
        print(f"获取飞书Token失败: {e}", file=sys.stderr)
    return None


def send_lark_message(md_content):
    """发送飞书消息到指定群组"""
    token = get_feishu_token()
    if not token:
        print("警告: 无法获取飞书Token，跳过消息发送", file=sys.stderr)
        return False
    
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    
    # 飞书富文本消息格式
    content = {
        "zh_cn": {
            "title": "【消耗预警】星广报表抖音商城消耗统计",
            "content": [
                [{
                    "tag": "text",
                    "text": md_content
                }]
            ]
        }
    }
    
    body = json.dumps({
        "receive_id": FEISHU_CHAT_ID,
        "msg_type": "interactive",
        "content": json.dumps({
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "【消耗预警】星广报表抖音商城消耗统计"},
                "template": "red"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": md_content
                }
            ]
        })
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}"
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("code") == 0:
                print("飞书消息发送成功")
                return True
            else:
                print(f"飞书消息发送失败: {result.get('msg')}", file=sys.stderr)
                return False
    except Exception as e:
        print(f"飞书消息发送异常: {e}", file=sys.stderr)
        return False


def main():
    """主函数"""
    # 读取快照数据文件
    snapshot_file = "/workspace/snapshot_all_pages.txt"
    if not os.path.exists(snapshot_file):
        print(f"错误: 快照文件不存在: {snapshot_file}", file=sys.stderr)
        sys.exit(1)
    
    with open(snapshot_file, 'r', encoding='utf-8') as f:
        snapshot_text = f.read()
    
    print(f"快照文件大小: {len(snapshot_text)} 字符")
    
    # a. 解析所有行
    records = extract_table_data(snapshot_text)
    print(f"解析到记录数: {len(records)}")
    
    # b. 筛选抖音商城记录
    mall_records = filter_mall_records(records)
    print(f"抖音商城记录数: {len(mall_records)}")
    
    # c. 若商城记录为空或总消耗<=0，直接结束不发消息
    mall_total_cost = calc_total_cost(mall_records)
    print(f"抖音商城总消耗: {mall_total_cost} 元")
    
    if len(mall_records) == 0 or mall_total_cost <= 0:
        print("商城记录为空或总消耗<=0，直接结束")
        return
    
    # e. 筛选消耗>2000明细
    over_threshold_records = filter_cost_over(mall_records, 2000)
    print(f"消耗>2000记录数: {len(over_threshold_records)}")
    
    # f. 保存CSV
    csv_path = save_csv(over_threshold_records, "mall_cost_over_2000")
    
    # g. 构造markdown消息
    md_content = build_markdown_message(over_threshold_records, mall_total_cost)
    print("消息内容预览:")
    print("-" * 50)
    print(md_content)
    print("-" * 50)
    
    # h. 发送飞书消息
    send_status = send_lark_message(md_content)
    
    # 输出结果摘要（供后续读取）
    result_summary = {
        "over_threshold_count": len(over_threshold_records),
        "mall_total_cost": mall_total_cost,
        "send_status": "成功" if send_status else "失败",
        "csv_path": csv_path,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("/workspace/result_summary.json", 'w', encoding='utf-8') as f:
        json.dump(result_summary, f, ensure_ascii=False, indent=2)
    
    print("\n===== 执行结果 =====")
    print(f"超2000记录数: {len(over_threshold_records)}")
    print(f"商城总消耗: {mall_total_cost} 元")
    print(f"飞书发送状态: {'成功' if send_status else '失败'}")


if __name__ == "__main__":
    main()
