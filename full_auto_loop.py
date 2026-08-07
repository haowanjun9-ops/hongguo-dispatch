#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整自动化循环提取脚本
主程序 - 通过MCP工具控制浏览器
"""
import json
import csv
import time
from datetime import datetime

class AutomationController:
    def __init__(self):
        self.all_data = []
        self.filtered_data = []
        self.total_pages = 52
        self.current_page = 0
        self.extraction_complete = False

    # JavaScript脚本定义
    INIT_SCRIPT = """
window.CURRENT_PAGE = 1;
window.ALL_DATA = [];
'Initialized';
"""

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

return JSON.stringify({
    success: true,
    page: window.CURRENT_PAGE || 1,
    rowCount: rows.length,
    data: rows
});
"""

    NEXT_PAGE_SCRIPT = """
const nextBtn = document.querySelector('.arco-pagination-item-next');
if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
    nextBtn.click();
    window.CURRENT_PAGE = (window.CURRENT_PAGE || 1) + 1;
    return 'clicked';
}
return 'disabled';
"""

    def process_extraction_result(self, json_str):
        """处理提取结果"""
        try:
            result = json.loads(json_str)

            if 'error' in result:
                return False, result['error']

            if not result.get('success'):
                return False, 'Extraction failed'

            page = result.get('page', '?')
            data = result.get('data', [])

            self.all_data.extend(data)
            self.current_page = page

            # 筛选消耗>2000的记录
            page_filtered = [row for row in data if row.get('cost', 0) > 2000]
            self.filtered_data.extend(page_filtered)

            return True, {
                'page': page,
                'extracted': len(data),
                'filtered': len(page_filtered),
                'total': len(self.all_data),
                'total_filtered': len(self.filtered_data)
            }

        except Exception as e:
            return False, str(e)

    def save_filtered_data(self):
        """保存筛选后的数据"""
        if not self.filtered_data:
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"

        fieldnames = ['materialId', 'title', 'taskId', 'taskName', 'douyinNickname',
                      'douyinId', 'videoUrl', 'accountName', 'cost', 'productName', 'date']

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.filtered_data)

        return filename

# 主程序
if __name__ == '__main__':
    controller = AutomationController()

    print("=" * 70)
    print("星广报表数据自动提取系统")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总页数: {controller.total_pages}")
    print("=" * 70)
    print()
    print("此脚本将通过以下步骤执行:")
    print()
    print("1. 初始化浏览器全局变量")
    print("2. 循环处理每一页:")
    print("   a. 提取当前页数据")
    print("   b. 筛选消耗>2000的记录")
    print("   c. 点击下一页")
    print("   d. 等待2秒")
    print("3. 保存筛选后的数据到CSV")
    print("4. 生成摘要报告")
    print()
    print("=" * 70)
    print()
    print("注意: 需要在主程序中通过 run_mcp 工具调用浏览器")
    print()
    print("使用的脚本:")
    print(f"- INIT_SCRIPT: {len(controller.INIT_SCRIPT)} 字符")
    print(f"- EXTRACT_SCRIPT: {len(controller.EXTRACT_SCRIPT)} 字符")
    print(f"- NEXT_PAGE_SCRIPT: {len(controller.NEXT_PAGE_SCRIPT)} 字符")
    print()
    print("=" * 70)