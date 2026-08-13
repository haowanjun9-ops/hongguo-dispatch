#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鲸准3.0星广报表数据提取脚本
- 合并 raw_pages_batch1.json 和 raw_pages_batch2*.json
- 筛选「产品名称」或「下单账户名称」包含"抖音商城"的记录
- 计算商城总消耗、筛选>2000的明细
- 保存CSV、构造markdown、发送飞书消息
"""

import json
import csv
import re
import os
import glob
from datetime import datetime
from pathlib import Path

COL_KEYS = [
    '素材ID（巨量）',
    '标题',
    '星图任务ID',
    '星图任务名称',
    '抖音号昵称',
    '抖音号',
    '视频播放链接',
    '下单账户名称',
    '消耗',
    '产品名称',
    '数据统计日期',
]


def load_and_merge_pages(patterns):
    """读取所有匹配的 pages JSON 文件，合并，按page号去重（保留首次出现）"""
    seen_pages = set()
    all_pages = []
    for pat in patterns:
        for fp in sorted(glob.glob(pat)):
            with open(fp, 'r', encoding='utf-8') as f:
                pages = json.load(f)
            for p in pages:
                pg = p.get('page', 0)
                if pg in seen_pages:
                    continue
                seen_pages.add(pg)
                all_pages.append(p)
    return all_pages


def pages_to_records(pages):
    """把 pages[{rows:[[cell,...]]}] 转换为 records[dict]"""
    records = []
    for p in pages:
        for row in p.get('rows', []):
            if len(row) < len(COL_KEYS):
                row = row + [''] * (len(COL_KEYS) - len(row))
            rec = dict(zip(COL_KEYS, row[:len(COL_KEYS)]))
            records.append(rec)
    return records


def extract_table_data(snapshot_data):
    """兼容原逻辑：从 snapshot 文本中提取（目前用 pages 方式，保留备用）"""
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
        row = cells[i:i+row_size]
        if len(row) == row_size:
            records.append(dict(zip(COL_KEYS, row)))
        i += row_size
    return records


def parse_cost(cost_str):
    try:
        return float(str(cost_str).replace(',', '').strip())
    except Exception:
        return 0.0


def filter_mall_records(records):
    """筛选产品名称或下单账户名称包含"抖音商城"的记录"""
    result = []
    for r in records:
        prod = str(r.get('产品名称', ''))
        acct = str(r.get('下单账户名称', ''))
        if '抖音商城' in prod or '抖音商城' in acct:
            result.append(r)
    return result


def calc_total_cost(records):
    return sum(parse_cost(r.get('消耗', '0')) for r in records)


def filter_cost_over(records, threshold):
    return [r for r in records if parse_cost(r.get('消耗', '0')) > threshold]


def save_csv(records, name_prefix):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = f'/workspace/{name_prefix}_{ts}.csv'
    if not records:
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(COL_KEYS)
        return path
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COL_KEYS)
        w.writeheader()
        for r in records:
            w.writerow({k: r.get(k, '') for k in COL_KEYS})
    return path


def build_markdown_message(over_threshold, mall_total_cost):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []
    lines.append(f'统计时间：{now}')
    lines.append('')
    lines.append('## 【消耗预警】星广报表抖音商城消耗统计')
    lines.append('')
    lines.append('| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |')
    lines.append('| --- | --- | --- | --- | --- |')
    for r in over_threshold:
        nick = str(r.get('抖音号昵称', '')).replace('|', '\\|')
        title = str(r.get('标题', '')).replace('|', '\\|')
        cost = parse_cost(r.get('消耗', '0'))
        link = str(r.get('视频播放链接', '')).strip()
        date = str(r.get('数据统计日期', ''))
        link_md = f'[观看]({link})' if link else ''
        lines.append(f'| {nick} | {title} | {cost:.2f} | {link_md} | {date} |')
    lines.append('')
    n = len(over_threshold)
    lines.append(f'共{n}条记录消耗超过2000元；抖音商城总消耗：{mall_total_cost:.2f}元')
    return '\n'.join(lines)


def send_lark_message(md_content, chat_id='oc_74cf357efbbda7b35af5078abcb29bdb'):
    """调用 lark-cli 发送飞书消息。若失败则抛出异常。"""
    import subprocess
    import tempfile
    # 写入临时 markdown 文件后发送
    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as tf:
        tf.write(md_content)
        tmp_path = tf.name
    try:
        cmd = [
            'lark-cli', 'im', 'message', 'send',
            '--chat-id', chat_id,
            '--msg-type', 'interactive',
            '--input-file', tmp_path,
        ]
        # 没有 lark-cli 也可以用通用 skill，这里优先用 lark-cli；若不存在则抛出
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            stderr = (result.stderr or '') + (result.stdout or '')
            raise RuntimeError(f'lark-cli failed: {stderr[:800]}')
        return {'status': 'ok', 'raw': result.stdout[:500]}
    except FileNotFoundError:
        # fallback to Skill: send via Feishu IM
        raise RuntimeError('lark-cli not found')
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def send_lark_message_via_skill(md_content, chat_id='oc_74cf357efbbda7b35af5078abcb29bdb'):
    """备用：当 lark-cli 不可用时，返回内容由外部 skill 发送。返回 False 提示用外部方式。"""
    return False


def main():
    print('合并 pages 数据文件...')
    pages = load_and_merge_pages([
        '/workspace/raw_pages_batch1.json',
        '/workspace/raw_pages_batch2*.json',
    ])
    page_nums = sorted([p.get('page', 0) for p in pages])
    print(f'共加载 {len(pages)} 页数据, 页号范围: min={page_nums[0] if page_nums else 0}, max={page_nums[-1] if page_nums else 0}')

    records = pages_to_records(pages)
    print(f'解析出 {len(records)} 条记录')

    mall_records = filter_mall_records(records)
    print(f'抖音商城相关记录: {len(mall_records)} 条')
    if not mall_records:
        print('无商城记录，结束')
        return
    mall_total_cost = calc_total_cost(mall_records)
    print(f'抖音商城总消耗: {mall_total_cost:.2f} 元')
    if mall_total_cost <= 0:
        print('商城总消耗<=0，结束不发消息')
        return

    over_threshold = filter_cost_over(mall_records, 2000)
    print(f'消耗超过2000的记录: {len(over_threshold)} 条')

    csv_path = save_csv(over_threshold, 'mall_cost_over_2000')
    print(f'CSV已保存: {csv_path}')

    md = build_markdown_message(over_threshold, mall_total_cost)
    md_path = f'/workspace/lark_message_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f'Markdown消息已保存: {md_path}')

    # 打印发送结果摘要，外部发送方式负责实际发送
    summary = {
        'over_threshold_count': len(over_threshold),
        'mall_total_cost': round(mall_total_cost, 2),
        'csv_path': csv_path,
        'md_path': md_path,
    }
    with open('/workspace/result_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print('RESULT_SUMMARY_JSON:', json.dumps(summary, ensure_ascii=False))

    # 尝试发送飞书消息
    lark_status = 'skipped'
    try:
        res = send_lark_message(md)
        if res and res.get('status') == 'ok':
            lark_status = 'sent'
            print('飞书消息发送成功')
        else:
            lark_status = 'failed_unknown'
            print('飞书消息发送失败(未知)')
    except Exception as e:
        lark_status = 'failed: ' + str(e)[:200]
        print(f'飞书消息发送异常: {e}')

    summary['lark_status'] = lark_status
    with open('/workspace/result_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print('FINAL_SUMMARY:', json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
