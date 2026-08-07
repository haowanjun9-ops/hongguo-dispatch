#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化逐页提取数据
通过MCP工具控制浏览器
"""
import json
import csv
import os
from datetime import datetime

class StarReportAutoExtractor:
    def __init__(self):
        self.all_data = []
        self.filtered_data = []
        self.total_pages = 52
        self.current_page = 0

    def get_extract_script(self):
        """获取提取当前页数据的脚本"""
        return """
const tbody = document.querySelector('.arco-table-body');
if (!tbody) return JSON.stringify({error: 'No tbody found', page: window.CURRENT_PAGE || 1});

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

    def get_next_page_script(self):
        """获取点击下一页的脚本"""
        return """
const nextBtn = document.querySelector('.arco-pagination-item-next');
if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
    nextBtn.click();
    if (window.CURRENT_PAGE) {
        window.CURRENT_PAGE++;
    } else {
        window.CURRENT_PAGE = 2;
    }
    return 'clicked';
}
return 'disabled';
"""

    def get_init_script(self):
        """获取初始化脚本"""
        return """
window.CURRENT_PAGE = 1;
window.ALL_DATA = [];
'Initialized';
"""

    def process_page_result(self, json_str):
        """处理页面提取结果"""
        try:
            result = json.loads(json_str)

            if 'error' in result:
                print(f"✗ Error on page {result.get('page', '?')}: {result['error']}")
                return False

            if not result.get('success'):
                print(f"✗ Extraction failed")
                return False

            page = result.get('page', '?')
            data = result.get('data', [])

            self.all_data.extend(data)
            self.current_page = page

            # 实时筛选消耗>2000的记录
            page_filtered = [row for row in data if row.get('cost', 0) > 2000]
            self.filtered_data.extend(page_filtered)

            print(f"✓ Page {page}: Extracted {len(data)} records, "
                  f"Found {len(page_filtered)} with cost>2000, "
                  f"Total: {len(self.all_data)} records, "
                  f"Filtered: {len(self.filtered_data)} records")

            return True

        except Exception as e:
            print(f"✗ Error parsing result: {e}")
            return False

    def save_filtered_data(self):
        """保存筛选后的数据到CSV"""
        if not self.filtered_data:
            print("\\n✗ No filtered data to save")
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"

        fieldnames = ['materialId', 'title', 'taskId', 'taskName', 'douyinNickname',
                      'douyinId', 'videoUrl', 'accountName', 'cost', 'productName', 'date']

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.filtered_data)

            print(f"\\n✓ Saved {len(self.filtered_data)} filtered records to {filename}")
            return filename

        except Exception as e:
            print(f"\\n✗ Error saving CSV: {e}")
            return None

    def get_summary(self):
        """获取提取摘要"""
        return {
            'total_records': len(self.all_data),
            'filtered_records': len(self.filtered_data),
            'pages_processed': self.current_page,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
        }

if __name__ == '__main__':
    extractor = StarReportAutoExtractor()
    print("Star Report Auto Extractor")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total pages to process: {extractor.total_pages}")
    print()
    print("This script should be called by the main agent through MCP tools")
    print()
    print("Scripts ready:")
    print(f"- Init script: {len(extractor.get_init_script())} chars")
    print(f"- Extract script: {len(extractor.get_extract_script())} chars")
    print(f"- Next page script: {len(extractor.get_next_page_script())} chars")