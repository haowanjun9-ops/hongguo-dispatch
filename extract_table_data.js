// 全局存储所有数据
window.allTableData = [];

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
    if (row['素材ID(巨量)'] && row['素材ID(巨量)'] !== '汇总') {
      pageData.push(row);
    }
  }
  
  return pageData;
}

// 点击下一页并等待
async function goToNextPage() {
  const nextButton = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)');
  if (nextButton) {
    nextButton.click();
    await new Promise(resolve => setTimeout(resolve, 2000)); // 等待2秒
    return true;
  }
  return false;
}

// 主流程：遍历所有页面
async function collectAllData() {
  // 提取第一页数据
  const firstPageData = extractCurrentPageData();
  window.allTableData = window.allTableData.concat(firstPageData);
  
  let pageNum = 1;
  const maxPages = 38; // 从快照看到总共有38页
  
  while (pageNum < maxPages) {
    const hasNext = await goToNextPage();
    if (!hasNext) break;
    
    pageNum++;
    const pageData = extractCurrentPageData();
    window.allTableData = window.allTableData.concat(pageData);
    
    console.log(`已收集第 ${pageNum} 页数据，累计 ${window.allTableData.length} 条`);
  }
  
  return JSON.stringify({
    success: true,
    totalRecords: window.allTableData.length,
    data: window.allTableData
  });
}

// 执行
collectAllData().then(result => {
  console.log('数据收集完成:', result);
});