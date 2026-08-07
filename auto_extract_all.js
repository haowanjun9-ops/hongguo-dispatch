// 自动提取所有52页数据的完整脚本
// 在浏览器中执行此脚本

(async function() {
    try {
        const totalPages = 52;
        const allData = [];

        // 提取当前页面数据
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

        // 点击下一页
        function clickNextPage() {
            const nextBtn = document.querySelector('.arco-pagination-item-next');
            if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
                nextBtn.click();
                return true;
            }
            return false;
        }

        // 等待函数
        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        // 提取第1页数据
        console.log('[Extraction] Starting extraction from page 1');
        const page1Data = extractCurrentPageData();
        allData.push(...page1Data);
        console.log(`[Extraction] Page 1: ${page1Data.length} records, Total: ${allData.length}`);

        // 提取第2-52页数据
        for (let page = 2; page <= totalPages; page++) {
            // 点击下一页
            if (!clickNextPage()) {
                console.log(`[Extraction] No more pages at page ${page}, stopping.`);
                break;
            }

            // 等待页面加载
            await sleep(2000);

            // 提取数据
            const pageData = extractCurrentPageData();
            allData.push(...pageData);
            console.log(`[Extraction] Page ${page}: ${pageData.length} records, Total: ${allData.length}`);
        }

        console.log(`[Extraction] Completed! Total: ${allData.length} records`);

        // 将数据存储到全局变量
        window.STAR_REPORT_ALL_DATA = allData;

        // 返回结果
        return JSON.stringify({
            success: true,
            totalRecords: allData.length,
            message: 'All data extracted and stored in window.STAR_REPORT_ALL_DATA'
        });

    } catch (error) {
        return JSON.stringify({
            success: false,
            error: error.message,
            stack: error.stack
        });
    }
})();