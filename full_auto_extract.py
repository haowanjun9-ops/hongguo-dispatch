#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的自动化数据提取脚本
"""

# 提取所有数据的完整JavaScript脚本
COMPLETE_EXTRACTION_SCRIPT = """
(async function() {
    const totalPages = 52;
    const allData = [];

    function extractCurrentPageData() {
        const tbody = document.querySelector('.arco-table-body');
        if (!tbody) return [];

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

        return rows;
    }

    function clickNextPage() {
        const nextBtn = document.querySelector('.arco-pagination-item-next');
        if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
            nextBtn.click();
            return true;
        }
        return false;
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    try {
        // 提取第1页
        const page1Data = extractCurrentPageData();
        allData.push(...page1Data);
        console.log('Page 1: ' + page1Data.length + ' records');

        // 提取第2-52页
        for (let page = 2; page <= totalPages; page++) {
            if (!clickNextPage()) break;
            await sleep(2000);

            const pageData = extractCurrentPageData();
            allData.push(...pageData);
            console.log('Page ' + page + ': ' + pageData.length + ' records');
        }

        return JSON.stringify({
            success: true,
            totalRecords: allData.length,
            data: allData
        });

    } catch (error) {
        return JSON.stringify({
            success: false,
            error: error.message
        });
    }
})();
"""

print("=" * 60)
print("完整自动化数据提取脚本")
print("=" * 60)
print()
print("JavaScript脚本已准备就绪")
print("请在主程序中通过 run_mcp 执行以下脚本:")
print()
print(COMPLETE_EXTRACTION_SCRIPT)
print()
print("=" * 60)