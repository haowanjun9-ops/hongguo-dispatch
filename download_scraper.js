// 简化版：翻页抓取并下载为 JSON
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
  
  // 自动下载 JSON 文件
  const blob = new Blob([JSON.stringify(allRows, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'table_data_all_pages.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  console.log('📁 JSON 文件已自动下载');
  
  // 同时保存到全局变量
  window.allScrapedData = allRows;
  console.log('💾 数据已保存到 window.allScrapedData 变量');
})();