/**
 * 星广报表数据提取脚本
 * 功能：
 * 1. 使用DOM遍历提取当前页面表格数据
 * 2. 循环处理所有39页数据
 * 3. 筛选消耗>2000的记录
 * 4. 输出JSON格式结果
 */

// 提取当前页面表格数据的函数
async function extractCurrentPageData() {
    const script = `
        (function() {
            // 查找表格元素 - 使用多种选择器确保找到表格
            let table = document.querySelector('table');
            if (!table) {
                table = document.querySelector('.ant-table table');
            }
            if (!table) {
                table = document.querySelector('[role="table"]');
            }
            
            if (!table) {
                return { error: '未找到表格元素' };
            }
            
            // 获取所有行
            const allRows = Array.from(table.querySelectorAll('tr'));
            
            // 跳过前两行（汇总行和表头）
            const dataRows = allRows.slice(2);
            
            const extractedData = [];
            
            for (const row of dataRows) {
                const cells = Array.from(row.querySelectorAll('td, th'));
                
                if (cells.length < 11) continue;
                
                // 提取11列数据
                const rowData = {
                    '素材ID（巨量）': cells[0]?.textContent?.trim() || '',
                    '标题': cells[1]?.textContent?.trim() || '',
                    '星图任务ID': cells[2]?.textContent?.trim() || '',
                    '星图任务名称': cells[3]?.textContent?.trim() || '',
                    '抖音号昵称': cells[4]?.textContent?.trim() || '',
                    '抖音号': cells[5]?.textContent?.trim() || '',
                    '视频播放链接': cells[6]?.querySelector('a')?.href || cells[6]?.textContent?.trim() || '',
                    '下单账户名称': cells[7]?.textContent?.trim() || '',
                    '消耗': parseFloat(cells[8]?.textContent?.replace(/[¥,]/g, '')?.trim() || '0'),
                    '产品名称': cells[9]?.textContent?.trim() || '',
                    '数据统计日期': cells[10]?.textContent?.trim() || ''
                };
                
                extractedData.push(rowData);
            }
            
            return extractedData;
        })()
    `;
    
    const result = await tools.browser_evaluate({ script: `JSON.stringify(${script})` });
    return JSON.parse(result.content[0].text);
}

// 主执行流程
async function main() {
    const allData = [];
    
    // 1. 提取第一页数据
    text('开始提取第1页数据...');
    let pageData = await extractCurrentPageData();
    
    if (pageData.error) {
        text('错误: ' + pageData.error);
        return;
    }
    
    allData.push(...pageData);
    text(`第1页提取完成，获取 ${pageData.length} 条数据`);
    
    // 2. 获取页面快照，找到分页按钮
    const snap = await tools.browser_snapshot();
    text('页面快照已获取，需要查看分页按钮...');
    text(snap);
}

// 执行主函数
await main();