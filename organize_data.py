#!/usr/bin/env python3
"""
将下载的星广报表数据移动到指定位置
"""
import os
import json
import shutil
from pathlib import Path

def find_and_organize_star_report():
    """
    查找浏览器下载的星广报表JSON文件，并移动到 /workspace/all_data.json
    """
    # 常见的浏览器下载目录
    download_dirs = [
        Path.home() / 'Downloads',
        Path.home() / '下载',
        Path('/tmp/downloads'),
    ]

    # 查找所有可能的星广报表文件
    star_report_files = []

    for download_dir in download_dirs:
        if download_dir.exists():
            # 查找匹配的文件
            for file_path in download_dir.glob('star_report_*.json'):
                star_report_files.append(file_path)

    if not star_report_files:
        print("未找到星广报表数据文件")
        print("\n请确保：")
        print("1. 已在浏览器控制台运行 /workspace/extract_star_report_automation.js")
        print("2. 数据文件已下载到浏览器默认下载目录")
        return False

    # 按修改时间排序，选择最新的
    star_report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_file = star_report_files[0]

    print(f"找到星广报表数据文件: {latest_file}")

    # 验证JSON文件有效性
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("错误：数据格式不正确，应为JSON数组")
            return False

        print(f"数据验证通过，包含 {len(data)} 条记录")

        # 移动到目标位置
        target_path = Path('/workspace/all_data.json')
        shutil.copy2(latest_file, target_path)

        print(f"\n✅ 数据已复制到: {target_path}")
        print(f"   总记录数: {len(data)}")

        # 显示前3条记录示例
        print("\n前3条记录示例:")
        for i, record in enumerate(data[:3], 1):
            print(f"\n记录 {i}:")
            print(f"  物料ID: {record.get('materialId', 'N/A')}")
            print(f"  标题: {record.get('title', 'N/A')}")
            print(f"  成本: {record.get('cost', 0)}")

        return True

    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return False
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        return False

def create_sample_data():
    """
    创建示例数据文件（用于测试）
    """
    sample_data = [
        {
            "materialId": "SAMPLE001",
            "title": "示例标题1",
            "taskId": "TASK001",
            "taskName": "示例任务",
            "douyinNickname": "示例昵称",
            "douyinId": "123456789",
            "videoUrl": "https://example.com/video1",
            "accountName": "示例账户",
            "cost": 100.50,
            "productName": "示例产品",
            "date": "2024-01-01"
        }
    ]

    target_path = Path('/workspace/all_data.json')
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)

    print(f"示例数据已创建: {target_path}")

if __name__ == "__main__":
    print("=" * 70)
    print("星广报表数据文件整理工具")
    print("=" * 70)
    print("\n正在查找下载的数据文件...\n")

    success = find_and_organize_star_report()

    if not success:
        print("\n" + "=" * 70)
        print("如果数据文件在其他位置，您可以手动移动：")
        print("1. 找到浏览器下载的 star_report_*.json 文件")
        print("2. 将其复制到 /workspace/all_data.json")
        print("=" * 70)