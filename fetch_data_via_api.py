#!/usr/bin/env python3
"""
使用Python requests库提取数据
通过API直接获取数据，避免浏览器自动化的复杂性
"""
import requests
import csv
import json
from datetime import datetime

# 登录信息
LOGIN_URL = "https://apex.whaleidea.cn/api/v1/auth/login"
REPORT_URL = "https://apex.whaleidea.cn/api/v1/star/report/list"

def login(session, username, password):
    """登录获取token"""
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = session.post(LOGIN_URL, json=login_data)
        response.raise_for_status()
        
        result = response.json()
        if result.get('code') == 0:
            token = result['data'].get('token')
            print(f"登录成功，获取到token")
            return token
        else:
            print(f"登录失败: {result.get('message')}")
            return None
    except Exception as e:
        print(f"登录出错: {e}")
        return None

def fetch_report_data(session, token, page=1, page_size=20):
    """获取报表数据"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "page": page,
        "page_size": page_size,
        # 可以添加其他筛选参数
    }
    
    try:
        response = session.get(REPORT_URL, headers=headers, params=params)
        response.raise_for_status()
        
        result = response.json()
        if result.get('code') == 0:
            return result.get('data', {})
        else:
            print(f"获取数据失败: {result.get('message')}")
            return None
    except Exception as e:
        print(f"获取数据出错: {e}")
        return None

def extract_all_pages(session, token):
    """提取所有页面数据"""
    all_data = []
    page = 1
    
    while True:
        print(f"正在获取第{page}页数据...")
        data = fetch_report_data(session, token, page=page)
        
        if not data:
            break
        
        items = data.get('list', [])
        if not items:
            break
        
        all_data.extend(items)
        print(f"第{page}页: {len(items)}条记录，累计{len(all_data)}条")
        
        # 检查是否还有下一页
        total = data.get('total', 0)
        if len(all_data) >= total:
            break
        
        page += 1
    
    return all_data

def filter_high_cost(data, threshold=2000):
    """筛选消耗超过阈值的记录"""
    high_cost = []
    
    for item in data:
        # 提取消耗值（假设字段名为 cost 或 consumption）
        cost = float(item.get('cost', 0) or item.get('consumption', 0) or 0)
        
        if cost > threshold:
            high_cost.append({
                '素材ID（巨量）': item.get('materialId', ''),
                '标题': item.get('title', ''),
                '星图任务ID': item.get('starTaskId', ''),
                '星图任务名称': item.get('starTaskName', ''),
                '抖音号昵称': item.get('douyinNickname', ''),
                '抖音号': item.get('douyinId', ''),
                '视频播放链接': item.get('videoLink', ''),
                '下单账户名称': item.get('orderAccount', ''),
                '消耗': cost,
                '产品名称': item.get('productName', ''),
                '数据统计日期': item.get('statDate', '')
            })
    
    return high_cost

def save_to_csv(data, filename):
    """保存数据到CSV"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', 
                      '抖音号', '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def main():
    username = "haowanjun@whalewh.cn"
    password = "?!]d<yI0"
    
    print("="*60)
    print("鲸准3.0星广报表数据提取")
    print("="*60)
    
    session = requests.Session()
    
    # 登录
    token = login(session, username, password)
    if not token:
        print("登录失败，无法继续")
        return
    
    # 提取所有数据
    all_data = extract_all_pages(session, token)
    
    if not all_data:
        print("\n无数据")
        return
    
    print(f"\n总共提取了 {len(all_data)} 条记录")
    
    # 筛选消耗超过2000的记录
    high_cost_data = filter_high_cost(all_data, 2000)
    print(f"消耗超过2000的记录: {len(high_cost_data)} 条")
    
    if not high_cost_data:
        print("\n无超2000消耗数据")
        return
    
    # 保存到CSV
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    csv_file = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"
    save_to_csv(high_cost_data, csv_file)
    print(f"数据已保存到: {csv_file}")
    
    return csv_file, len(high_cost_data)

if __name__ == "__main__":
    result = main()
    if result:
        csv_file, count = result
        print(f"\n任务完成！共筛选出 {count} 条消耗超过2000的记录")