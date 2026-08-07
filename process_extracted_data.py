#!/usr/bin/env python3
"""
数据处理脚本 - 处理从浏览器提取的JSON数据
"""

import json
import csv
import sys
from pathlib import Path

# 配置
INPUT_JSON = "/workspace/all_data.json"
OUTPUT_JSON = "/workspace/all_data_clean.json"
OUTPUT_CSV = "/workspace/high_cost_records.csv"
MIN_COST = 2000  # 筛选条件

def load_json(filepath):
    """加载JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ 成功加载 {filepath}")
        print(f"  记录数: {len(data)}")
        return data
    except FileNotFoundError:
        print(f"✗ 错误: 文件不存在 {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ 错误: JSON解析失败 {filepath}")
        print(f"  {e}")
        sys.exit(1)

def save_json(data, filepath):
    """保存JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ 已保存到 {filepath}")

def filter_high_cost(data, min_cost):
    """筛选消耗大于指定值的记录"""
    filtered = [row for row in data if row.get('cost', 0) > min_cost]
    print(f"\n筛选条件: 消耗 > {min_cost}")
    print(f"符合条件记录数: {len(filtered)}")
    return filtered

def save_to_csv(data, filepath):
    """保存为CSV文件"""
    if not data:
        print(f"✗ 没有数据可保存")
        return
    
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✓ 已保存CSV到 {filepath}")

def print_statistics(data):
    """打印数据统计信息"""
    print("\n" + "=" * 60)
    print("数据统计")
    print("=" * 60)
    
    total_records = len(data)
    print(f"总记录数: {total_records}")
    
    # 计算消耗统计
    costs = [row.get('cost', 0) for row in data if row.get('cost')]
    if costs:
        avg_cost = sum(costs) / len(costs)
        max_cost = max(costs)
        min_cost = min(costs)
        total_cost = sum(costs)
        
        print(f"消耗统计:")
        print(f"  - 总消耗: {total_cost:,.2f}")
        print(f"  - 平均消耗: {avg_cost:,.2f}")
        print(f"  - 最大消耗: {max_cost:,.2f}")
        print(f"  - 最小消耗: {min_cost:,.2f}")
    
    # 统计账号数量
    accounts = set(row.get('accountName', '') for row in data if row.get('accountName'))
    print(f"账号数: {len(accounts)}")
    
    # 统计产品数量
    products = set(row.get('productName', '') for row in data if row.get('productName'))
    print(f"产品数: {len(products)}")
    
    print("=" * 60)

def main():
    """主函数"""
    print("=" * 60)
    print("星广报表数据处理脚本")
    print("=" * 60)
    
    # 加载数据
    print(f"\n步骤1: 加载数据")
    data = load_json(INPUT_JSON)
    
    # 打印统计信息
    print(f"\n步骤2: 数据统计")
    print_statistics(data)
    
    # 筛选高消耗记录
    print(f"\n步骤3: 筛选消耗 > {MIN_COST} 的记录")
    high_cost = filter_high_cost(data, MIN_COST)
    
    # 保存结果
    print(f"\n步骤4: 保存结果")
    
    # 保存清理后的JSON
    save_json(data, OUTPUT_JSON)
    
    # 保存高消耗记录为CSV
    if high_cost:
        save_to_csv(high_cost, OUTPUT_CSV)
        
        # 打印前几条高消耗记录示例
        print(f"\n高消耗记录示例（前5条）:")
        print("-" * 60)
        for i, record in enumerate(high_cost[:5], 1):
            print(f"{i}. {record.get('title', 'N/A')[:30]}...")
            print(f"   消耗: {record.get('cost', 0):,.2f}")
            print(f"   账号: {record.get('accountName', 'N/A')}")
            print(f"   产品: {record.get('productName', 'N/A')}")
            print()
    
    print("\n" + "=" * 60)
    print("处理完成！")
    print("=" * 60)
    print(f"\n输出文件:")
    print(f"  1. {OUTPUT_JSON} - 完整数据（JSON格式）")
    print(f"  2. {OUTPUT_CSV} - 高消耗记录（CSV格式）")
    print("=" * 60)

if __name__ == "__main__":
    main()