// ========================================
// 星广报表数据提取脚本 - 浏览器控制台版本
// ========================================
//
// 使用方法：
// 1. 确保已打开星广报表页面: https://apex.whaleidea.cn/star/report
// 2. 打开浏览器开发者工具 (F12 或 右键 -> 检查)
// 3. 切换到 Console (控制台) 标签
// 4. 复制整个脚本内容并粘贴到控制台
// 5. 按回车键执行
//
// 脚本将自动：
// - 遍历所有38页数据
// - 提取表格中的所有记录
// - 筛选消耗>2000的记录
// - 自动下载CSV文件
// ========================================

(async function extractStarReportData() {
    console.log('🚀 开始执行星广报表数据提取脚本...');
    console.log('📍 当前页面:', window.location.href);

    // 检查是否在正确的页面
    if (!window.location.href.includes('apex.whaleidea.cn/star/report')) {
        console.error('❌ 错误: 请先导航到星广报表页面');
        console.log('📝 目标页面: https://apex.whaleidea.cn/star/report');
        return;
    }

    const allData = [];
    let currentPage = 1;
    const totalPages = 38;
    let consecutiveErrors = 0;
    const maxErrors = 3;

    console.log(`📊 预计总页数: ${totalPages}`);
    console.log('⏳ 开始提取数据...\n');

    // 提取当前页数据的函数
    function extractCurrentPageData() {
        try {
            const rows = document.querySelectorAll('table tbody tr');

            if (rows.length === 0) {
                console.warn('⚠️ 未找到表格行数据');
                return [];
            }

            const pageData = [];

            rows.forEach((row, index) => {
                const cells = row.querySelectorAll('td');

                if (cells.length >= 11) {
                    try {
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

                        pageData.push(rowData);
                    } catch (e) {
                        console.warn(`⚠️ 第 ${index + 1} 行数据提取失败:`, e.message);
                    }
                }
            });

            return pageData;
        } catch (e) {
            console.error('❌ 提取数据时发生错误:', e);
            return [];
        }
    }

    // 点击下一页的函数
    async function clickNextPage() {
        try {
            const nextButton = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)');

            if (!nextButton) {
                console.log('ℹ️ 没有找到下一页按钮');
                return false;
            }

            // 检查按钮是否可点击
            if (nextButton.classList.contains('ant-pagination-disabled')) {
                console.log('ℹ️ 下一页按钮已禁用');
                return false;
            }

            // 点击下一页
            nextButton.click();

            // 等待页面加载
            await new Promise(resolve => setTimeout(resolve, 2500));

            // 验证页面是否已加载
            const rows = document.querySelectorAll('table tbody tr');
            if (rows.length === 0) {
                console.warn('⚠️ 翻页后未找到数据,等待更长时间...');
                await new Promise(resolve => setTimeout(resolve, 1500));
            }

            return true;
        } catch (e) {
            console.error('❌ 翻页时发生错误:', e);
            return false;
        }
    }

    // 主循环
    while (true) {
        console.log(`📖 正在提取第 ${currentPage} 页...`);

        const pageData = extractCurrentPageData();

        if (pageData.length === 0) {
            consecutiveErrors++;
            console.warn(`⚠️ 第 ${currentPage} 页没有数据 (${consecutiveErrors}/${maxErrors})`);

            if (consecutiveErrors >= maxErrors) {
                console.error('❌ 连续多次提取失败,停止执行');
                break;
            }
        } else {
            consecutiveErrors = 0; // 重置错误计数
            allData.push(...pageData);
            console.log(`✅ 第 ${currentPage} 页: ${pageData.length} 条记录 (累计: ${allData.length} 条)`);
        }

        // 检查是否到达最后一页
        if (currentPage >= totalPages) {
            console.log('\n✅ 已处理完所有页面');
            break;
        }

        // 点击下一页
        const hasNext = await clickNextPage();

        if (!hasNext) {
            console.log('\nℹ️ 已到达最后一页');
            break;
        }

        currentPage++;
    }

    console.log(`\n📊 提取完成! 总共 ${allData.length} 条记录`);

    // 筛选消耗>2000的记录
    console.log('\n🔍 开始筛选消耗>2000的记录...');

    const filteredData = allData.filter(item => {
        try {
            // 清理消耗字符串
            const costStr = item['消耗']
                .replace(/[¥￥,，元]/g, '')
                .trim();

            const cost = parseFloat(costStr);

            if (isNaN(cost)) {
                // 尝试提取数字
                const match = item['消耗'].match(/(\d+\.?\d*)/);
                if (match) {
                    return parseFloat(match[1]) > 2000;
                }
                return false;
            }

            return cost > 2000;
        } catch (e) {
            return false;
        }
    });

    console.log(`✅ 筛选完成: ${filteredData.length} 条消耗>2000的记录`);

    // 保存到全局变量
    window.starReportAllData = allData;
    window.starReportFilteredData = filteredData;

    if (filteredData.length === 0) {
        console.log('\n⚠️ 无超2000消耗数据');
        return {
            success: true,
            totalRecords: allData.length,
            filteredRecords: 0,
            message: '无超2000消耗数据'
        };
    }

    // 创建CSV内容
    console.log('\n📝 生成CSV文件...');

    const headers = [
        '素材ID（巨量）', '标题', '星图任务ID', '星图任务名称',
        '抖音号昵称', '抖音号', '视频播放链接',
        '下单账户名称', '消耗', '产品名称', '数据统计日期'
    ];

    const csvRows = [headers.join(',')];

    filteredData.forEach(row => {
        const values = headers.map(header => {
            let value = row[header] || '';

            // 处理CSV中的特殊字符
            if (value.includes(',') || value.includes('"') || value.includes('\n')) {
                value = '"' + value.replace(/"/g, '""') + '"';
            }

            return value;
        });

        csvRows.push(values.join(','));
    });

    const csvContent = '\ufeff' + csvRows.join('\n');

    // 下载CSV文件
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    const timestamp = new Date().toTimeString().slice(0, 8).replace(/:/g, '');
    link.href = url;
    link.download = `star_report_cost_over_2000_2026-08-10_${timestamp}.csv`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    console.log('✅ CSV文件已下载');

    // 显示筛选结果摘要
    console.log('\n========== 筛选结果摘要 ==========');
    console.log(`总记录数: ${allData.length}`);
    console.log(`筛选记录数: ${filteredData.length}`);
    console.log(`CSV文件名: ${link.download}`);

    console.log('\n前5条记录:');
    filteredData.slice(0, 5).forEach((item, index) => {
        console.log(`${index + 1}. ${item['抖音号昵称']} | ${item['标题'].substring(0, 20)}... | ¥${item['消耗']} | ${item['数据统计日期']}`);
    });

    console.log('\n📊 数据已保存到变量:');
    console.log('  - window.starReportAllData (所有数据)');
    console.log('  - window.starReportFilteredData (筛选后数据)');

    console.log('\n✨ 任务完成!');

    return {
        success: true,
        totalRecords: allData.length,
        filteredRecords: filteredData.length,
        csvFilename: link.download,
        data: filteredData
    };
})();