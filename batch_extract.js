// 分批提取脚本 - 每次提取5页
// 将在浏览器中多次执行

(function() {
    // 初始化全局存储
    if (!window.ALL_DATA) {
        window.ALL_DATA = [];
        window.CURRENT_BATCH = 0;
        window.TOTAL_PAGES = 52;
        window.PAGES_PER_BATCH = 5;
        window.TOTAL_BATCHES = 11; // 52页 / 5页/批 ≈ 11批
    }

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

    // 提取一批数据（5页）
    async function extractBatch(batchNum) {
        const batchData = [];

        // 提取当前页
        const currentPageData = extractCurrentPageData();
        batchData.push(...currentPageData);

        // 提取接下来的4页
        for (let i = 1; i < 5; i++) {
            if (!clickNextPage()) break;
            await new Promise(resolve => setTimeout(resolve, 2000));

            const pageData = extractCurrentPageData();
            batchData.push(...pageData);
        }

        return batchData;
    }

    return 'Batch extraction functions loaded';
})();