#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的自动化数据提取脚本
通过主程序调用run_mcp工具逐页提取
"""
import json
import csv
from datetime import datetime

# 全局状态
class ExtractionState:
    def __init__(self):
        self.all_data = []
        self.filtered_data = []
        self.current_page = 0
        self.total_pages = 52
        self.success_count = 0
        self.error_count = 0

    def add_page_data(self, data):
        """添加一页数据"""
        self.all_data.extend(data)
        self.success_count += 1

        # 实时筛选
        page_filtered = [row for row in data if row.get('cost', 0) > 2000]
        self.filtered_data.extend(page_filtered)

    def get_status(self):
        """获取当前状态"""
        return {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'total_records': len(self.all_data),
            'filtered_records': len(self.filtered_data),
            'success': self.success_count,
            'errors': self.error_count
        }

# 提取脚本模板
EXTRACT_TEMPLATE = """
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

return JSON.stringify({success: true, page: PAGE_NUM, rowCount: rows.length, data: rows});
"""

NEXT_PAGE_SCRIPT = """
const nextBtn = document.querySelector('.arco-pagination-item-next');
if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
    nextBtn.click();
    return 'clicked';
}
return 'disabled';
"""

def main():
    state = ExtractionState()

    print("=" * 70)
    print("星广报表数据自动提取系统")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总页数: {state.total_pages}")
    print("=" * 70)
    print()
    print("此脚本通过主程序调用 run_mcp 工具执行")
    print()
    print("执行步骤:")
    print("1. 初始化状态")
    print("2. 循环提取每一页:")
    print("   - 使用 browser_evaluate 提取数据")
    print("   - 使用 browser_evaluate 点击下一页")
    print("   - 使用 browser_wait_for 等待加载")
    print("3. 保存筛选后的数据")
    print("4. 发送飞书消息")
    print()
    print("=" * 70)

if __name__ == '__main__':
    main()