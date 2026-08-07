// 提取所有表格数据的脚本
(async function() {
    const allData = [];
    const totalPages = 52;
    
    // 提取当前页面数据的函数
    function extractCurrentPageData() {
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
    }
    
    // 等待函数
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // 点击指定页码的函数
    async function clickPage(pageNum) {
        const pageLinks = document.querySelectorAll('.arco-pagination-item');
        for (let link of pageLinks) {
            if (link.textContent.trim() === String(pageNum)) {
                link.click();
                await sleep(2000); // 等待2秒让数据加载
                return true;
            }
        }
        return false;
    }
    
    // 提取第1页数据
    console.log('Extracting page 1...');
    const page1Data = extractCurrentPageData();
    allData.push(...page1Data);
    console.log(`Page 1 extracted: ${page1Data.length} records`);
    
    // 提取第2-52页数据
    for (let page = 2; page <= totalPages; page++) {
        console.log(`Extracting page ${page}...`);
        const clicked = await clickPage(page);
        
        if (clicked) {
            const pageData = extractCurrentPageData();
            allData.push(...pageData);
            console.log(`Page ${page} extracted: ${pageData.length} records`);
        } else {
            console.log(`Failed to click page ${page}`);
            break;
        }
    }
    
    return allData;
})();