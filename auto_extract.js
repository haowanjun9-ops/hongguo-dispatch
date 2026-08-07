// 自动提取所有页面数据的脚本
// 将在浏览器中执行

(function() {
    // 存储所有数据
    window.ALL_DATA = [];
    window.CURRENT_PAGE = 1;
    window.TOTAL_PAGES = 52;

    // 提取当前页面数据的函数
    window.extractCurrentPageData = function() {
        const tbody = document.querySelector('.arco-table-body');
        if (!tbody) return [];

        const trs = tbody.querySelectorAll('tr.arco-table-tr');
        const rows = [];

        for (let i = 1; i < trs.length; i++) { // 跳过第一行汇总行
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
    };

    // 点击下一页的函数
    window.clickNextPage = function() {
        const nextBtn = document.querySelector('.arco-pagination-item-next:not(.arco-pagination-item-disabled)');
        if (nextBtn) {
            nextBtn.click();
            return true;
        }
        return false;
    };

    // 获取当前提取状态
    window.getExtractionStatus = function() {
        return {
            currentPage: window.CURRENT_PAGE,
            totalPages: window.TOTAL_PAGES,
            extractedRecords: window.ALL_DATA.length,
            lastUpdate: new Date().toISOString()
        };
    };

    // 获取所有已提取的数据
    window.getAllExtractedData = function() {
        return window.ALL_DATA;
    };

    console.log('Data extraction helper functions loaded.');
    console.log('Use: window.extractCurrentPageData(), window.clickNextPage(), window.getAllExtractedData()');
})();