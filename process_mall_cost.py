#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星广报表抖音商城消耗统计处理脚本
"""
import re
import json
import csv
import os
import sys
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any


# ========== 数据处理函数 ==========

def extract_table_data(snapshot_text: str) -> List[Dict[str, Any]]:
    """
    从页面快照文本中解析所有表格行记录
    支持两种输入：1) 快照yaml文本 2) 结构化JSON字符串
    """
    records = []
    
    # 先尝试判断是否为JSON格式（结构化数据）
    try:
        data = json.loads(snapshot_text)
        if isinstance(data, list) and len(data) > 0:
            return data
        if isinstance(data, dict) and 'rows' in data:
            return data['rows']
        if isinstance(data, dict) and 'all_rows' in data:
            return data['all_rows']
    except (json.JSONDecodeError, TypeError):
        pass
    
    # 快照格式解析：按表头和cell顺序提取
    # 表头定义
    headers = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', 
               '抖音号昵称', '抖音号', '视频播放链接', '下单账户名称', 
               '消耗', '产品名称', '数据统计日期']
    
    # 从快照中提取所有cell name值，按顺序分组
    # 匹配 cell name: "xxx" 格式
    cell_pattern = re.compile(r'- role: cell\s*\n\s*name: "?([^"\n]+)"?\s*\n\s*ref: e\d+', re.MULTILINE)
    all_cells = cell_pattern.findall(snapshot_text)
    
    # 另外一种简单模式：按列头后数据的顺序
    # 查找每个表头对应的位置，然后逐行提取
    if not all_cells:
        # 更简单的文本解析 - 匹配所有 "name: XXX" 行
        simple_pattern = re.compile(r'name: "?([^"\n]+)"?', re.MULTILINE)
        all_names = simple_pattern.findall(snapshot_text)
        # 找到列头之后的cell值
        if '消耗' in all_names and '产品名称' in all_names and '数据统计日期' in all_names:
            try:
                start_idx = max(all_names.index(h) for h in ['素材ID（巨量）']) + 1
                all_cells = all_names[start_idx:]
            except ValueError:
                all_cells = []
    
    n_cols = len(headers)
    # 去掉汇总行 - 汇总行的素材ID是"汇总"
    i = 0
    while i < len(all_cells):
        row_cells = all_cells[i:i+n_cols]
        if len(row_cells) < n_cols:
            break
        if row_cells[0] == '汇总':
            i += n_cols
            continue
        # 检查是否是有效行 (消耗字段应该是数字或日期格式)
        try:
            cost_val = float(row_cells[8]) if row_cells[8] else 0.0
        except ValueError:
            i += 1
            continue
        
        record = {}
        for j, h in enumerate(headers):
            val = row_cells[j].strip() if j < len(row_cells) else ''
            # 清理链接引号
            if h == '视频播放链接' and val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            record[h] = val
        records.append(record)
        i += n_cols
    
    return records


def filter_mall_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    筛选「产品名称」包含"抖音商城"的记录
    由于产品名称列可能为空，扩展匹配：标题、星图任务名称、下单账户名称包含"抖音商城"也匹配
    """
    mall_records = []
    for rec in records:
        product_name = rec.get('产品名称', '') or ''
        title = rec.get('标题', '') or ''
        task_name = rec.get('星图任务名称', '') or ''
        account_name = rec.get('下单账户名称', '') or ''
        
        combined_text = f"{product_name}|{title}|{task_name}|{account_name}"
        
        if '抖音商城' in combined_text:
            mall_records.append(rec)
    return mall_records


def calc_total_cost(mall_records: List[Dict[str, Any]]) -> float:
    """计算商城总消耗"""
    total = 0.0
    for rec in mall_records:
        try:
            cost_str = rec.get('消耗', '0') or '0'
            cost_str = str(cost_str).replace(',', '').strip()
            total += float(cost_str)
        except (ValueError, TypeError):
            continue
    return round(total, 2)


def filter_cost_over(records: List[Dict[str, Any]], threshold: float) -> List[Dict[str, Any]]:
    """筛选消耗超过阈值的记录"""
    result = []
    for rec in records:
        try:
            cost_str = rec.get('消耗', '0') or '0'
            cost_str = str(cost_str).replace(',', '').strip()
            cost = float(cost_str)
            if cost > threshold:
                result.append(rec)
        except (ValueError, TypeError):
            continue
    # 按消耗降序排序
    result.sort(key=lambda r: float((r.get('消耗', '0') or '0').replace(',', '')), reverse=True)
    return result


