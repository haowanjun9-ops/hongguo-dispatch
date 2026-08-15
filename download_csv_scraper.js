// 翻页抓取并下载为 CSV 格式（Excel 友好）
// 在浏览器控制台中运行

(async () => {
  const allRows = [];
  
  // 提取当前页表格数据
  const extractData = () => {
    const rows = [];
    document.querySelectorAll('tr').forEach(tr => {
      const cells = tr.querySelectorAll('td');
      if (cells.length >= 11) {
        const firstCell = cells[0].textContent.trim();
        if (firstCell !== '汇总') {
          rows.push({
            materialId: cells[0].textContent.trim(),
            title: cells[1].textContent.trim(),
            taskId: cells[2].textContent.trim(),
            taskName: cells[3].textContent.trim(),
            douyinNickname: cells[4].textContent.trim(),
            douyinId: cells[5].textContent.trim(),
            videoUrl: cells[6].textContent.trim(),
            accountName: cells[7].textContent.trim(),
            cost: cells[8].textContent.trim(),
            productName: cells[9].textContent.trim(),
            date: cells[10].textContent.trim()
          });
        }
      }
    });
    return rows;
  };
  
  // 点击指定页码
  const goToPage = async (pageNum) => {
    const pageBtn = [...document.querySelectorAll('[class*="pagination"] button, [class*="pagination"] a, .ant-pagination-item')]
      .find(el => el.textContent.trim() === String(pageNum));
    
    if (pageBtn) {
      pageBtn.click();
      await new Promise(r => setTimeout(r, 2500)); // 等待2.5秒
      return true;
    }
    return false;
  };
  
  // 转换为 CSV
  const toCSV = (data) => {
    const headers = ['materialId', 'title', 'taskId', 'taskName', 'douyinNickname', 'douyinId', 'videoUrl', 'accountName', 'cost', 'productName', 'date'];
    const csvRows = [];
    
    // 添加表头（中文）
    csvRows.push(['素材ID', '标题', '任务ID', '任务名称', '抖音昵称', '抖音ID', '视频URL', '账户名称', '成本', '产品名称', '日期'].join(','));
    
    // 添加数据行
    data.forEach(row => {
      csvRows.push(headers.map(h => {
        let value = row[h] || '';
        // CSV 转义：如果包含逗号、引号或换行，需要用引号包裹
        if (value.includes(',') || value.includes('"') || value.includes('\n')) {
          value = '"' + value.replace(/"/g, '""') + '"';
        }
        return value;
      }).join(','));
    });
    
    return csvRows.join('\n');
  };
  
  console.log('🚀 开始抓取 1-51 页数据...');
  
  // 抓取第1页
  allRows.push(...extractData());
  console.log(`✅ 第1页完成，已抓取 ${allRows.length} 条`);
  
  // 抓取第2-51页
  for (let p = 2; p <= 51; p++) {
    if (await goToPage(p)) {
      const data = extractData();
      allRows.push(...data);
      console.log(`✅ 第${p}页完成，本页${data.length}条，总计${allRows.length}条`);
    } else {
      console.warn(`⚠️ 第${p}页未找到按钮，跳过`);
    }
  }
  
  console.log(`\n🎉 抓取完成！总计 ${allRows.length} 条数据`);
  
  // 生成并下载 CSV 文件
  const csvContent = toCSV(allRows);
  const BOM = '\uFEFF'; // UTF-8 BOM，确保 Excel 正确识别中文
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'table_data_all_pages.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  console.log('📁 CSV 文件已自动下载（UTF-8 编码，Excel 可直接打开）');
  
  // 同时保存到全局变量
  window.allScrapedData = allRows;
  window.allScrapedCSV = csvContent;
  console.log('💾 数据已保存到 window.allScrapedData 和 window.allScrapedCSV 变量');
})();