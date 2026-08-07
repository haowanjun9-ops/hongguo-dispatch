#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化提取所有星广报表数据
"""
import json
import time
import csv
from datetime import datetime

class StarReportExtractor:
    def __init__(self):
        self.all_data = []
        self.total_pages = 52
        self.current_page = 0

    def get_extraction_script(self):
        """获取提取当前页面数据的JavaScript脚本"""
        return """
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

        return JSON.stringify({rowCount: rows.length, data: rows});
        """

    def get_click_next_script(self):
        """获取点击下一页的JavaScript脚本"""
        return """
        const nextBtn = document.querySelector('.arco-pagination-item-next');
        if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
            nextBtn.click();
            return 'clicked';
        }
        return 'disabled';
        """

    def process_page_data(self, page_num, data_str):
        """处理页面数据"""
        try:
            result = json.loads(data_str)
            if 'error' in result:
                print(f"Error on page {page_num}: {result['error']}")
                return False

            rows = result.get('data', [])
            self.all_data.extend(rows)
            self.current_page = page_num
            print(f"Page {page_num}: Extracted {len(rows)} records, Total: {len(self.all_data)}")
            return True
        except Exception as e:
            print(f"Error parsing page {page_num} data: {e}")
            return False

    def filter_cost_over_2000(self):
        """筛选消耗>2000的记录"""
        filtered = [row for row in self.all_data if row.get('cost', 0) > 2000]
        return filtered

    def save_to_csv(self, data, filename):
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

    def get_current_timestamp(self):
        """获取当前时间戳"""
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M")

    def get_current_date(self):
        """获取当前日期"""
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

if __name__ == '__main__':
    extractor = StarReportExtractor()
    print("Star Report Extractor initialized")
    print(f"Total pages to extract: {extractor.total_pages}")
    print(f"Current timestamp: {extractor.get_current_timestamp()}")