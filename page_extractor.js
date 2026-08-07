// 分页提取数据的JavaScript脚本

// 存储所有数据
window.allReportData = window.allReportData || [];

// 提取当前页数据
function extractCurrentPageData() {
    const rows = document.querySelectorAll('table tbody tr');
    const data = [];
    
    for (let row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 11) {
            const materialId = cells[0].textContent.trim();
            if (materialId === '汇总') continue;
            
            const costText = cells[8].textContent.trim();
            const cost = parseFloat(costText) || 0;
            
            data.push({
                materialId: materialId,
                title: cells[1].textContent.trim(),
                starTaskId: cells[2].textContent.trim(),
                starTaskName: cells[3].textContent.trim(),
                douyinNickname: cells[4].textContent.trim(),
                douyinId: cells[5].textContent.trim(),
                videoLink: cells[6].textContent.trim(),
                orderAccount: cells[7].textContent.trim(),
                cost: cost,
                productName: cells[9].textContent.trim(),
                statDate: cells[10].textContent.trim()
            });
        }
    }
    
    return data;
}

// 等待指定毫秒
function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 点击下一页
async function goToNextPage(currentPage) {
    const pageButtons = document.querySelectorAll('li.number');
    
    for (let btn of pageButtons) {
        if (btn.textContent.trim() === String(currentPage + 1)) {
            btn.click();
            await wait(3000); // 等待页面加载
            return true;
        }
    }
    
    // 尝试点击下一页箭头
    const nextBtn = document.querySelector('li.btn-next:not(.disabled)');
    if (nextBtn) {
        nextBtn.click();
        await wait(3000);
        return true;
    }
    
    return false;
}

// 主提取函数
async function extractAllPagesData() {
    const total = document.querySelector('.el-pagination__total');
    let totalItems = 0;
    if (total) {
        const match = total.textContent.match(/共\s*(\d+)\s*条/);
        if (match) {
            totalItems = parseInt(match[1]);
        }
    }
    
    console.log(`总记录数: ${totalItems}`);
    
    // 获取总页数
    const pageNumbers = Array.from(document.querySelectorAll('li.number'));
    let totalPages = 36;
    if (pageNumbers.length > 0) {
        totalPages = parseInt(pageNumbers[pageNumbers.length - 1].textContent.trim());
    }
    
    console.log(`总页数: ${totalPages}`);
    
    // 清空之前的数据
    window.allReportData = [];
    
    // 提取第一页
    const firstPageData = extractCurrentPageData();
    window.allReportData.push(...firstPageData);
    console.log(`第1页: ${firstPageData.length} 条, 累计: ${window.allReportData.length} 条`);
    
    // 提取剩余页面
    for (let i = 2; i <= totalPages; i++) {
        const success = await goToNextPage(i - 1);
        
        if (!success) {
            console.log(`无法翻到第${i}页，停止提取`);
            break;
        }
        
        await wait(2000); // 额外等待确保数据加载
        
        const pageData = extractCurrentPageData();
        window.allReportData.push(...pageData);
        console.log(`第${i}页: ${pageData.length} 条, 累计: ${window.allReportData.length} 条`);
        
        // 避免请求过多
        await wait(1000);
    }
    
    console.log(`\n提取完成! 共${window.allReportData.length}条记录`);
    
    // 筛选消耗超过2000的记录
    const highCost = window.allReportData.filter(item => item.cost > 2000);
    console.log(`消耗超过2000的记录: ${highCost.length} 条`);
    
    return {
        total: window.allReportData.length,
        highCost: highCost.length,
        highCostData: highCost
    };
}

// 执行提取
extractAllPagesData().then(result => {
    console.log('\n========== 提取结果 ==========');
    console.log(`总记录数: ${result.total}`);
    console.log(`消耗>2000: ${result.highCost}`);
    console.log('数据已存储在 window.allReportData 和 window.highCostData 中');
});