# 星广报表数据提取任务指南

## 任务概述

本指南用于从鲸准3.0系统的星广报表页面提取数据，筛选消耗>2000的记录，并发送飞书消息通知。

## 当前环境状态

- ✅ 浏览器已打开并登录成功
- ✅ 已导航到星广报表页面: https://apex.whaleidea.cn/star/report
- ✅ 数据已查询显示，共38页，750条记录
- ✅ 飞书CLI已安装并配置

## 解决方案

由于浏览器已锁定，我们提供以下几种方法完成任务：

### 方法一：浏览器控制台脚本（推荐）

**步骤：**

1. 在浏览器中按 `F12` 或右键点击页面选择"检查"
2. 切换到 `Console` (控制台) 标签
3. 复制 `/workspace/console_extract_complete.js` 文件的全部内容
4. 粘贴到控制台并按回车执行

**脚本功能：**
- 自动遍历所有38页数据
- 提取完整的表格数据
- 筛选消耗>2000的记录
- 自动下载CSV文件
- 数据保存到全局变量 `window.starReportFilteredData`

**执行时间：** 约2-3分钟（38页 × 2.5秒/页）

**输出文件：**
- 自动下载的CSV文件：`star_report_cost_over_2000_2026-08-10_XXXXXX.csv`
- 全局变量：`window.starReportAllData` (所有数据)
- 全局变量：`window.starReportFilteredData` (筛选后数据)

---

### 方法二：使用CDP WebSocket自动化脚本

如果需要自动化执行，可以使用提供的Python脚本：

```bash
# 安装依赖
pip install websockets requests

# 运行脚本（需要在已打开的浏览器上执行）
python /workspace/smart_extract.py
```

**注意：** 此方法需要浏览器在正确的页面，并且可能需要处理登录状态。

---

### 方法三：手动提取后处理

如果自动化不工作，可以：

1. 在浏览器控制台运行简化脚本提取当前页数据：
```javascript
// 提取当前页数据
const rows = document.querySelectorAll('table tbody tr');
const data = [];
rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length >= 11) {
        data.push({
            '素材ID（巨量）': cells[0].innerText.trim(),
            '标题': cells[1].innerText.trim(),
            '消耗': cells[8].innerText.trim(),
            '抖音号昵称': cells[4].innerText.trim(),
            '视频播放链接': cells[6].querySelector('a')?.href || '',
            '数据统计日期': cells[10].innerText.trim()
        });
    }
});
console.table(data);
console.log('数据已保存到变量: window.currentPageData');
window.currentPageData = data;
```

2. 手动翻页并重复提取
3. 合并数据后保存为JSON文件
4. 运行处理脚本：

```bash
python /workspace/process_and_send.py
```

---

## 数据处理和发送

### 步骤1: 数据保存

如果使用浏览器控制台脚本，提取完成后：

1. CSV文件会自动下载到浏览器默认下载目录
2. 数据也保存在全局变量中，可以导出：

```javascript
// 导出JSON数据
const data = JSON.stringify(window.starReportFilteredData, null, 2);
const blob = new Blob([data], {type: 'application/json'});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'star_report_filtered_data.json';
a.click();
```

### 步骤2: 处理数据并发送飞书消息

将JSON文件保存到 `/workspace/star_report_filtered_data.json`，然后运行：

```bash
python /workspace/process_and_send.py
```

**脚本功能：**
- 读取JSON数据
- 筛选消耗>2000的记录
- 生成CSV文件：`/workspace/star_report_cost_over_2000_2026-08-10_XXXXXX.csv`
- 发送飞书消息到群聊：`oc_74cf357efbbda7b35af5078abcb29bdb`

---

## 飞书消息格式

```
## 【消耗预警】星广报表实时消耗>2000
统计时间：2026-08-10 18:00

| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |
|-----------|------|------|---------|------|
| 小余爱追剧 | xxx | 13888.48 | [观看](https://v.douyin.com/abc/) | 2026-08-10 |
...

共N条记录消耗超过2000元
```

---

## 文件清单

### 浏览器脚本
- `/workspace/console_extract_complete.js` - 完整的浏览器控制台脚本（推荐）
- `/workspace/browser_console_script.js` - 简化版浏览器脚本

### Python脚本
- `/workspace/smart_extract.py` - CDP自动化提取脚本
- `/workspace/process_and_send.py` - 数据处理和飞书消息发送脚本
- `/workspace/complete_extract.py` - 备用CDP脚本
- `/workspace/final_extract.py` - 备用CDP脚本

---

## 常见问题

### Q1: 浏览器控制台脚本执行失败
**A:** 确保：
- 已正确登录鲸准系统
- 已导航到星广报表页面
- 数据已加载显示

### Q2: 数据提取不完整
**A:** 可能原因：
- 页面加载慢，可以增加等待时间
- 表格结构变化，需要调整选择器
- 需要登录状态，请先手动登录

### Q3: 飞书消息发送失败
**A:** 检查：
- 飞书CLI是否正确配置：`lark-cli auth status`
- 是否有发送消息的权限
- 群聊ID是否正确：`oc_74cf357efbbda7b35af5078abcb29bdb`

---

## 手动飞书消息发送

如果自动发送失败，可以手动发送：

```bash
lark-cli im +messages-send --as user --chat-id oc_74cf357efbbda7b35af5078abcb29bdb --markdown "$(cat message.txt)"
```

或者使用Python发送：

```python
import subprocess

message = """## 【消耗预警】星广报表实时消耗>2000
统计时间：2026-08-10 18:00

| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |
...
"""

subprocess.run([
    'lark-cli', 'im', '+messages-send',
    '--as', 'user',
    '--chat-id', 'oc_74cf357efbbda7b35af5078abcb29bdb',
    '--markdown', message
])
```

---

## 技术支持

如需帮助，请检查：
1. 浏览器控制台的错误信息
2. Python脚本的输出日志
3. 飞书CLI的权限和配置

---

**最后更新时间：** 2026-08-10