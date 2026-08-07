/**
 * 星广报表数据自动提取脚本 - 浏览器控制台版本
 * 
 * 使用方法：
 * 1. 在浏览器中打开 https://apex.whaleidea.cn/star/report
 * 2. 确保数据已加载，页面显示完整
 * 3. 按F12打开开发者工具，切换到Console（控制台）标签
 * 4. 将此整个脚本复制粘贴到控制台，按回车执行
 * 5. 等待脚本自动完成所有页面的提取（约2-3分钟）
 * 6. 完成后会弹出提示，数据保存在 window.ALL_DATA 中
 * 7. 使用 copy(window.ALL_DATA_JSON) 命令复制JSON数据
 * 8. 将数据保存到 /workspace/all_data.json 文件
 */

// 配置参数
const CONFIG = {
    totalPages: 52,
    waitTime: 2000,  // 毫秒
    minCost: 2000    // 筛选最小消耗值
};

// 初始化全局变量
window.CURRENT_PAGE = 1;
window.ALL_DATA = [];

console.log('========================================');
console.log('星广报表数据自动提取脚本');
console.log('========================================');
console.log(`总页数: ${CONFIG.totalPages}`);
console.log(`每页等待时间: ${CONFIG.waitTime}ms`);
console.log(`筛选条件: 消耗 > ${CONFIG.minCost}`);
console.log('========================================\n');

/**
 * 提取当前页面的数据
 */
function extractCurrentPage() {
    const tbody = document.querySelector('.arco-table-body');
    if (!tbody) {
        console.error('错误: 未找到表格主体元素');
        return { error: 'No tbody found', rowCount: 0 };
    }

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

    return { rowCount: rows.length, data: rows };
}

/**
 * 点击下一页按钮
 */
function clickNextPage() {
    const nextBtn = document.querySelector('.arco-pagination-item-next');
    if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
        nextBtn.click();
        window.CURRENT_PAGE++;
        return true;
    }
    return false;
}

/**
 * 延迟函数
 */
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 主提取函数
 */
async function extractAllPages() {
    console.log('开始提取数据...\n');
    
    let consecutiveErrors = 0;
    const maxErrors = 3;
    
    for (let pageNum = 1; pageNum <= CONFIG.totalPages; pageNum++) {
        try {
            // 提取当前页数据
            const result = extractCurrentPage();
            
            if (result.error) {
                console.error(`第 ${pageNum} 页提取失败: ${result.error}`);
                consecutiveErrors++;
                
                if (consecutiveErrors >= maxErrors) {
                    console.error('连续错误次数过多，停止提取');
                    break;
                }
                continue;
            }
            
            consecutiveErrors = 0;  // 重置错误计数
            
            // 保存数据
            window.ALL_DATA.push(...result.data);
            
            console.log(`✓ 第 ${pageNum}/${CONFIG.totalPages} 页: 提取 ${result.rowCount} 条记录，累计 ${window.ALL_DATA.length} 条`);
            
            // 如果不是最后一页，点击下一页
            if (pageNum < CONFIG.totalPages) {
                const clicked = clickNextPage();
                
                if (!clicked) {
                    console.log('\n已到达最后一页（按钮不可用）');
                    break;
                }
                
                // 等待页面加载
                await delay(CONFIG.waitTime);
            }
            
        } catch (error) {
            console.error(`第 ${pageNum} 页处理出错:`, error);
            consecutiveErrors++;
            
            if (consecutiveErrors >= maxErrors) {
                console.error('连续错误次数过多，停止提取');
                break;
            }
        }
    }
    
    // 提取完成
    console.log('\n========================================');
    console.log('数据提取完成！');
    console.log('========================================');
    console.log(`总记录数: ${window.ALL_DATA.length} 条`);
    
    // 筛选高消耗记录
    const highCostRecords = window.ALL_DATA.filter(row => row.cost > CONFIG.minCost);
    console.log(`消耗 > ${CONFIG.minCost} 的记录: ${highCostRecords.length} 条`);
    
    // 准备JSON数据
    window.ALL_DATA_JSON = JSON.stringify(window.ALL_DATA, null, 2);
    
    console.log('\n数据已准备好，使用以下命令复制:');
    console.log('  copy(window.ALL_DATA_JSON)');
    console.log('\n然后粘贴到文件: /workspace/all_data.json');
    console.log('========================================');
    
    return {
        total: window.ALL_DATA.length,
        highCost: highCostRecords.length,
        data: window.ALL_DATA
    };
}

// 执行提取
console.log('开始执行自动提取...\n');
extractAllPages().then(result => {
    console.log('\n✓ 脚本执行完毕');
}).catch(error => {
    console.error('脚本执行出错:', error);
});