/**
 * 完整的浏览器自动化脚本
 * 使用 integrated_code_mode 的 Exec 工具来执行浏览器操作
 * 
 * 这个脚本需要在浏览器环境中通过 browser_evaluate 执行
 */

// 全局变量存储所有数据
const allData = [];

// 提取当前页面数据的函数（将在浏览器页面上下文中执行）
const extractPageDataScript = `
(function() {
    // 查找表格
    const table = document.querySelector('table') || 
                  document.querySelector('.ant-table table') ||
                  document.querySelector('[role="table"]');
    
    if (!table) {
        return { error: '未找到表格元素' };
    }
    
    // 获取所有行
    const allRows = Array.from(table.querySelectorAll('tr'));
    
    // 跳过前两行（汇总行和表头）
    const dataRows = allRows.slice(2);
    
    const extracted = [];
    
    dataRows.forEach(row => {
        const cells = Array.from(row.querySelectorAll('td, th'));
        
        if (cells.length < 11) return;
        
        // 解析消耗字段
        const costText = (cells[8]?.textContent || '0').trim();
        const costValue = parseFloat(costText.replace(/[¥,\\s]/g, '')) || 0;
        
        const rowData = {
            '素材ID（巨量）': (cells[0]?.textContent || '').trim(),
            '标题': (cells[1]?.textContent || '').trim(),
            '星图任务ID': (cells[2]?.textContent || '').trim(),
            '星图任务名称': (cells[3]?.textContent || '').trim(),
            '抖音号昵称': (cells[4]?.textContent || '').trim(),
            '抖音号': (cells[5]?.textContent || '').trim(),
            '视频播放链接': cells[6]?.querySelector('a')?.href || (cells[6]?.textContent || '').trim(),
            '下单账户名称': (cells[7]?.textContent || '').trim(),
            '消耗': costValue,
            '产品名称': (cells[9]?.textContent || '').trim(),
            '数据统计日期': (cells[10]?.textContent || '').trim()
        };
        
        extracted.push(rowData);
    });
    
    return extracted;
})()
`;

// 主执行脚本
async function main() {
    const totalPages = 39;
    
    for (let currentPage = 1; currentPage <= totalPages; currentPage++) {
        text(`正在提取第 ${currentPage}/${totalPages} 页数据...`);
        
        // 提取当前页面数据
        const pageDataResult = await tools.browser_evaluate({
            script: `JSON.stringify(${extractPageDataScript})`
        });
        
        const pageData = JSON.parse(pageDataResult.content[0].text);
        
        if (pageData.error) {
            text(`错误: ${pageData.error}`);
            break;
        }
        
        allData.push(...pageData);
        text(`✓ 第 ${currentPage} 页提取完成，获取 ${pageData.length} 条数据，累计 ${allData.length} 条`);
        
        if (currentPage < totalPages) {
            // 获取页面快照以找到下一页按钮
            const snap = await tools.browser_snapshot();
            
            // 在快照中查找下一页按钮
            // 这里需要从快照中解析出下一页按钮的ref
            text('需要从快照中找到下一页按钮...');
            text(snap);
            
            // 点击下一页按钮（假设ref为某个值，需要从快照中获取）
            // await tools.browser_click({ ref: "XX" });
            
            // 等待数据加载
            await tools.browser_wait_for({ time: 3 });
        }
    }
    
    // 筛选消耗>2000的记录
    const filteredData = allData.filter(row => row['消耗'] > 2000);
    
    text(`========================================`);
    text(`数据提取完成！`);
    text(`总记录数: ${allData.length}`);
    text(`筛选后记录数 (消耗>2000): ${filteredData.length}`);
    text(`========================================`);
    
    // 输出JSON结果
    text(JSON.stringify(filteredData, null, 2));
}

// 执行主函数
await main();