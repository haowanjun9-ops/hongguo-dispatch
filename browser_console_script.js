/**
 * 星广报表数据提取脚本 - 浏览器控制台版本
 * 
 * 使用方法：
 * 1. 打开 https://apex.whaleidea.cn/star/report
 * 2. 按 F12 打开开发者工具
 * 3. 切换到 Console 标签
 * 4. 复制并粘贴此脚本的全部内容
 * 5. 按回车执行
 */

(async function() {
    'use strict';
    
    // 存储所有数据的数组
    const allData = [];
    
    // 提取当前页面数据的函数
    function extractCurrentPageData() {
        // 查找表格 - 尝试多种选择器
        const table = document.querySelector('table') || 
                      document.querySelector('.ant-table table') ||
                      document.querySelector('[role="table"]');
        
        if (!table) {
            console.error('未找到表格元素');
            return [];
        }
        
        // 获取所有行
        const allRows = Array.from(table.querySelectorAll('tr'));
        
        // 跳过前两行（汇总行和表头）
        const dataRows = allRows.slice(2);
        
        const extracted = [];
        
        dataRows.forEach(row => {
            const cells = Array.from(row.querySelectorAll('td, th'));
            
            if (cells.length < 11) return;
            
            // 解析消耗字段的数值
            const costText = (cells[8]?.textContent || '0').trim();
            const costValue = parseFloat(costText.replace(/[¥,\s]/g, '')) || 0;
            
            // 提取11列数据
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
    }
    
    // 点击下一页的函数
    function clickNextPage() {
        // 尝试多种方式找到下一页按钮
        const nextButton = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)') ||
                          document.querySelector('[aria-label="Next Page"]') ||
                          document.querySelector('.ant-pagination-item-next:not(.ant-pagination-disabled)');
        
        if (nextButton && !nextButton.classList.contains('ant-pagination-disabled')) {
            nextButton.click();
            return true;
        }
        
        return false;
    }
    
    // 等待函数
    function wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // 主提取流程
    async function extractAllPages() {
        console.log('========================================');
        console.log('开始提取星广报表数据');
        console.log('========================================');
        
        const totalPages = 39;
        let currentPage = 1;
        let consecutiveErrors = 0;
        
        while (currentPage <= totalPages) {
            console.log(`正在提取第 ${currentPage}/${totalPages} 页数据...`);
            
            try {
                // 提取当前页面数据
                const pageData = extractCurrentPageData();
                
                if (pageData.length === 0) {
                    console.warn(`第 ${currentPage} 页没有提取到数据`);
                    consecutiveErrors++;
                    
                    if (consecutiveErrors >= 3) {
                        console.error('连续3页没有数据，停止提取');
                        break;
                    }
                } else {
                    allData.push(...pageData);
                    console.log(`✓ 第 ${currentPage} 页提取完成，获取 ${pageData.length} 条数据，累计 ${allData.length} 条`);
                    consecutiveErrors = 0;
                }
                
                if (currentPage < totalPages) {
                    // 点击下一页
                    const hasNext = clickNextPage();
                    
                    if (!hasNext) {
                        console.log('没有下一页了，停止提取');
                        break;
                    }
                    
                    // 等待数据加载（3秒）
                    await wait(3000);
                }
                
            } catch (error) {
                console.error(`第 ${currentPage} 页提取出错:`, error);
                consecutiveErrors++;
                
                if (consecutiveErrors >= 3) {
                    console.error('连续3次错误，停止提取');
                    break;
                }
            }
            
            currentPage++;
        }
        
        console.log('========================================');
        console.log(`数据提取完成！共获取 ${allData.length} 条数据`);
        console.log('========================================');
        
        // 筛选消耗>2000的记录
        const filteredData = allData.filter(row => row['消耗'] > 2000);
        console.log(`筛选完成！消耗>2000的记录共 ${filteredData.length} 条`);
        
        // 输出筛选结果
        console.log('========================================');
        console.log('筛选结果（消耗>2000的记录）：');
        console.log('========================================');
        console.table(filteredData);
        
        // 在控制台中输出JSON格式
        console.log('========================================');
        console.log('JSON格式数据：');
        console.log('========================================');
        console.log(JSON.stringify(filteredData, null, 2));
        
        // 将结果保存到全局变量，方便后续访问
        window.extractedData = {
            allData: allData,
            filteredData: filteredData,
            summary: {
                totalRecords: allData.length,
                filteredRecords: filteredData.length,
                totalPages: currentPage - 1
            }
        };
        
        console.log('========================================');
        console.log('数据已保存到 window.extractedData 变量');
        console.log('可以使用以下命令访问：');
        console.log('  window.extractedData.filteredData  // 筛选后的数据');
        console.log('  window.extractedData.allData       // 所有数据');
        console.log('========================================');
        
        return filteredData;
    }
    
    // 执行提取
    return await extractAllPages();
})();