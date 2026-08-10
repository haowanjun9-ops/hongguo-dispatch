// 全局变量存储所有数据
if (!window.allDataExtracted) {
    window.allDataExtracted = [];
}

// 提取当前页数据的函数
function extractCurrentPageData() {
    const headers = Array.from(document.querySelectorAll('table thead th')).map(th => th.textContent.trim());
    const allCells = Array.from(document.querySelectorAll('table tbody tr td'));
    const colsPerRow = 11;
    const totalRows = Math.floor(allCells.length / colsPerRow);
    const pageData = [];

    for (let i = 1; i < totalRows; i++) { // 跳过第一行(汇总行)
        const row = {};
        for (let j = 0; j < colsPerRow; j++) {
            const cellIndex = i * colsPerRow + j;
            if (cellIndex < allCells.length) {
                row[headers[j]] = allCells[cellIndex].textContent.trim();
            }
        }
        if (row['素材ID（巨量）'] && row['素材ID（巨量）'] !== '汇总') {
            pageData.push(row);
        }
    }

    return pageData;
}

// 一次性提取所有页面的数据
(async function extractAllPages() {
    console.log('🚀 开始提取所有页面数据...');

    const allData = [];
    let currentPage = 1;

    // 提取第一页
    console.log(`📖 提取第 ${currentPage} 页...`);
    const firstPageData = extractCurrentPageData();
    allData.push(...firstPageData);
    console.log(`✅ 第1页: ${firstPageData.length} 条记录`);

    // 循环提取剩余页面
    for (let p = 2; p <= 38; p++) {
        // 点击下一页
        const nextBtn = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)');
        if (!nextBtn) {
            console.log('ℹ️ 没有下一页了');
            break;
        }

        nextBtn.click();

        // 等待页面加载
        await new Promise(resolve => setTimeout(resolve, 2500));

        // 提取数据
        const pageData = extractCurrentPageData();
        allData.push(...pageData);
        currentPage = p;
        console.log(`✅ 第${p}页: ${pageData.length} 条记录 (累计: ${allData.length} 条)`);

        // 每10页保存一次到全局变量
        if (p % 10 === 0) {
            window.allDataExtracted = [...allData];
            console.log(`💾 已保存${allData.length}条数据到window.allDataExtracted`);
        }
    }

    // 最终保存
    window.allDataExtracted = [...allData];
    console.log(`\n✅ 完成！共提取 ${allData.length} 条记录`);

    // 筛选消耗>2000的记录
    const filtered = allData.filter(row => {
        const cost = parseFloat(row['消耗'] || '0');
        return cost > 2000;
    });

    console.log(`🔍 筛选结果: ${filtered.length} 条消耗>2000的记录`);
    window.filteredDataExtracted = filtered;

    // 生成CSV内容
    if (filtered.length > 0) {
        const headers = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', '抖音号', '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期'];
        const csvRows = [headers.join(',')];

        filtered.forEach(row => {
            const values = headers.map(h => {
                let val = row[h] || '';
                if (val.includes(',') || val.includes('"') || val.includes('\n')) {
                    val = '"' + val.replace(/"/g, '""') + '"';
                }
                return val;
            });
            csvRows.push(values.join(','));
        });

        window.csvContent = '\ufeff' + csvRows.join('\n');
        console.log('📝 CSV内容已生成，保存在window.csvContent');
    }

    return {
        success: true,
        totalRecords: allData.length,
        filteredRecords: filtered.length
    };
})();