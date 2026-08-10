// 提取当前页面表格数据的函数
async function extractTableData() {
    const result = await tools.browser_evaluate({
        script: `JSON.stringify((() => {
            // 查找表格元素
            const table = document.querySelector('table');
            if (!table) return { error: '未找到表格' };
            
            // 获取所有行（包括thead和tbody中的）
            const allRows = Array.from(table.querySelectorAll('tr'));
            
            // 跳过第一行（汇总行）和表头行，从数据行开始提取
            const dataRows = allRows.slice(2); // 假设前两行是汇总和表头
            
            const extractedData = dataRows.map(row => {
                const cells = Array.from(row.querySelectorAll('td'));
                if (cells.length < 11) return null;
                
                // 11列数据：素材ID（巨量）、标题、星图任务ID、星图任务名称、抖音号昵称、抖音号、视频播放链接、下单账户名称、消耗、产品名称、数据统计日期
                return {
                    materialId: cells[0]?.textContent?.trim() || '',
                    title: cells[1]?.textContent?.trim() || '',
                    taskId: cells[2]?.textContent?.trim() || '',
                    taskName: cells[3]?.textContent?.trim() || '',
                    nickname: cells[4]?.textContent?.trim() || '',
                    douyinId: cells[5]?.textContent?.trim() || '',
                    videoLink: cells[6]?.querySelector('a')?.href || cells[6]?.textContent?.trim() || '',
                    accountName: cells[7]?.textContent?.trim() || '',
                    cost: parseFloat(cells[8]?.textContent?.trim() || '0'),
                    productName: cells[9]?.textContent?.trim() || '',
                    date: cells[10]?.textContent?.trim() || ''
                };
            }).filter(row => row !== null);
            
            return extractedData;
        })())`
    });
    
    return JSON.parse(result.content[0].text);
}

// 主执行流程
const allData = [];

// 提取第一页数据
text('开始提取第1页数据...');
const firstPageData = await extractTableData();
allData.push(...firstPageData);
text(\`第1页提取完成，获取 \${firstPageData.length} 条数据\`);

// 获取页面快照以找到分页按钮
const snap = await tools.browser_snapshot();
text(snap);