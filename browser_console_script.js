// 在浏览器控制台运行此脚本来提取所有星广报表数据

(async function extractStarReportData() {
    const results = [];
    let currentPage = 1;
    const totalPages = 38;

    console.log('=== 开始提取星广报表数据 ===');
    console.log(`总页数: ${totalPages}`);

    // 提取当前页数据
    function extractPageData() {
        const rows = document.querySelectorAll('table tbody tr');
        const data = [];

        rows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 11) {
                // 获取视频链接
                const videoLinkElement = cells[6].querySelector('a');
                const videoLink = videoLinkElement ? videoLinkElement.href : '';

                const rowData = {
                    '素材ID（巨量）': cells[0].innerText.trim(),
                    '标题': cells[1].innerText.trim(),
                    '星图任务ID': cells[2].innerText.trim(),
                    '星图任务名称': cells[3].innerText.trim(),
                    '抖音号昵称': cells[4].innerText.trim(),
                    '抖音号': cells[5].innerText.trim(),
                    '视频播放链接': videoLink,
                    '下单账户名称': cells[7].innerText.trim(),
                    '消耗': cells[8].innerText.trim(),
                    '产品名称': cells[9].innerText.trim(),
                    '数据统计日期': cells[10].innerText.trim()
                };

                data.push(rowData);
            }
        });

        return data;
    }

    // 点击下一页
    async function nextPage() {
        const nextBtn = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)');
        if (nextBtn) {
            nextBtn.click();
            // 等待页面加载
            await new Promise(resolve => setTimeout(resolve, 2500));
            return true;
        }
        return false;
    }

    // 主循环
    while (true) {
        console.log(`正在提取第 ${currentPage} 页数据...`);

        const pageData = extractPageData();
        results.push(...pageData);
        console.log(`✓ 第 ${currentPage} 页: ${pageData.length} 条记录, 累计: ${results.length} 条`);

        if (currentPage >= totalPages) {
            console.log('已到达最后一页');
            break;
        }

        const hasNext = await nextPage();
        if (!hasNext) {
            console.log('没有更多页面');
            break;
        }

        currentPage++;
    }

    console.log(`\n=== 提取完成 ===`);
    console.log(`总共提取 ${results.length} 条记录`);

    // 筛选消耗>2000的记录
    const filteredResults = results.filter(item => {
        try {
            const costStr = item['消耗'].replace(/[¥,]/g, '').trim();
            const cost = parseFloat(costStr);
            return cost > 2000;
        } catch (e) {
            return false;
        }
    });

    console.log(`筛选出 ${filteredResults.length} 条消耗>2000的记录`);

    // 保存到全局变量供后续使用
    window.starReportAllData = results;
    window.starReportFilteredData = filteredResults;

    // 创建CSV内容
    const headers = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', '抖音号',
                      '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期'];

    const csvContent = [
        headers.join(','),
        ...filteredResults.map(row =>
            headers.map(h => {
                let value = row[h] || '';
                // 处理CSV中的特殊字符
                if (value.includes(',') || value.includes('"') || value.includes('\n')) {
                    value = '"' + value.replace(/"/g, '""') + '"';
                }
                return value;
            }).join(',')
        )
    ].join('\n');

    // 创建下载链接
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `star_report_cost_over_2000_2026-08-10_${new Date().toTimeString().slice(0,8).replace(/:/g,'')}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    console.log('✓ CSV文件已下载');

    // 输出筛选结果
    if (filteredResults.length > 0) {
        console.log('\n=== 筛选结果 ===');
        filteredResults.forEach((item, index) => {
            console.log(`${index + 1}. ${item['抖音号昵称']} - ${item['标题']} - ¥${item['消耗']} - ${item['数据统计日期']}`);
        });

        console.log(`\n数据已保存到变量: window.starReportFilteredData`);
        console.log(`共 ${filteredResults.length} 条记录`);
    } else {
        console.log('\n无超2000消耗数据');
    }

    return {
        total: results.length,
        filtered: filteredResults.length,
        data: filteredResults
    };
})();