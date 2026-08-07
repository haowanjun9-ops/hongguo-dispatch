#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示版本 - 提取前10页数据
"""
import json
import csv
from datetime import datetime

# 提取脚本
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

return JSON.stringify({success: true, rowCount: rows.length, data: rows});
"""

# 点击下一页脚本
NEXT_PAGE_SCRIPT = """
const nextBtn = document.querySelector('.arco-pagination-item-next');
if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
    nextBtn.click();
    return 'clicked';
}
return 'disabled';
"""

def process_page(json_str, all_data, filtered_data):
    """处理一页数据"""
    try:
        result = json.loads(json_str)

        if 'error' in result:
            return False, result['error']

        data = result.get('data', [])

        all_data.extend(data)

        # 筛选消耗>2000
        page_filtered = [row for row in data if row.get('cost', 0) > 2000]
        filtered_data.extend(page_filtered)

        return True, {
            'extracted': len(data),
            'filtered': len(page_filtered),
            'total': len(all_data),
            'total_filtered': len(filtered_data)
        }

    except Exception as e:
        return False, str(e)

def save_results(all_data, filtered_data):
    """保存结果"""
    # 保存所有数据
    with open('/workspace/all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Saved {len(all_data)} total records")

    # 保存筛选后的数据
    if filtered_data:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"

        fieldnames = ['materialId', 'title', 'taskId', 'taskName', 'douyinNickname',
                      'douyinId', 'videoUrl', 'accountName', 'cost', 'productName', 'date']

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_data)

        print(f"✓ Saved {len(filtered_data)} filtered records")
        return filename

    return None

if __name__ == '__main__':
    print("数据提取演示脚本")
    print("此脚本通过主程序调用run_mcp工具执行")
    print()
    print("脚本准备就绪:")
    print(f"- EXTRACT_SCRIPT: {len(EXTRACT_SCRIPT)} 字符")
    print(f"- NEXT_PAGE_SCRIPT: {len(NEXT_PAGE_SCRIPT)} 字符")