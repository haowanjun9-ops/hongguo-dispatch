// 提取表格数据的JavaScript脚本
function extractTableData() {
    const rows = document.querySelectorAll('table tbody tr');
    const data = [];
    
    rows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 11) {
            // 跳过汇总行
            const firstCell = cells[0].textContent.trim();
            if (firstCell === '汇总') return;
            
            const rowData = {
                materialId: cells[0].textContent.trim(), // 素材ID（巨量）
                title: cells[1].textContent.trim(), // 标题
                taskId: cells[2].textContent.trim(), // 星图任务ID
                taskName: cells[3].textContent.trim(), // 星图任务名称
                nickname: cells[4].textContent.trim(), // 抖音号昵称
                douyinId: cells[5].textContent.trim(), // 抖音号
                videoLink: cells[6].textContent.trim(), // 视频播放链接
                accountName: cells[7].textContent.trim(), // 下单账户名称
                cost: parseFloat(cells[8].textContent.trim()) || 0, // 消耗
                productName: cells[9].textContent.trim(), // 产品名称
                date: cells[10].textContent.trim() // 数据统计日期
            };
            data.push(rowData);
        }
    });
    
    return data;
}

extractTableData();