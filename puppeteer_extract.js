/**
 * 浏览器自动化脚本 - 使用Puppeteer
 * 用于从星广报表提取所有消耗>2000的记录
 */

const puppeteer = require('puppeteer');

async function extractData() {
    console.log('启动浏览器...');
    
    const browser = await puppeteer.launch({
        headless: false, // 使用有头模式，可以看到浏览器操作
        defaultViewport: null,
        args: ['--start-maximized']
    });
    
    const page = await browser.newPage();
    
    // 如果需要，可以在这里设置已有的Cookie或登录状态
    
    console.log('导航到星广报表页面...');
    await page.goto('https://apex.whaleidea.cn/star/report', {
        waitUntil: 'networkidle2',
        timeout: 60000
    });
    
    // 等待表格加载
    console.log('等待表格数据加载...');
    await page.waitForSelector('table', { timeout: 30000 });
    await page.waitForTimeout(3000);
    
    const allData = [];
    const totalPages = 39;
    
    for (let currentPage = 1; currentPage <= totalPages; currentPage++) {
        console.log(`正在提取第 ${currentPage}/${totalPages} 页数据...`);
        
        // 提取当前页面数据
        const pageData = await page.evaluate(() => {
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
                const costValue = parseFloat(costText.replace(/[¥,\s]/g, '')) || 0;
                
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
        });
        
        if (pageData.error) {
            console.error('错误:', pageData.error);
            break;
        }
        
        allData.push(...pageData);
        console.log(`✓ 第 ${currentPage} 页提取完成，获取 ${pageData.length} 条数据，累计 ${allData.length} 条`);
        
        if (currentPage < totalPages) {
            // 点击下一页按钮
            const nextButtonClicked = await page.evaluate(() => {
                const nextButton = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)') ||
                                   document.querySelector('[aria-label="Next Page"]') ||
                                   document.querySelector('.ant-pagination-item-next:not(.ant-pagination-disabled)');
                
                if (nextButton && !nextButton.classList.contains('ant-pagination-disabled')) {
                    nextButton.click();
                    return true;
                }
                
                return false;
            });
            
            if (!nextButtonClicked) {
                console.log('没有下一页了，停止提取');
                break;
            }
            
            // 等待数据加载
            await page.waitForTimeout(3000);
        }
    }
    
    // 筛选消耗>2000的记录
    const filteredData = allData.filter(row => row['消耗'] > 2000);
    
    console.log('\n========================================');
    console.log('数据提取完成！');
    console.log(`总记录数: ${allData.length}`);
    console.log(`筛选后记录数 (消耗>2000): ${filteredData.length}`);
    console.log('========================================\n');
    
    // 输出JSON结果
    console.log('筛选结果（消耗>2000的记录）：');
    console.log(JSON.stringify(filteredData, null, 2));
    
    // 保存到文件
    const fs = require('fs');
    fs.writeFileSync('extracted_data_all.json', JSON.stringify(allData, null, 2));
    fs.writeFileSync('extracted_data_filtered.json', JSON.stringify(filteredData, null, 2));
    
    console.log('\n数据已保存到文件：');
    console.log('  - extracted_data_all.json (所有数据)');
    console.log('  - extracted_data_filtered.json (筛选后数据)');
    
    // 关闭浏览器
    // await browser.close();
    
    return filteredData;
}

// 执行提取
extractData().catch(console.error);