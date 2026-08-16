#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星广报表抖音商城消耗统计脚本
功能：提取、筛选、计算消耗，生成CSV，发送飞书消息
"""

import json
import csv
import re
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/workspace")


def extract_table_data(snapshot_text):
    """
    a. 从页面快照文本中解析所有表格行
    兼容两种格式：
    1. 浏览器snapshot原生格式：含 "- role: cell" 和 "name: XXX" 行
    2. 兼容格式：每行11列，用制表符或|分隔的文本（预解析后格式）
    返回: list of dict，每个dict包含一行数据（11个字段）
    """
    records = []

    # --- 格式1: 浏览器snapshot原生格式 ---
    if "- role: cell" in snapshot_text:
        lines = snapshot_text.split('\n')
        cells = []
        for line in lines:
            if '- role: cell' in line:
                match = re.search(r'name: (.+)$', line)
                if match:
                    cells.append(match.group(1))

        row_size = 11
        # 查找第一个数据行起始：跳过"汇总"行（如果存在）
        start_idx = 0
        # 汇总行特征：第0个cell是"汇总"
        if len(cells) >= row_size and cells[0] == '汇总':
            start_idx = row_size  # 跳过汇总行

        i = start_idx
        while i + row_size <= len(cells):
            row = cells[i:i + row_size]
            record = _build_record(row)
            if record:
                records.append(record)
            i += row_size

        return records

    # --- 格式2: 预解析文本（每行JSON或制表符分隔）---
    # 尝试按行解析JSON
    for line in snapshot_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('{') and line.endswith('}'):
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and '产品名称' in obj:
                    records.append(obj)
                    continue
            except:
                pass
        if line.startswith('[') and line.endswith(']'):
            try:
                obj = json.loads(line)
                if isinstance(obj, list) and len(obj) == 11:
                    record = _build_record(obj)
                    if record:
                        records.append(record)
                    continue
            except:
                pass
        # 按制表符或|分隔
        parts = re.split(r'\t|\|', line)
        if len(parts) == 11:
            record = _build_record(parts)
            if record:
                records.append(record)

    return records


def _build_record(row):
    """从11个元素的列表构建record dict，跳过汇总行"""
    if len(row) != 11:
        return None
    row = [str(x).strip() for x in row]
    # 跳过汇总行
    if row[0] == '汇总':
        return None
    # 跳过空行（素材ID为空且其他字段大多为空）
    if not row[0] and sum(1 for x in row if x) <= 2:
        return None
    return {
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


def _parse_cost(cost_str):
    """解析消耗字段为浮点数"""
    try:
        s = str(cost_str).replace(',', '').replace('¥', '').strip()
        return float(s) if s else 0.0
    except:
        return 0.0


def filter_mall_records(records):
    """
    b. 筛选「产品名称」包含"抖音商城"的记录
    同时也检查「下单账户名称」包含"抖音商城"（兼容历史数据）
    """
    mall_records = []
    for r in records:
        product_name = str(r.get('产品名称', ''))
        account_name = str(r.get('下单账户名称', ''))
        if '抖音商城' in product_name or '抖音商城' in account_name:
            mall_records.append(r)
    return mall_records


def calc_total_cost(mall_records):
    """
    d. 计算抖音商城总消耗
    """
    total = 0.0
    for r in mall_records:
        total += _parse_cost(r.get('消耗', '0'))
    return round(total, 2)


def filter_cost_over(records, threshold):
    """
    e. 筛选消耗 > threshold 的记录
    """
    result = []
    for r in records:
        cost = _parse_cost(r.get('消耗', '0'))
        if cost > threshold:
            # 附加解析后的数值，便于排序和显示
            r['_消耗值'] = cost
            result.append(r)
    # 按消耗降序排序
    result.sort(key=lambda x: x['_消耗值'], reverse=True)
    return result


def save_csv(records, filename_without_ext):
    """
    f. 保存CSV到/workspace
    返回文件绝对路径
    """
    if not filename_without_ext.lower().endswith('.csv'):
        filename = filename_without_ext + '.csv'
    else:
        filename = filename_without_ext

    filepath = WORKSPACE / filename

    fields = ['抖音号昵称', '标题', '消耗', '视频播放链接', '产品名称', '下单账户名称', '数据统计日期',
              '素材ID（巨量）', '星图任务ID', '星图任务名称', '抖音号']

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for r in records:
            row = {}
            for k in fields:
                v = r.get(k, '')
                if isinstance(v, str):
                    v = v.strip()
                row[k] = v
            writer.writerow(row)

    return str(filepath)


def build_markdown_message(over_threshold_records, mall_total_cost):
    """
    g. 构造飞书markdown消息
    要求：
    - 标题：## 【消耗预警】星广报表抖音商城消耗统计
    - 顶部注明统计时间
    - 表格列：抖音号昵称 | 标题 | 消耗 | 视频链接([观看](URL)) | 日期
    - 末尾两行：共N条记录消耗超过2000元；抖音商城总消耗：XXXXX元
    """
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []
    lines.append(f"**统计时间：{now_str}**")
    lines.append("")
    lines.append("## 【消耗预警】星广报表抖音商城消耗统计")
    lines.append("")

    # markdown表格
    lines.append("| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
    lines.append("| --- | --- | --- | --- | --- |")

    for r in over_threshold_records:
        nickname = _escape_md(r.get('抖音号昵称', ''))
        title = _escape_md(r.get('标题', ''))
        if len(title) > 30:
            title = title[:27] + '...'
        cost_val = _parse_cost(r.get('消耗', '0'))
        cost_str = f"{cost_val:,.2f}"
        url = str(r.get('视频播放链接', '')).strip()
        link_md = f"[观看]({url})" if url else '-'
        date = _escape_md(r.get('数据统计日期', ''))
        lines.append(f"| {nickname} | {title} | {cost_str} | {link_md} | {date} |")

    lines.append("")
    n = len(over_threshold_records)
    lines.append(f"> 共 **{n}** 条记录消耗超过2000元")
    lines.append(f"> 抖音商城总消耗：**{mall_total_cost:,.2f}** 元")

    return "\n".join(lines)


def _escape_md(s):
    s = str(s) if s is not None else ''
    # 转义管道符和换行
    s = s.replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')
    return s.strip()


def send_lark_message(md_content):
    """
    h. 发送飞书消息到群 oc_74cf357efbbda7b35af5078abcb29bdb
    使用 lark-cli im message 发送交互卡片/markdown
    返回 (success: bool, info: str)
    """
    chat_id = "oc_74cf357efbbda7b35af5078abcb29bdb"
    # 若环境变量覆盖则使用环境变量（便于测试）
    chat_id = os.environ.get("LARK_REPORT_CHAT_ID", chat_id)

    try:
        # 使用lark-cli发送markdown到群
        # lark-cli im +messages-send --chat-id <id> --markdown "内容"
        cmd = [
            "lark-cli", "im", "+messages-send",
            "--chat-id", chat_id,
            "--markdown", md_content
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, cwd=str(WORKSPACE)
        )
        if result.returncode == 0:
            return True, f"发送成功(rc=0): {_truncate(result.stdout or result.stderr, 200)}"
        else:
            return False, f"lark-cli失败(rc={result.returncode}): stderr={_truncate(result.stderr, 500)} stdout={_truncate(result.stdout, 500)}"
    except FileNotFoundError:
        return False, "lark-cli not found"
    except subprocess.TimeoutExpired:
        return False, "lark-cli调用超时"
    except Exception as e:
        return False, f"send_lark_message异常: {repr(e)}"


def _truncate(s, n):
    s = (s or '').strip()
    return s if len(s) <= n else s[:n] + '...'


def snapshot_text_from_pages_json(pages_data):
    """
    辅助：将采集到的结构化JSON pages数组转换成snapshot_text
    pages_data: list of dict，每个dict含 "r":[[{t,h},...], ...] (每行11个cell)
    返回符合 extract_table_data 解析格式的字符串
    """
    rows_text = []
    for page in pages_data:
        page_rows = page.get('r', [])
        for row_cells in page_rows:
            # row_cells: list of {t: text, h: href}
            texts = []
            for i, cell in enumerate(row_cells):
                if isinstance(cell, dict):
                    t = str(cell.get('t', '')).strip()
                    # 对视频播放链接列(index=6)，保留href作为文本
                    if i == 6:
                        h = str(cell.get('h', '')).strip()
                        texts.append(h if h else t)
                    else:
                        texts.append(t)
                else:
                    texts.append(str(cell).strip() if cell else '')
            # 仅在长度11时输出
            if len(texts) == 11:
                rows_text.append(json.dumps(texts, ensure_ascii=False))
    return '\n'.join(rows_text)


def main():
    """
    主流程：
    1. 读取 /workspace/star_report_pages.json (采集的页面JSON)
       或读取 /workspace/star_report_snapshot.txt (快照文本)
    2. a. extract_table_data(snapshot_text)
    3. b. filter_mall_records
    4. c. 空或总消耗<=0则直接结束
    5. d. calc_total_cost
    6. e. filter_cost_over(..., 2000)
    7. f. save_csv
    8. g. build_markdown_message
    9. h. send_lark_message
    """

    pages_json_path = WORKSPACE / "star_report_pages.json"
    snapshot_txt_path = WORKSPACE / "star_report_snapshot.txt"

    snapshot_text = ""

    if pages_json_path.exists():
        try:
            with open(pages_json_path, 'r', encoding='utf-8') as f:
                pages_data = json.load(f)
            snapshot_text = snapshot_text_from_pages_json(pages_data)
            print(f"[INFO] 从 {pages_json_path.name} 加载 {len(pages_data)} 页数据")
        except Exception as e:
            print(f"[WARN] 读取 pages json失败: {e}")

    if not snapshot_text and snapshot_txt_path.exists():
        with open(snapshot_txt_path, 'r', encoding='utf-8') as f:
            snapshot_text = f.read()
        print(f"[INFO] 从 {snapshot_txt_path.name} 加载快照文本")

    if not snapshot_text:
        print("[ERROR] 未找到可用的快照数据 (star_report_pages.json 或 star_report_snapshot.txt)")
        sys.exit(1)

    # a. 解析
    all_records = extract_table_data(snapshot_text)
    print(f"[a] extract_table_data: 解析到 {len(all_records)} 条记录")

    # b. 筛选抖音商城
    mall_records = filter_mall_records(all_records)
    print(f"[b] filter_mall_records: 抖音商城记录 {len(mall_records)} 条")

    # c. 检查是否需要继续
    mall_total = calc_total_cost(mall_records)
    if not mall_records or mall_total <= 0:
        print(f"[c] 商城记录为空或总消耗<=0 (records={len(mall_records)}, total={mall_total})，不发送消息，结束")
        return

    # d. 总消耗
    mall_total_cost = calc_total_cost(mall_records)
    print(f"[d] calc_total_cost: 抖音商城总消耗 = {mall_total_cost:,.2f} 元")

    # e. 筛选>2000
    over_threshold = filter_cost_over(mall_records, 2000)
    print(f"[e] filter_cost_over(>2000): {len(over_threshold)} 条")

    # f. 保存CSV
    csv_path = save_csv(over_threshold, "mall_cost_over_2000")
    print(f"[f] save_csv: 已保存到 {csv_path}")

    # g. 构造markdown
    md_msg = build_markdown_message(over_threshold, mall_total_cost)
    print("[g] build_markdown_message 完成")
    print("--- 消息预览 ---")
    print(md_msg)
    print("--- 结束预览 ---")

    # 保存消息内容到文件，便于debug或Skill发送
    md_path = WORKSPACE / "mall_message.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_msg)
    print(f"[DEBUG] markdown已保存到 {md_path}")

    # h. 发送飞书
    ok, info = send_lark_message(md_msg)
    print(f"[h] send_lark_message: success={ok}, info={info}")

    # 输出结果摘要（便于调用方读取）
    summary = {
        "over_threshold_count": len(over_threshold),
        "mall_total_cost": mall_total_cost,
        "lark_send_success": ok,
        "lark_send_info": info,
        "csv_path": csv_path,
        "md_path": str(md_path),
    }
    summary_path = WORKSPACE / "summary_result.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n[SUMMARY] {json.dumps(summary, ensure_ascii=False)}")


if __name__ == '__main__':
    main()
