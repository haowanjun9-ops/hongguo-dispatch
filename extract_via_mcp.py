#!/usr/bin/env python3
"""
星广报表数据提取脚本 - 使用MCP浏览器工具
此脚本需要在 Trae IDE 环境中运行，使用 integrated_browser MCP 工具
"""

import json
import time

# 配置参数
TOTAL_PAGES = 52
WAIT_TIME = 2000  # 毫秒
OUTPUT_FILE = '/workspace/all_data.json'

# JavaScript 脚本
EXTRACT_DATA_JS = """
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

CLICK_NEXT_PAGE_JS = """
const nextBtn = document.querySelector('.arco-pagination-item-next');
if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
    nextBtn.click();
    return 'clicked';
}
return 'disabled';
"""

def main():
    """
    主函数 - 在 Trae IDE 中需要通过 MCP 工具调用
    """
    print("=" * 70)
    print("星广报表数据提取脚本")
    print("=" * 70)
    print(f"\n配置信息：")
    print(f"  - 总页数: {TOTAL_PAGES}")
    print(f"  - 每页等待时间: {WAIT_TIME}ms")
    print(f"  - 输出文件: {OUTPUT_FILE}")
    print("\n" + "=" * 70)

    print("\n使用说明：")
    print("此脚本需要配合 integrated_browser MCP 工具使用")
    print("\n在 Trae IDE 中，请按以下步骤操作：")
    print("\n【步骤1】提取第1页数据")
    print("  使用 run_mcp 工具调用 browser_evaluate:")
    print(f"  工具: integrated_browser.browser_evaluate")
    print(f"  参数: {{\"script\": {repr(EXTRACT_DATA_JS)}}}")

    print("\n【步骤2】点击下一页")
    print("  使用 run_mcp 工具调用 browser_evaluate:")
    print(f"  工具: integrated_browser.browser_evaluate")
    print(f"  参数: {{\"script\": {repr(CLICK_NEXT_PAGE_JS)}}}")

    print("\n【步骤3】等待页面加载")
    print("  使用 run_mcp 工具调用 browser_wait_for:")
    print(f"  工具: integrated_browser.browser_wait_for")
    print(f"  参数: {{\"selector\": \".arco-table-body\", \"timeout\": {WAIT_TIME}}}")

    print("\n【步骤4】重复步骤1-3直到处理完所有52页")

    print("\n" + "=" * 70)
    print("JavaScript 脚本内容：")
    print("\n【提取数据脚本】：")
    print(EXTRACT_DATA_JS)
    print("\n【点击下一页脚本】：")
    print(CLICK_NEXT_PAGE_JS)

    print("\n" + "=" * 70)
    print("\n注意：由于我无法直接访问 run_mcp 工具，您需要：")
    print("1. 在 Trae IDE 环境中手动调用 MCP 工具")
    print("2. 或者使用浏览器控制台运行 /workspace/extract_star_report.js")
    print("=" * 70)

if __name__ == "__main__":
    main()