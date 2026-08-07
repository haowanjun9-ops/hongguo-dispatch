// 完整的自动化数据提取脚本
// 这个脚本需要在浏览器控制台中执行

(async function() {
    const totalPages = 52;
    const allData = [];
    let currentPage = 1;

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
    console.log('Extracting page 1...');
    const page1Data = extractCurrentPageData();
    allData.push(...page1Data);
    console.log(`Page 1 extracted: ${page1Data.length} records, Total: ${allData.length}`);

    // 提取第2-52页数据
    for (let page = 2; page <= totalPages; page++) {
        console.log(`Moving to page ${page}...`);

        // 点击下一页
        if (!clickNextPage()) {
            console.log(`Failed to click next page at page ${page}, stopping.`);
            break;
        }

        // 等待页面加载
        await sleep(2000);

        // 提取数据
        const pageData = extractCurrentPageData();
        allData.push(...pageData);
        console.log(`Page ${page} extracted: ${pageData.length} records, Total: ${allData.length}`);

        // 每10页输出一次进度
        if (page % 10 === 0) {
            console.log(`=== Progress: ${page}/${totalPages} pages completed ===`);
        }
    }

    console.log(`=== Extraction completed! Total records: ${allData.length} ===`);

    // 将数据存储到全局变量
    window.EXTRACTED_DATA = allData;

    // 输出JSON数据（由于数据量大，这里只输出前5条）
    console.log('Sample data (first 5 records):');
    console.log(JSON.stringify(allData.slice(0, 5), null, 2));

    return allData;
})();