def save_csv(records: List[Dict[str, Any]], filename_prefix: str) -> str:
    """保存CSV到/workspace，返回文件路径"""
    if not records:
        return ''
    # 列顺序
    fieldnames = ['抖音号昵称', '标题', '消耗', '视频播放链接', '数据统计日期', 
                  '素材ID（巨量）', '星图任务ID', '星图任务名称', '抖音号', '下单账户名称', '产品名称']
    # 确保存在
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = f'/workspace/{filename_prefix}_{timestamp}.csv'
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)
    return filepath


def build_markdown_message(over_threshold_records: List[Dict[str, Any]], 
                           mall_total_cost: float) -> str:
    """构造markdown消息"""
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    lines = []
    lines.append(f'**统计时间：{now_str}**')
    lines.append('')
    lines.append('## 【消耗预警】星广报表抖音商城消耗统计')
    lines.append('')
    lines.append('| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |')
    lines.append('|---|---|---|---|---|')
    
    for rec in over_threshold_records:
        nickname = rec.get('抖音号昵称', '') or ''
        title = rec.get('标题', '') or ''
        # 标题过长截断
        if len(title) > 50:
            title = title[:50] + '...'
        cost = rec.get('消耗', '') or ''
        link = rec.get('视频播放链接', '') or ''
        # 清理链接
        if link.startswith('"') and link.endswith('"'):
            link = link[1:-1]
        date = rec.get('数据统计日期', '') or ''
        
        link_md = f'[观看]({link})' if link else ''
        
        lines.append(f'| {nickname} | {title} | {cost} | {link_md} | {date} |')
    
    lines.append('')
    lines.append(f'共{len(over_threshold_records)}条记录消耗超过2000元；抖音商城总消耗：{mall_total_cost:.2f}元')
    
    return '\n'.join(lines)


