// 第一步：获取页面快照，了解表格结构和分页控件
const snap = await tools.browser_snapshot();
text(snap);