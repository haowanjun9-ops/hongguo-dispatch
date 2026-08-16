import requests
import json
import csv
import os
from datetime import datetime

# API信息
BASE_URL = "https://wxxcx.whaleidea.cn/material-report/"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNTQzIiwiZXhwIjoxNzg4MDY5NzA2fQ.6FYKBrAcr51nPEyit92GXNafL8s7p79NX6THybvRIhE"
COOKIE = "_preview_auth=50gtEGTNnFSljxKFxEZ8_V3yrdzG6Me61Lys7mNstRM"

# 请求头
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Cookie": COOKIE,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://apex.whaleidea.cn",
    "Referer": "https://apex.whaleidea.cn/"
}

# 列名映射 - 需要确认API返回的字段名
COLUMNS = [
    "素材ID（巨量）", "标题", "星图任务ID", "星图任务名称", 
    "抖音号昵称", "抖音号", "视频播放链接", "下单账户名称", 
    "消耗", "产品名称", "数据统计日期"
]

def fetch_all_data():
    all_data = []
    page = 1
    page_size = 100
    
    # 先获取第一页，看看总数
    params = {"page": 1, "page_size": page_size}
    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
        print(f"第一页状态码: {resp.status_code}")
        print(f"响应内容前500字符: {resp.text[:500]}")
        
        if resp.status_code != 200:
            # 尝试不带Bearer，只带cookie
            headers2 = {
                "Cookie": COOKIE,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://apex.whaleidea.cn/"
            }
            resp2 = requests.get(BASE_URL, params=params, headers=headers2, timeout=30)
            print(f"\n尝试不带Bearer的状态码: {resp2.status_code}")
            print(f"响应前500字符: {resp2.text[:500]}")
            
            # 尝试只带token作为query参数
            params3 = {"page": 1, "page_size": page_size, "token": TOKEN}
            resp3 = requests.get(BASE_URL, params=params3, headers=headers2, timeout=30)
            print(f"\n尝试token参数方式状态码: {resp3.status_code}")
            print(f"响应前500字符: {resp3.text[:500]}")
            
            # 尝试用token替换preview_auth cookie
            for cookie_name in ["token", "authorization", "auth", "jwt"]:
                headers4 = {
                    "Cookie": f"{cookie_name}={TOKEN}",
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                    "Referer": "https://apex.whaleidea.cn/"
                }
                resp4 = requests.get(BASE_URL, params=params, headers=headers4, timeout=30)
                if resp4.status_code == 200:
                    print(f"Cookie {cookie_name} 成功！")
                    resp = resp4
                    break
            
        return parse_and_collect(resp, page_size)
            
    except Exception as e:
        print(f"请求出错: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_and_collect(first_resp, page_size):
    """解析响应并收集所有页面数据"""
    all_data = []
    
    try:
        data = first_resp.json()
    except:
        print(f"无法解析JSON，原始响应: {first_resp.text[:1000]}")
        return []
    
    print(f"\n解析到的JSON结构 keys: {data.keys() if isinstance(data, dict) else '非dict'}")
    print(f"JSON内容: {json.dumps(data, ensure_ascii=False)[:1500]}")
    
    # 尝试多种可能的分页结构
    items = None
    total = 0
    
    if isinstance(data, dict):
        # 常见结构1: {count: N, results: [...]} or {data: {count, items}}
        for key in ['results', 'items', 'data', 'list', 'records']:
            if key in data and isinstance(data[key], list):
                items = data[key]
                break
        
        # 如果data本身是list
        if items is None and isinstance(data, list):
            items = data
        
        # 找总数
        for key in ['count', 'total', 'totalCount', 'total_count']:
            if key in data and isinstance(data[key], (int, float)):
                total = int(data[key])
                break
        
        # 如果嵌套在data字段里
        if 'data' in data and isinstance(data['data'], dict):
            inner = data['data']
            for key in ['results', 'items', 'list', 'records']:
                if key in inner and isinstance(inner[key], list):
                    items = inner[key]
                    break
            for key in ['count', 'total', 'totalCount']:
                if key in inner and isinstance(inner[key], (int, float)):
                    total = int(inner[key])
                    break
    
    if items is None:
        print("无法从响应中找到数据列表")
        return []
    
    print(f"\n第一页找到 {len(items)} 条记录，总数约 {total}")
    
    # 打印第一条记录的字段结构
    if items and isinstance(items[0], dict):
        print(f"单条记录字段: {list(items[0].keys())}")
        print(f"示例记录: {json.dumps(items[0], ensure_ascii=False)[:500]}")
    
    all_data.extend(items)
    
    # 如果有更多页，继续获取
    if total > len(items):
        total_pages = (total + page_size - 1) // page_size
        print(f"\n需要获取 {total_pages} 页数据")
        
        for page in range(2, total_pages + 1):
            params = {"page": page, "page_size": page_size}
            try:
                resp = requests.get(BASE_URL, params=params, headers=first_resp.request.headers, timeout=30)
                if resp.status_code == 200:
                    page_data = resp.json()
                    page_items = None
                    
                    if isinstance(page_data, dict):
                        for key in ['results', 'items', 'data', 'list', 'records']:
                            if key in page_data and isinstance(page_data[key], list):
                                page_items = page_data[key]
                                break
                        if 'data' in page_data and isinstance(page_data['data'], dict):
                            inner = page_data['data']
                            for key in ['results', 'items', 'list', 'records']:
                                if key in inner and isinstance(inner[key], list):
                                    page_items = inner[key]
                                    break
                    
                    if page_items:
                        all_data.extend(page_items)
                        print(f"第 {page}/{total_pages} 页: +{len(page_items)} 条，累计 {len(all_data)} 条")
                    else:
                        print(f"第 {page} 页未找到数据")
                else:
                    print(f"第 {page} 页请求失败: {resp.status_code}")
            except Exception as e:
                print(f"第 {page} 页出错: {e}")
    
    print(f"\n总共获取 {len(all_data)} 条记录")
    return all_data

def transform_record(raw):
    """将API返回的原始记录转换为标准列名"""
    # 需要根据实际API字段来映射
    # 常见字段猜测:
    mapping = {
        "素材ID（巨量）": ["material_id", "materialId", "ad_id", "adId", "素材ID"],
        "标题": ["title", "ad_title", "video_title", "标题"],
        "星图任务ID": ["star_task_id", "starTaskId", "task_id", "taskId", "星图任务ID"],
        "星图任务名称": ["star_task_name", "starTaskName", "task_name", "taskName", "星图任务名称"],
        "抖音号昵称": ["douyin_nickname", "douyinNickname", "nickname", "aweme_nickname", "抖音号昵称"],
        "抖音号": ["douyin_id", "douyinId", "aweme_id", "awemeId", "sec_uid", "抖音号"],
        "视频播放链接": ["video_url", "videoUrl", "play_url", "playUrl", "share_url", "视频播放链接"],
        "下单账户名称": ["account_name", "accountName", "advertiser_name", "下单账户名称"],
        "消耗": ["cost", "spend", "expense", "消耗"],
        "产品名称": ["product_name", "productName", "产品名称"],
        "数据统计日期": ["date", "stat_date", "statDate", "report_date", "数据统计日期"],
    }
    
    result = {}
    for col, possible_keys in mapping.items():
        for key in possible_keys:
            if key in raw and raw[key] is not None:
                result[col] = raw[key]
                break
        if col not in result:
            # 也尝试直接匹配
            if col in raw:
                result[col] = raw[col]
            else:
                result[col] = ""
    
    return result

def filter_cost_over_2000(records):
    """筛选消耗>2000的记录"""
    filtered = []
    for r in records:
        try:
            cost_str = str(r.get("消耗", "0")).replace(",", "").replace("￥", "").replace("¥", "")
            cost = float(cost_str) if cost_str else 0
            if cost > 2000:
                filtered.append(r)
        except (ValueError, TypeError):
            continue
    return filtered

def save_to_csv(records, filepath):
    """保存到CSV"""
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for r in records:
            writer.writerow({col: r.get(col, "") for col in COLUMNS})
    print(f"CSV已保存到: {filepath}")

if __name__ == "__main__":
    print("开始获取星广报表数据...")
    raw_data = fetch_all_data()
    
    if not raw_data:
        print("未获取到任何数据")
        exit(1)
    
    # 转换字段
    transformed = [transform_record(r) for r in raw_data]
    
    # 筛选消耗>2000
    filtered = filter_cost_over_2000(transformed)
    print(f"\n筛选出消耗>2000的记录: {len(filtered)} 条")
    
    for i, r in enumerate(filtered[:5]):
        print(f"  {i+1}. {r.get('抖音号昵称')} - {r.get('标题')[:20]}... - 消耗: {r.get('消耗')}")
    
    # 生成时间戳和文件名
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M")
    csv_path = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"
    
    # 保存结果元数据供后续步骤使用
    result_meta = {
        "total_records": len(transformed),
        "filtered_count": len(filtered),
        "csv_path": csv_path if filtered else None,
        "filter_records": filtered,
        "timestamp": now.strftime("%Y-%m-%d %H:%M"),
        "date_str": now.strftime("%Y-%m-%d")
    }
    
    with open("/workspace/star_report_result.json", "w", encoding="utf-8") as f:
        json.dump(result_meta, f, ensure_ascii=False, indent=2)
    
    if filtered:
        save_to_csv(filtered, csv_path)
    else:
        print("无超2000消耗数据")
    
    print(f"\n结果元数据已保存: /workspace/star_report_result.json")