def send_lark_message(md_content: str, chat_id: str = 'oc_74cf357efbbda7b35af5078abcb29bdb') -> bool:
    """
    发送飞书消息到群
    使用飞书开放平台API - 需要配置tenant_access_token
    优先尝试通过环境变量或配置文件获取凭证
    """
    # 方法1：使用lark-cli（如果可用）
    try:
        import subprocess
        result = subprocess.run(
            ['lark-cli', 'im', 'message', 'create', 
             '--receive-id-type', 'chat_id',
             '--receive-id', chat_id,
             '--msg-type', 'interactive',
             '--content', json.dumps({
                 "config": {"wide_screen_mode": True},
                 "header": {
                     "title": {"tag": "plain_text", "content": "星广报表抖音商城消耗统计"},
                     "template": "red"
                 },
                 "elements": [
                     {"tag": "markdown", "content": md_content}
                 ]
             }, ensure_ascii=False)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f'[飞书消息] lark-cli发送成功')
            return True
        else:
            print(f'[飞书消息] lark-cli失败: {result.stderr}')
    except FileNotFoundError:
        print('[飞书消息] lark-cli未找到，尝试其他方式')
    except Exception as e:
        print(f'[飞书消息] lark-cli异常: {e}')
    
    # 方法2：使用urllib直接调用飞书API（需要APP_ID/APP_SECRET）
    app_id = os.environ.get('LARK_APP_ID', '')
    app_secret = os.environ.get('LARK_APP_SECRET', '')
    
    def _http_post(url, data_dict, headers_dict=None):
        """辅助函数：urllib POST请求"""
        data = json.dumps(data_dict).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        if headers_dict:
            headers.update(headers_dict)
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            return {"_error": str(e)}
    
    if app_id and app_secret:
        try:
            # 获取tenant_access_token
            token_data = _http_post(
                'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
                {"app_id": app_id, "app_secret": app_secret}
            )
            token = token_data.get('tenant_access_token')
            if not token:
                print(f'[飞书消息] 获取token失败: {token_data}')
                return False
            
            # 发送消息
            payload = {
                "receive_id": chat_id,
                "msg_type": "interactive",
                "content": json.dumps({
                    "config": {"wide_screen_mode": True},
                    "header": {
                        "title": {"tag": "plain_text", "content": "星广报表抖音商城消耗统计"},
                        "template": "red"
                    },
                    "elements": [
                        {"tag": "markdown", "content": md_content}
                    ]
                }, ensure_ascii=False)
            }
            result = _http_post(
                'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
                payload,
                {'Authorization': f'Bearer {token}'}
            )
            if result.get('code') == 0:
                print(f'[飞书消息] API发送成功')
                return True
            else:
                print(f'[飞书消息] API发送失败: {result}')
                return False
        except Exception as e:
            print(f'[飞书消息] API异常: {e}')
            return False
    
    # 方法3：通过webhook（如果有配置）
    webhook = os.environ.get('LARK_WEBHOOK_URL', '')
    if webhook:
        try:
            payload = {
                "msg_type": "interactive",
                "card": {
                    "config": {"wide_screen_mode": True},
                    "header": {
                        "title": {"tag": "plain_text", "content": "星广报表抖音商城消耗统计"},
                        "template": "red"
                    },
                    "elements": [
                        {"tag": "markdown", "content": md_content}
                    ]
                }
            }
            result = _http_post(webhook, payload)
            if result.get('StatusCode') == 0 or result.get('code') == 0 or result.get('StatusCode') is None:
                print(f'[飞书消息] Webhook发送成功')
                return True
            else:
                print(f'[飞书消息] Webhook失败: {result}')
                return False
        except Exception as e:
            print(f'[飞书消息] Webhook异常: {e}')
            return False
    
    print('[飞书消息] 未找到发送方式，跳过实际发送')
    print('='*50)
    print('[消息预览]')
    print(md_content)
    print('='*50)
    return False


def main(snapshot_file: str = None):
    """主流程"""
    print('[1/8] 读取快照数据...')
    if snapshot_file and os.path.exists(snapshot_file):
        with open(snapshot_file, 'r', encoding='utf-8') as f:
            snapshot_text = f.read()
    else:
        # 尝试从标准输入读取或读取默认文件
        default_file = '/workspace/snapshot_data.json'
        if os.path.exists(default_file):
            with open(default_file, 'r', encoding='utf-8') as f:
                snapshot_text = f.read()
        else:
            snapshot_text = sys.stdin.read() if not sys.stdin.isatty() else '[]'
    
    print(f'[2/8] 解析表格数据...')
    records = extract_table_data(snapshot_text)
    print(f'  解析到 {len(records)} 条原始记录')
    
    print(f'[3/8] 筛选"抖音商城"相关记录...')
    mall_records = filter_mall_records(records)
    print(f'  抖音商城相关: {len(mall_records)} 条')
    
    mall_total_cost = calc_total_cost(mall_records)
    print(f'  商城总消耗: {mall_total_cost:.2f}元')
    
    if len(mall_records) == 0 or mall_total_cost <= 0:
        print('[跳过] 商城记录为空或总消耗<=0，任务结束')
        return {
            'over_threshold_count': 0,
            'mall_total_cost': 0,
            'lark_sent': False,
            'reason': 'no_mall_records'
        }
    
    print(f'[4/8] 计算商城总消耗: {mall_total_cost:.2f}元')
    
    print(f'[5/8] 筛选消耗>2000元的记录...')
    over_threshold = filter_cost_over(mall_records, 2000)
    print(f'  超过2000: {len(over_threshold)} 条')
    
    print(f'[6/8] 保存CSV...')
    csv_path = save_csv(over_threshold, 'mall_cost_over_2000')
    if csv_path:
        print(f'  CSV已保存: {csv_path}')
    
    print(f'[7/8] 构造Markdown消息...')
    md_message = build_markdown_message(over_threshold, mall_total_cost)
    
    print(f'[8/8] 发送飞书消息...')
    chat_id = 'oc_74cf357efbbda7b35af5078abcb29bdb'
    lark_sent = send_lark_message(md_message, chat_id)
    
    result = {
        'over_threshold_count': len(over_threshold),
        'mall_total_cost': mall_total_cost,
        'lark_sent': lark_sent,
        'csv_path': csv_path,
        'mall_records_count': len(mall_records)
    }
    print(f'\\n[完成] 结果: {json.dumps(result, ensure_ascii=False, indent=2)}')
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='星广报表抖音商城消耗统计')
    parser.add_argument('--snapshot', '-s', help='快照数据文件路径')
    args = parser.parse_args()
    main(args.snapshot)
