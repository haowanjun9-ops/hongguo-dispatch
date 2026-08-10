#!/usr/bin/env python3
"""
使用CDP协议直接与浏览器交互
"""
import json
import time
import csv
import requests
from datetime import datetime

class BrowserController:
    def __init__(self, cdp_url="http://localhost:9222"):
        self.cdp_url = cdp_url
        self.session = requests.Session()

    def get_pages(self):
        """获取所有打开的页面"""
        response = self.session.get(f"{self.cdp_url}/json")
        if response.status_code == 200:
            return response.json()
        return []

    def find_target_page(self, url_pattern):
        """查找包含特定URL的页面"""
        pages = self.get_pages()
        for page in pages:
            if url_pattern in page.get('url', ''):
                return page
        return None

    def execute_script(self, page_id, script, timeout=30000):
        """在指定页面执行JavaScript脚本"""
        url = f"{self.cdp_url}/json"
        ws_url = None

        # 获取WebSocket URL
        pages = self.get_pages()
        for page in pages:
            if page.get('id') == page_id or (page_id is None and 'apex.whaleidea.cn' in page.get('url', '')):
                ws_url = page.get('webSocketDebuggerUrl')
                break

        if not ws_url:
            print("未找到WebSocket连接URL")
            return None

        # 由于直接使用WebSocket比较复杂,我们使用HTTP方式
        # 这里需要构建CDP命令
        try:
            # 使用requests发送POST请求
            cdp_endpoint = f"{self.cdp_url}/json"
            return self._send_cdp_command(page_id, script)
        except Exception as e:
            print(f"执行脚本失败: {e}")
            return None

    def _send_cdp_command(self, page_id, script):
        """发送CDP命令(简化版)"""
        # 这个方法需要WebSocket支持,这里简化处理
        pass

def extract_with_cdp():
    """使用CDP提取数据"""
    controller = BrowserController("http://localhost:9222")

    # 查找星广报表页面
    pages = controller.get_pages()
    print(f"找到 {len(pages)} 个浏览器页面")

    target_page = None
    for page in pages:
        print(f"页面: {page.get('url', 'N/A')[:80]}")
        if 'apex.whaleidea.cn/star/report' in page.get('url', ''):
            target_page = page
            break

    if not target_page:
        print("未找到星广报表页面")
        return None

    print(f"找到目标页面: {target_page['url']}")

    # 由于CDP直接调用比较复杂,我们返回页面信息
    # 实际执行需要在浏览器控制台运行脚本
    return target_page

def main():
    print("=== 星广报表数据提取工具 ===\n")

    # 尝试连接CDP
    page_info = extract_with_cdp()

    if page_info:
        print(f"\n浏览器已打开目标页面")
        print(f"请在浏览器控制台执行以下脚本来提取数据:\n")
        print("=" * 80)

        # 输出JavaScript脚本
        with open('/workspace/browser_console_script.js', 'r') as f:
            print(f.read())

        print("=" * 80)
        print("\n或者使用以下简化脚本快速提取当前页数据:")

        # 简化版提取脚本
        simple_script = """
// 在控制台运行此脚本提取当前页数据
const rows = document.querySelectorAll('table tbody tr');
const data = [];
rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length >= 11) {
        const videoLink = cells[6].querySelector('a');
        data.push({
            '素材ID': cells[0].innerText.trim(),
            '标题': cells[1].innerText.trim(),
            '消耗': cells[8].innerText.trim(),
            '抖音号昵称': cells[4].innerText.trim(),
            '视频链接': videoLink ? videoLink.href : '',
            '日期': cells[10].innerText.trim()
        });
    }
});
console.log(`当前页${data.length}条记录`);
console.table(data);

// 筛选消耗>2000
const filtered = data.filter(item => {
    const cost = parseFloat(item['消耗'].replace(/[¥,]/g, ''));
    return cost > 2000;
});
console.log(`消耗>2000: ${filtered.length}条`);
console.table(filtered);
        """
        print(simple_script)

if __name__ == "__main__":
    main()