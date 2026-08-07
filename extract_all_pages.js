// 提取所有页面数据的脚本

async function extractAllPages() {
    const allData = [];
    let currentPage = 1;
    let totalPages = 36; // 默认36页
    
    // 提取当前页数据
    function extractPageData() {
        const rows = document.querySelectorAll('table tbody tr');
        const data = [];
        
        for (let row of rows) {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 11) {
                const materialId = cells[0].textContent.trim();
                if (materialId === '汇总') continue;
                
                data.push({
                    materialId: materialId,
                    title: cells[1].textContent.trim(),
                    starTaskId: cells[2].textContent.trim(),
                    starTaskName: cells[3].textContent.trim(),
                    douyinNickname: cells[4].textContent.trim(),
                    douyinId: cells[5].textContent.trim(),
                    videoLink: cells[6].textContent.trim(),
                    orderAccount: cells[7].textContent.trim(),
                    cost: parseFloat(cells[8].textContent.trim()) || 0,
                    productName: cells[9].textContent.trim(),
                    statDate: cells[10].textContent.trim()
                });
            }
        }
        
        return data;
    }
    
    // 等待指定时间
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // 点击页码
    function clickPage(pageNum) {
        const pageButtons = document.querySelectorAll('li.number');
        for (let btn of pageButtons) {
            if (btn.textContent.trim() === String(pageNum)) {
                btn.click();
                return true;
            }
        }
        return false;
    }
    
    // 提取第一页
    allData.push(...extractPageData());
    console.log(`提取第1页: ${allData.length} 条记录`);
    
    // 遍历剩余页面
    for (let i = 2; i <= totalPages; i++) {
        await sleep(2000); // 等待2秒
        
        if (clickPage(i)) {
            await sleep(2000); // 等待页面加载
            
            const pageData = extractPageData();
            allData.push(...pageData);
            console.log(`提取第${i}页: ${pageData.length} 条记录，累计 ${allData.length} 条`);
        } else {
            console.log(`无法点击第${i}页，停止提取`);
            break;
        }
    }
    
    return allData;
}

// 执行提取
extractAllPages().then(data => {
    console.log(`\n总共提取 ${data.length} 条记录`);
    console.log('数据已准备好');
    
    // 保存到全局变量
    window.extractedData = data;
    
    // 筛选消耗大于2000的记录
    const highCostData = data.filter(item => item.cost > 2000);
    console.log(`消耗超过2000的记录: ${highCostData.length} 条`);
    
    return {
        total: data.length,
        highCost: highCostData.length,
        highCostData: highCostData
    };
});