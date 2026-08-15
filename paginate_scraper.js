// 自动翻页抓取脚本
// 在浏览器控制台中运行此脚本

(async function autoPaginate() {
  const allData = [];
  let currentPage = 1;
  const totalPages = 51;
  
  // 数据提取函数
  function extractTableData() {
    const rows = [];
    const allRows = document.querySelectorAll('tr');
    for (const tr of allRows) {
      const cells = tr.querySelectorAll('td');
      if (cells.length >= 11) {
        const firstCell = cells[0].textContent.trim();
        if (firstCell === '汇总') continue;
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
    return rows;
  }
  
  // 等待函数
  function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  // 点击页码并等待加载
  async function clickPage(pageNum) {
    // 查找页码按钮
    const pageButtons = document.querySelectorAll('.ant-pagination-item, .pagination-item, [class*="page"]');
    let targetButton = null;
    
    for (const btn of pageButtons) {
      if (btn.textContent.trim() === String(pageNum)) {
        targetButton = btn;
        break;
      }
    }
    
    if (!targetButton) {
      console.error(`未找到页码 ${pageNum} 的按钮`);
      return false;
    }
    
    // 点击页码
    targetButton.click();
    console.log(`已点击第 ${pageNum} 页`);
    
    // 等待页面加载（2-3秒）
    await wait(2500);
    
    return true;
  }
  
  // 主循环
  console.log('开始抓取数据...');
  console.log(`总页数: ${totalPages}`);
  
  // 先提取第一页数据
  const firstPageData = extractTableData();
  allData.push(...firstPageData);
  console.log(`第 1 页: 提取了 ${firstPageData.length} 条数据`);
  
  // 从第2页开始循环
  for (let page = 2; page <= totalPages; page++) {
    try {
      const success = await clickPage(page);
      
      if (success) {
        const pageData = extractTableData();
        allData.push(...pageData);
        console.log(`第 ${page} 页: 提取了 ${pageData.length} 条数据，总计: ${allData.length} 条`);
      } else {
        console.warn(`第 ${page} 页跳过`);
      }
      
      // 短暂延迟，避免请求过快
      await wait(500);
      
    } catch (error) {
      console.error(`第 ${page} 页处理出错:`, error);
    }
  }
  
  console.log('\n========================================');
  console.log(`抓取完成！总共 ${allData.length} 条数据`);
  console.log('========================================\n');
  
  // 输出结果到控制台
  console.log('完整数据（可复制）:');
  console.log(JSON.stringify(allData, null, 2));
  
  // 同时返回数据
  window.scrapedData = allData;
  console.log('\n数据已保存到 window.scrapedData 变量');
  console.log('可以使用以下代码下载为 JSON 文件:');
  console.log('const blob = new Blob([JSON.stringify(window.scrapedData, null, 2)], {type: "application/json"});');
  console.log('const url = URL.createObjectURL(blob);');
  console.log('const a = document.createElement("a"); a.href = url; a.download = "table_data.json"; a.click();');
  
  return allData;
})();