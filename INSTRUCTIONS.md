# 星广报表数据提取 - 执行指南

## 概述
从 https://apex.whaleidea.cn/star/report 提取所有消耗>2000的记录

## 方法一：浏览器控制台直接执行（推荐）

### 步骤：
1. 确保浏览器已经打开并登录到星广报表页面
2. 按 `F12` 打开开发者工具
3. 切换到 `Console` 标签
4. 复制 `browser_console_script.js` 文件的全部内容
5. 粘贴到控制台并按回车执行
6. 脚本将自动：
   - 提取当前页面的表格数据
   - 点击下一页按钮
   - 等待数据加载
   - 重复直到所有39页都处理完成
   - 筛选消耗>2000的记录
   - 输出JSON格式的结果

### 查看结果：
执行完成后，可以通过以下方式查看结果：
```javascript
// 查看筛选后的数据
window.extractedData.filteredData

// 查看所有数据
window.extractedData.allData

// 查看统计信息
window.extractedData.summary
```

## 方法二：使用浏览器自动化工具

### 如果需要使用浏览器自动化工具（如 Puppeteer/Playwright）：

1. 安装依赖：
```bash
npm install puppeteer
```

2. 运行自动化脚本：
```bash
node puppeteer_extract.js
```

## 数据字段说明

提取的11列数据：
1. 素材ID（巨量）
2. 标题
3. 星图任务ID
4. 星图任务名称
5. 抖音号昵称
6. 抖音号
7. 视频播放链接
8. 下单账户名称
9. 消耗（数值类型）
10. 产品名称
11. 数据统计日期

## 注意事项

- 第一行通常是"汇总"行，脚本会自动跳过
- 消耗字段会自动解析为浮点数进行比较
- 视频播放链接列会提取URL地址
- 每次翻页后会等待3秒确保数据加载完成
- 所有数据都会保存在 `window.extractedData` 变量中