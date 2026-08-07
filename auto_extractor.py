#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化循环提取所有星广报表数据
"""
import json
import csv
from datetime import datetime

# 读取保存的数据
def load_data_from_file():
    """从文件加载数据"""
    try:
        with open('/workspace/all_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data_to_file(data):
    """保存数据到文件"""
    with open('/workspace/all_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def filter_cost_over_2000(data):
    """筛选消耗>2000的记录"""
    return [row for row in data if row.get('cost', 0) > 2000]

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    if not data:
        print("No data to save")
        return False

    fieldnames = ['materialId', 'title', 'taskId', 'taskName', 'douyinNickname',
                  'douyinId', 'videoUrl', 'accountName', 'cost', 'productName', 'date']

    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"✓ Saved {len(data)} records to {filename}")
        return True
    except Exception as e:
        print(f"✗ Error saving CSV: {e}")
        return False

# 全局数据
all_data = []

# 初始化脚本
INIT_SCRIPT = """
if (!window.ALL_DATA) {
    window.ALL_DATA = [];
    window.CURRENT_PAGE = 1;
}
'Initialized';
"""

# 提取数据脚本
EXTRACT_SCRIPT = """
const tbody = document.querySelector('.arco-table-body');
if (!tbody) return JSON.stringify({error: 'No tbody found'});

const trs = tbody.querySelectorAll('tr.arco-table-tr');
const rows = [];

for (let i = 1; i < trs.length; i++) {
    const tr = trs[i];
    const cells = tr.querySelectorAll('td.arco-table-td');

    if (cells.length >= 11) {
        const row = {
            materialId: cells[0].textContent.trim(),
            title: cells[1].textContent.trim(),
            taskId: cells[2].textContent.trim(),
            taskName: cells[3].textContent.trim(),
            douyinNickname: cells[4].textContent.trim(),
            douyinId: cells[5].textContent.trim(),
            videoUrl: cells[6].textContent.trim(),
            accountName: cells[7].textContent.trim(),
            cost: parseFloat(cells[8].textContent.trim()) || 0,
            productName: cells[9].textContent.trim(),
            date: cells[10].textContent.trim()
        };
        rows.push(row);
    }
}

if (window.ALL_DATA) {
    window.ALL_DATA.push(...rows);
}

return JSON.stringify({
    page: window.CURRENT_PAGE || 1,
    extracted: rows.length,
    total: window.ALL_DATA ? window.ALL_DATA.length : 0,
    data: rows
});
"""

# 点击下一页脚本
NEXT_PAGE_SCRIPT = """
const nextBtn = document.querySelector('.arco-pagination-item-next');
if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
    nextBtn.click();
    window.CURRENT_PAGE = (window.CURRENT_PAGE || 1) + 1;
    return 'clicked';
}
return 'disabled';
"""

# 获取所有数据脚本
GET_ALL_DATA_SCRIPT = """
return JSON.stringify({
    totalRecords: window.ALL_DATA ? window.ALL_DATA.length : 0,
    data: window.ALL_DATA || []
});
"""

if __name__ == '__main__':
    print("=" * 60)
    print("星广报表数据自动提取脚本")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("此脚本需要通过主程序调用 run_mcp 工具来执行")
    print()
    print("提取流程:")
    print("1. 初始化全局变量")
    print("2. 循环52次，每次：")
    print("   - 提取当前页数据")
    print("   - 点击下一页")
    print("   - 等待2秒")
    print("3. 获取所有数据并保存")
    print()
    print("注意：浏览器已锁定，需要使用 run_mcp 工具")
    print("=" * 60)