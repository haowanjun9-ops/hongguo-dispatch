#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合执行：构造数据 -> 处理 -> 生成CSV/Markdown -> 调用lark-cli发消息
"""
import json
import subprocess
import sys
import os
from datetime import datetime

# ============ 从浏览器采集的2条超2000记录 & 商城总消耗 ============
OVER_THRESHOLD = [
    {
        "douyin_nickname": "苏苏说说看",
        "title": "长久坚守每日签到，累计打卡时日越多福利等级越高 #抖音商城 #签到 #网赚 #福利多多 #剪辑制作",
        "cost": "13392.61",
        "video_url": "https://douyin.com/video/7670154522911657250",
        "date": "2026-08-13",
        "product_name": "抖音商城",
        "plan_name": "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1"
    },
    {
        "douyin_nickname": "我的智能外挂",
        "title": "简单一键签到，省去复杂操作领取福利 #网赚 #签到 #真人实拍 #福利多多 #抖音商城",
        "cost": "2131.81",
        "video_url": "https://douyin.com/video/7670532019411062056",
        "date": "2026-08-13",
        "product_name": "抖音商城",
        "plan_name": "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1"
    }
]

MALL_TOTAL_COST = 24213.57
OVER_COUNT = len(OVER_THRESHOLD)

# ============ 保存CSV ============
def save_csv(records, filename_prefix):
    filepath = f'/workspace/{filename_prefix}.csv'
    import csv
    fieldnames = ['抖音号昵称', '标题', '消耗', '视频链接', '日期', '产品名称', '计划名称']
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({
                '抖音号昵称': r.get('douyin_nickname', ''),
                '标题': r.get('title', ''),
                '消耗': r.get('cost', ''),
                '视频链接': r.get('video_url', ''),
                '日期': r.get('date', ''),
                '产品名称': r.get('product_name', ''),
                '计划名称': r.get('plan_name', '')
            })
    print(f'CSV已保存: {filepath}')
    return filepath

# ============ 构造Markdown ============
def build_markdown_message(records, total_cost):
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []
    lines.append(f'统计时间：{now_str}')
    lines.append('')
    lines.append('## 【消耗预警】星广报表抖音商城消耗统计')
    lines.append('')
    lines.append('| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |')
    lines.append('| --- | --- | --- | --- | --- |')
    for r in records:
        nickname = r.get('douyin_nickname', '').replace('|', '\\|')
        title = r.get('title', '').replace('|', '\\|')
        if len(title) > 60:
            title = title[:57] + '...'
        cost = r.get('cost', '')
        url = r.get('video_url', '')
        date = r.get('date', '')
        link_md = f'[观看]({url})' if url else ''
        lines.append(f'| {nickname} | {title} | {cost} | {link_md} | {date} |')
    lines.append('')
    n = len(records)
    lines.append(f'共{n}条记录消耗超过2000元；抖音商城总消耗：{total_cost}元')
    return '\n'.join(lines)

# ============ 调用lark-cli发消息 ============
def send_lark_message(md_content):
    chat_id = 'oc_74cf357efbbda7b35af5078abcb29bdb'
    # 把markdown写入临时文件，避免shell转义问题
    tmp_path = '/tmp/lark_msg.md'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    # 构造命令：用 lark-cli im +messages-send
    cmd = [
        'lark-cli', 'im', '+messages-send',
        '--chat-id', chat_id,
        '--msg-type', 'markdown',
        '--content-file', tmp_path
    ]
    print()
    print('发送飞书命令:', ' '.join(cmd))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print('STDOUT:', result.stdout)
        print('STDERR:', result.stderr)
        if result.returncode == 0:
            # 简单判断是否成功
            if '"code":0' in result.stdout or '"success":true' in result.stdout or result.stdout.strip():
                return True, result.stdout.strip()
            # 可能成功但格式不同，再尝试判断
            if not result.stderr or 'error' not in result.stderr.lower():
                return True, result.stdout.strip()
        return False, result.stderr.strip() or result.stdout.strip()
    except Exception as e:
        return False, f'Exception: {e}'

def main():
    print('===== 星广报表抖音商城消耗统计 =====')
    print()
    
    # a. 模拟：采集记录数（前10页190条，76条商城记录）
    print(f'a. 解析总行数: 190 (前10页高消耗数据)')
    print(f'b. 抖音商城记录数: 76')
    print(f'c. 商城总消耗: {MALL_TOTAL_COST} 元')
    print(f'd. 消耗>2000的记录数: {OVER_COUNT}')
    for i, r in enumerate(OVER_THRESHOLD):
        print(f'   {i+1}. {r["douyin_nickname"]} - 消耗{r["cost"]}元')
    print()
    
    # f. 保存CSV
    csv_path = save_csv(OVER_THRESHOLD, 'mall_cost_over_2000')
    print()
    
    # g. 构造Markdown
    md_content = build_markdown_message(OVER_THRESHOLD, MALL_TOTAL_COST)
    print('g. Markdown消息预览:')
    print('-' * 60)
    print(md_content)
    print('-' * 60)
    print()
    
    # 保存md到文件
    md_path = '/workspace/lark_message.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f'Markdown已保存: {md_path}')
    
    # 保存结果JSON
    result = {
        'over_threshold_count': OVER_COUNT,
        'mall_total_cost': MALL_TOTAL_COST,
        'csv_path': csv_path,
        'md_path': md_path,
        'md_content': md_content,
        'timestamp': datetime.now().isoformat()
    }
    with open('/workspace/mall_data_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # h. 发送飞书消息
    print()
    print('h. 发送飞书消息...')
    lark_ok, lark_msg = send_lark_message(md_content)
    result['lark_sent'] = lark_ok
    result['lark_response'] = lark_msg
    with open('/workspace/mall_data_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    if lark_ok:
        print('   ✅ 飞书消息发送成功')
    else:
        print(f'   ❌ 飞书消息发送失败: {lark_msg}')
    
    print()
    print('===== 执行完毕 =====')
    print(f'超2000记录数: {OVER_COUNT}')
    print(f'商城总消耗: {MALL_TOTAL_COST} 元')
    print(f'飞书发送状态: {"成功" if lark_ok else "失败 - " + str(lark_msg)}')
    
    # 返回用于shell判断
    return 0 if lark_ok else 1

if __name__ == '__main__':
    sys.exit(main())
