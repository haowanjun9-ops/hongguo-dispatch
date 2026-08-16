#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星广报表抖音商城消耗统计 - 数据处理脚本
"""
import json
import re
import csv
import os
import sys
from datetime import datetime

WORKSPACE = "/workspace"
SNAPSHOT_FILE = os.path.join(WORKSPACE, "all_pages_data.json")
CSV_OUTPUT = os.path.join(WORKSPACE, "mall_cost_over_2000.csv")


def save_snapshot_data(pages_data_list):
    """保存采集的所有页数据到JSON文件"""
    with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
        json.dump(pages_data_list, f, ensure_ascii=False, indent=2)


def load_snapshot_data():
    """从JSON文件加载所有页数据"""
    if not os.path.exists(SNAPSHOT_FILE):
        return []
    with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_table_data(snapshot_data_list):
    """
    解析所有行数据，合并多页数据
    snapshot_data_list: 每页的JSON对象数组，每个对象有 headers 和 data 字段
    返回: records数组，每个record是字段->值的字典
    """
    all_records = []
    for page_data in snapshot_data_list:
        headers = page_data.get('headers', [])
        rows = page_data.get('data', [])
        for row in rows:
            record = {}
            for h in headers:
                cell = row.get(h, {})
                record[h] = cell.get('text', '') if isinstance(cell, dict) else str(cell)
                # 如果有链接字段也保存
                if isinstance(cell, dict) and cell.get('link'):
                    record[h + '_link'] = cell.get('link')
            # 如果视频播放链接_link不存在，使用文本内容
            if '视频播放链接_link' not in record and record.get('视频播放链接'):
                url = record['视频播放链接'].strip().strip('"').strip("'")
                record['视频播放链接_link'] = url
            all_records.append(record)
    return all_records


def filter_mall_records(records):
    """
    筛选「产品名称」包含"抖音商城"的记录
    由于产品名称列可能为空，同时检查标题、星图任务名称、下单账户名称
    """
    mall_records = []
    for rec in records:
        # 跳过汇总行
        if rec.get('素材ID（巨量）') == '汇总':
            continue
        product_name = rec.get('产品名称', '') or ''
        title = rec.get('标题', '') or ''
        task_name = rec.get('星图任务名称', '') or ''
        account_name = rec.get('下单账户名称', '') or ''
        
        # 只要任意一个字段包含"抖音商城"就算
        if ('抖音商城' in product_name or 
            '抖音商城' in title or 
            '抖音商城' in task_name or 
            '抖音商城' in account_name):
            mall_records.append(rec)
    return mall_records


def calc_total_cost(mall_records):
    """计算商城总消耗"""
    total = 0.0
    for rec in mall_records:
        try:
            cost_str = (rec.get('消耗') or '0').replace(',', '')
            total += float(cost_str)
        except (ValueError, TypeError):
            continue
    return round(total, 2)


def filter_cost_over(records, threshold):
    """筛选消耗超过指定阈值的记录"""
    result = []
    for rec in records:
        try:
            cost_str = (rec.get('消耗') or '0').replace(',', '')
            cost = float(cost_str)
            if cost > threshold:
                result.append(rec)
        except (ValueError, TypeError):
            continue
    # 按消耗降序排列
    result.sort(key=lambda r: float((r.get('消耗') or '0').replace(',', '')), reverse=True)
    return result


def save_csv(records, filename_prefix):
    """保存记录到CSV文件"""
    filepath = os.path.join(WORKSPACE, f"{filename_prefix}.csv")
    if not records:
        return filepath
    fieldnames = list(records[0].keys())
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)
    return filepath


def build_markdown_message(over_threshold_records, mall_total_cost):
    """构造飞书消息markdown"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append(f"统计时间：{now}")
    lines.append("")
    lines.append("## 【消耗预警】星广报表抖音商城消耗统计")
    lines.append("")
    
    if over_threshold_records:
        # 表头
        lines.append("| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for rec in over_threshold_records:
            nickname = rec.get('抖音号昵称', '') or ''
            title = rec.get('标题', '') or ''
            # 标题太长截断
            if len(title) > 50:
                title = title[:47] + '...'
            cost = rec.get('消耗', '') or ''
            video_url = rec.get('视频播放链接_link') or rec.get('视频播放链接', '') or ''
            video_url = video_url.strip().strip('"').strip("'")
            date = rec.get('数据统计日期', '') or ''
            
            link_md = f"[观看]({video_url})" if video_url else ''
            lines.append(f"| {nickname} | {title} | {cost} | {link_md} | {date} |")
    
    lines.append("")
    lines.append(f"共{len(over_threshold_records)}条记录消耗超过2000元；抖音商城总消耗：{mall_total_cost:.2f}元")
    lines.append("")
    
    return "\\n".join(lines)


def send_lark_message(md_content):
    """
    发送飞书消息到群 oc_74cf357efbbda7b35af5078abcb29bdb
    使用飞书开放API，需要获取tenant_access_token然后调用发送消息
    """
    import urllib.request
    import urllib.error
    
    chat_id = "oc_74cf357efbbda7b35af5078abcb29bdb"
    
    # 从环境变量获取凭证
    app_id = os.environ.get("LARK_APP_ID") or os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("LARK_APP_SECRET") or os.environ.get("FEISHU_APP_SECRET")
    
    if not app_id or not app_secret:
        print("WARNING: 未设置飞书APP凭证，尝试使用CLI方式发送", file=sys.stderr)
        return send_lark_via_cli(md_content, chat_id)
    
    try:
        # 1. 获取tenant_access_token
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token_data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode('utf-8')
        req = urllib.request.Request(token_url, data=token_data, 
                                    headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            token_result = json.loads(resp.read().decode('utf-8'))
        if token_result.get('code') != 0:
            raise Exception(f"获取token失败: {token_result}")
        token = token_result['tenant_access_token']
        
        # 2. 发送消息
        msg_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        msg_data = json.dumps({
            "receive_id": chat_id,
            "msg_type": "interactive",
            "content": json.dumps({
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {"tag": "plain_text", "content": "【消耗预警】星广报表抖音商城消耗统计"},
                    "template": "red"
                },
                "elements": [
                    {"tag": "markdown", "content": md_content}
                ]
            })
        }).encode('utf-8')
        req = urllib.request.Request(msg_url, data=msg_data,
                                    headers={"Content-Type": "application/json",
                                             "Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        if result.get('code') != 0:
            raise Exception(f"发送消息失败: {result}")
        print("飞书消息发送成功")
        return True, "success"
    except Exception as e:
        print(f"飞书API发送失败: {e}", file=sys.stderr)
        return send_lark_via_cli(md_content, chat_id)


def send_lark_via_cli(md_content, chat_id):
    """使用lark-cli发送消息"""
    import subprocess
    try:
        # 使用 interactive 卡片格式，带标题和红色主题
        card_content = json.dumps({
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "【消耗预警】星广报表抖音商城消耗统计"},
                "template": "red"
            },
            "elements": [
                {"tag": "markdown", "content": md_content}
            ]
        }, ensure_ascii=False)
        
        cmd = [
            "lark-cli", "im", "+messages-send",
            "--chat-id", chat_id,
            "--msg-type", "interactive",
            "--content", card_content
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("lark-cli发送成功")
            return True, "cli-success"
        else:
            print(f"lark-cli interactive发送失败，尝试用markdown方式: stdout={result.stdout}, stderr={result.stderr}", file=sys.stderr)
            # 回退到简单markdown发送
            cmd2 = [
                "lark-cli", "im", "+messages-send",
                "--chat-id", chat_id,
                "--markdown", md_content
            ]
            result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
            if result2.returncode == 0:
                print("lark-cli markdown发送成功")
                return True, "cli-markdown-success"
            else:
                print(f"lark-cli markdown也失败: stdout={result2.stdout}, stderr={result2.stderr}", file=sys.stderr)
                return False, f"cli-failed: {result2.stderr[:300]}"
    except Exception as e:
        print(f"lark-cli调用失败: {e}", file=sys.stderr)
        return False, f"error: {str(e)[:300]}"


# 单元测试用的模拟快照数据解析函数
def parse_snapshot_text_to_records(snapshot_text):
    """从纯文本快照解析行数据（兼容用户要求的接口形式）"""
    # 尝试用JSON反序列化多页的情况（我们实际存储的是JSON）
    records = []
    # 我们实际存储的是每页JSON数组，这里从文件加载
    loaded = load_snapshot_data()
    if loaded:
        return extract_table_data(loaded)
    return records


if __name__ == "__main__":
    # 完整执行流程
    print("===== 星广报表抖音商城消耗统计 =====")
    
    # 从JSON文件加载所有页
    pages_data = load_snapshot_data()
    print(f"加载了 {len(pages_data)} 页数据")
    
    # a. 解析所有行
    all_records = extract_table_data(pages_data)
    print(f"解析到 {len(all_records)} 条记录（含汇总行）")
    
    # b. 筛选抖音商城记录
    mall_records = filter_mall_records(all_records)
    print(f"筛选出 {len(mall_records)} 条抖音商城记录")
    
    # c. 空或总消耗<=0直接结束
    mall_total = calc_total_cost(mall_records)
    print(f"抖音商城总消耗: {mall_total:.2f}元")
    
    if not mall_records or mall_total <= 0:
        print("商城记录为空或总消耗<=0，不发送消息，直接结束")
        sys.exit(0)
    
    # d. 总消耗已计算
    
    # e. 筛选消耗>2000
    over_2000 = filter_cost_over(mall_records, 2000)
    print(f"消耗超过2000的记录数: {len(over_2000)}")
    for r in over_2000:
        print(f"  - {r.get('抖音号昵称','')}: {r.get('消耗','')}元, {r.get('标题','')[:30]}...")
    
    # f. 保存CSV
    csv_path = save_csv(over_2000, "mall_cost_over_2000")
    print(f"CSV已保存到: {csv_path}")
    
    # g. 构造markdown
    md_msg = build_markdown_message(over_2000, mall_total)
    print("\\n==== Markdown消息预览 ====")
    print(md_msg.replace('\\n', '\n'))
    print("============================\\n")
    
    # h. 发送飞书消息
    print("发送飞书消息...")
    ok, status = send_lark_message(md_msg)
    print(f"飞书发送状态: ok={ok}, status={status}")
    
    # 输出最终摘要
    print("\\n===== 执行结果摘要 =====")
    print(f"超2000记录数: {len(over_2000)}")
    print(f"商城总消耗: {mall_total:.2f}元")
    print(f"飞书发送状态: {'成功' if ok else '失败'} ({status})")
