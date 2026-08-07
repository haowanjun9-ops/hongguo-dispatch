/**
 * 星广报表数据提取脚本
 * 在浏览器控制台中运行此脚本，自动提取所有52页数据
 */

(async function() {
    console.log('开始提取星广报表数据...');
    console.log('=' .repeat(60));

    const allData = [];
    const totalPages = 52;
    let currentPage = 1;

    // 提取当前页表格数据的函数
    function extractCurrentPage() {
        const tbody = document.querySelector('.arco-table-body');
        if (!tbody) {
            console.error('未找到表格主体');
            return [];
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

        return rows;
    }

    // 点击下一页的函数
    function clickNextPage() {
        const nextBtn = document.querySelector('.arco-pagination-item-next');
        if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
            nextBtn.click();
            return true;
        }
        return false;
    }

    // 等待指定毫秒数
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // 主循环
    try {
        while (currentPage <= totalPages) {
            console.log(`正在处理第 ${currentPage}/${totalPages} 页...`);

            // 提取当前页数据
            const pageData = extractCurrentPage();
            console.log(`  提取到 ${pageData.length} 条记录`);
            allData.push(...pageData);

            // 如果不是最后一页，点击下一页
            if (currentPage < totalPages) {
                const clicked = clickNextPage();
                if (!clicked) {
                    console.warn('无法点击下一页，可能是已到最后一页');
                    break;
                }
                // 等待页面加载
                await sleep(2000);
            }

            currentPage++;
        }

        console.log('=' .repeat(60));
        console.log(`提取完成！总共 ${allData.length} 条记录`);

        // 将数据存储到全局变量，方便后续使用
        window.starReportData = allData;

        // 生成下载链接
        const dataStr = JSON.stringify(allData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'star_report_data.json';
        a.textContent = '点击下载星广报表数据 (JSON)';

        // 在控制台显示下载信息
        console.log('\n数据已保存到 window.starReportData 变量');
        console.log('您可以运行以下命令下载：');
        console.log('  copy(JSON.stringify(window.starReportData, null, 2))');
        console.log('\n或者在控制台中运行：');
        console.log('  document.body.appendChild(document.createElement("a")).download = "data.json"');

        // 自动触发下载
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('\n已自动触发下载！');

        return allData;
    } catch (error) {
        console.error('提取数据时发生错误:', error);
        console.log(`已提取 ${allData.length} 条记录，存储在 window.starReportData 中`);
        window.starReportData = allData;
        throw error;
    }
})();