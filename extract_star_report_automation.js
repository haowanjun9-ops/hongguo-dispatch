/**
 * 星广报表数据提取 - 完整自动化脚本
 *
 * 使用方法：
 * 1. 在星广报表页面（已登录并加载数据）
 * 2. 打开浏览器开发者工具（F12）
 * 3. 在Console标签中粘贴此脚本并回车
 * 4. 等待自动执行完成，数据将自动下载为JSON文件
 */

(async function autoExtractStarReport() {
    'use strict';

    // ==================== 配置区 ====================
    const CONFIG = {
        totalPages: 52,          // 总页数
        waitTime: 2000,          // 页面加载等待时间（毫秒）
        maxRetries: 3,           // 最大重试次数
        debug: true              // 是否显示调试信息
    };

    // ==================== 工具函数 ====================

    /**
     * 日志输出
     */
    function log(message, type = 'info') {
        const styles = {
            info: 'color: #2196F3; font-weight: bold',
            success: 'color: #4CAF50; font-weight: bold',
            warning: 'color: #FF9800; font-weight: bold',
            error: 'color: #F44336; font-weight: bold'
        };
        console.log(`%c[星广报表] ${message}`, styles[type] || styles.info);
    }

    /**
     * 等待函数
     */
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 等待表格加载
     */
    async function waitForTable() {
        const maxWait = 10000; // 最多等待10秒
        const startTime = Date.now();

        while (Date.now() - startTime < maxWait) {
            const tbody = document.querySelector('.arco-table-body');
            if (tbody) {
                const trs = tbody.querySelectorAll('tr.arco-table-tr');
                if (trs.length > 1) {
                    return true;
                }
            }
            await sleep(100);
        }
        return false;
    }

    // ==================== 核心功能函数 ====================

    /**
     * 提取当前页表格数据
     */
    function extractCurrentPageData() {
        try {
            const tbody = document.querySelector('.arco-table-body');
            if (!tbody) {
                log('未找到表格主体', 'error');
                return { error: 'No tbody found', data: [] };
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

            if (CONFIG.debug) {
                log(`提取到 ${rows.length} 条记录`, 'info');
            }

            return { rowCount: rows.length, data: rows };
        } catch (error) {
            log(`提取数据时发生错误: ${error.message}`, 'error');
            return { error: error.message, data: [] };
        }
    }

    /**
     * 点击下一页按钮
     */
    function goToNextPage() {
        try {
            const nextBtn = document.querySelector('.arco-pagination-item-next');

            if (!nextBtn) {
                log('未找到下一页按钮', 'warning');
                return false;
            }

            if (nextBtn.classList.contains('arco-pagination-item-disabled')) {
                log('已到达最后一页', 'warning');
                return false;
            }

            nextBtn.click();
            log('已点击下一页', 'info');
            return true;
        } catch (error) {
            log(`点击下一页时发生错误: ${error.message}`, 'error');
            return false;
        }
    }

    /**
     * 下载JSON文件
     */
    function downloadJSON(data, filename) {
        try {
            const dataStr = JSON.stringify(data, null, 2);
            const blob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.style.display = 'none';

            document.body.appendChild(a);
            a.click();

            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 100);

            log(`文件已下载: ${filename}`, 'success');
        } catch (error) {
            log(`下载文件时发生错误: ${error.message}`, 'error');
        }
    }

    // ==================== 主流程 ====================

    log('='.repeat(70), 'info');
    log('星广报表数据提取脚本启动', 'info');
    log('='.repeat(70), 'info');
    log(`配置: 总页数=${CONFIG.totalPages}, 等待时间=${CONFIG.waitTime}ms`, 'info');

    const allData = [];
    let currentPage = 1;
    let retryCount = 0;

    try {
        while (currentPage <= CONFIG.totalPages) {
            log(`处理第 ${currentPage}/${CONFIG.totalPages} 页`, 'info');

            // 等待表格加载
            const tableReady = await waitForTable();
            if (!tableReady) {
                retryCount++;
                log(`表格加载失败，重试 ${retryCount}/${CONFIG.maxRetries}`, 'warning');

                if (retryCount >= CONFIG.maxRetries) {
                    log('超过最大重试次数，停止提取', 'error');
                    break;
                }

                await sleep(CONFIG.waitTime);
                continue;
            }

            retryCount = 0; // 重置重试计数

            // 提取数据
            const result = extractCurrentPageData();

            if (result.error) {
                log(`第 ${currentPage} 页提取失败: ${result.error}`, 'error');
            } else {
                allData.push(...result.data);
                log(`第 ${currentPage} 页成功，累计 ${allData.length} 条记录`, 'success');
            }

            // 如果不是最后一页，进入下一页
            if (currentPage < CONFIG.totalPages) {
                const clicked = goToNextPage();

                if (!clicked) {
                    log('无法进入下一页，可能已到末尾', 'warning');
                    break;
                }

                // 等待页面加载
                await sleep(CONFIG.waitTime);
            }

            currentPage++;
        }

        log('='.repeat(70), 'info');
        log(`提取完成！`, 'success');
        log(`总页数: ${currentPage - 1}`, 'success');
        log(`总记录: ${allData.length}`, 'success');
        log('='.repeat(70), 'info');

        // 保存到全局变量
        window.starReportAllData = allData;
        log('数据已保存到 window.starReportAllData', 'info');

        // 自动下载
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const filename = `star_report_${timestamp}.json`;
        downloadJSON(allData, filename);

        // 显示使用提示
        log('\n使用提示:', 'info');
        log('- 数据已自动下载为JSON文件', 'info');
        log('- 可以通过 window.starReportAllData 访问数据', 'info');
        log('- 可以运行 copy(JSON.stringify(window.starReportAllData, null, 2)) 复制数据', 'info');

        return allData;

    } catch (error) {
        log('='.repeat(70), 'error');
        log(`执行过程中发生错误: ${error.message}`, 'error');
        log(`已提取 ${allData.length} 条记录`, 'warning');
        log('='.repeat(70), 'error');

        // 保存已提取的数据
        window.starReportAllData = allData;
        log('已提取的数据保存在 window.starReportAllData', 'warning');

        throw error;
    }
})();