# 星广报表数据提取 - 执行说明

## 当前状态
- ✅ 浏览器已打开并登录
- ✅ 已导航到星广报表页面
- ✅ 数据已加载，共52页
- ✅ 浏览器已锁定
- ⏳ 需要开始数据提取

## 执行方案

由于数据量大（52页），采用**逐页提取**策略：

### 步骤1: 提取第1页数据
执行脚本并保存结果

### 步骤2: 循环处理后续页面
对每一页：
1. 提取当前页数据
2. 点击下一页
3. 等待2秒
4. 重复

### 步骤3: 筛选并保存
筛选消耗>2000的记录，保存CSV

## JavaScript脚本

### 提取当前页数据
```javascript
const tbody = document.querySelector('.arco-table-body');
if (!tbody) return JSON.stringify({error: 'No tbody found'});

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

return JSON.stringify({success: true, page: window.CURRENT_PAGE || 1, rowCount: rows.length, data: rows});
```

### 点击下一页
```javascript
const nextBtn = document.querySelector('.arco-pagination-item-next');
if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
    nextBtn.click();
    window.CURRENT_PAGE = (window.CURRENT_PAGE || 1) + 1;
    return 'clicked';
}
return 'disabled';
```

## 预期结果
- 提取所有1024条记录（52页 × ~20条/页）
- 筛选出消耗>2000的记录
- 生成CSV文件和飞书消息

---
**执行时间**: 2026-08-07
**状态**: 准备执行