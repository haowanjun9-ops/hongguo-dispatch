# 星广报表数据提取方案

## 📋 任务概述

从星广报表（https://apex.whaleidea.cn/star/report）提取所有52页数据，共约1040条记录（52页 × 20条/页）。

## 🚀 快速使用方法

### 方法一：浏览器控制台自动化（推荐）

1. **在报表页面按 F12 打开开发者工具**
2. **切换到 Console（控制台）标签**
3. **复制并粘贴以下文件的全部内容：**
   ```
   /workspace/extract_star_report_automation.js
   ```
4. **按回车执行**
5. **等待自动完成，数据将自动下载**

**预计耗时：** 约2分钟（52页 × 2秒/页）

### 方法二：手动分步提取

如需逐页验证，可运行：
```bash
python3 /workspace/extract_via_mcp.py
```

按照提示手动操作。

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `extract_star_report_automation.js` | ✅ 推荐使用 - 浏览器控制台完整自动化脚本 |
| `extract_via_mcp.py` | Python辅助脚本，显示MCP工具调用方法 |
| `extract_star_report.py` | Python基础脚本，显示JavaScript代码 |

## 🎯 数据提取内容

每条记录包含以下11个字段：
- materialId: 物料ID
- title: 标题
- taskId: 任务ID
- taskName: 任务名称
- douyinNickname: 抖音昵称
- douyinId: 抖音ID
- videoUrl: 视频链接
- accountName: 账户名称
- cost: 成本（数值型）
- productName: 产品名称
- date: 日期

## ⚙️ 脚本功能特性

✅ **自动翻页** - 自动点击下一页按钮
✅ **智能等待** - 等待表格数据加载完成
✅ **错误处理** - 失败自动重试（最多3次）
✅ **进度显示** - 实时显示当前页数和累计记录数
✅ **自动下载** - 完成后自动下载JSON文件
✅ **数据备份** - 同时保存在浏览器全局变量

## 📊 输出文件

- **文件名格式：** `star_report_YYYY-MM-DDTHH-MM-SS.json`
- **保存位置：** 浏览器默认下载目录
- **数据格式：** JSON数组，每条记录为一个对象

## 🔧 故障排查

### 问题：脚本运行后立即停止
**解决方案：** 确保在报表页面（已登录）且数据已加载

### 问题：提示"未找到表格主体"
**解决方案：**
1. 确认已点击查询按钮
2. 等待表格完全加载后再运行脚本

### 问题：翻页中途停止
**解决方案：**
- 已提取的数据保存在 `window.starReportAllData`
- 可以运行 `copy(JSON.stringify(window.starReportAllData, null, 2))` 复制已提取数据

## 💡 使用提示

脚本执行完成后，可以通过以下方式访问数据：

1. **已下载的JSON文件** - 直接使用
2. **浏览器控制台：**
   ```javascript
   // 查看数据
   console.log(window.starReportAllData);

   // 复制数据到剪贴板
   copy(JSON.stringify(window.starReportAllData, null, 2));

   // 查看记录总数
   console.log('总记录数:', window.starReportAllData.length);
   ```

## 🎉 完成状态

数据提取完成后将显示：
```
提取完成！
总页数: 52
总记录: [实际记录数]
文件已下载: star_report_[时间戳].json
```

---

**建议：** 使用方法一（浏览器控制台自动化），最简单高效！