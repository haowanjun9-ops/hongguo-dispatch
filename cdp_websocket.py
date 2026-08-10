#!/usr/bin/env python3
"""
使用WebSocket连接到Chrome DevTools Protocol
"""
import json
import time
import csv
import asyncio
import websockets
from datetime import datetime

class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.message_id = 0

    async def send_command(self, websocket, method, params=None):
        """发送CDP命令"""
        self.message_id += 1
        command = {
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        await websocket.send(json.dumps(command))

        # 接收响应
        response = await websocket.recv()
        return json.loads(response)

    async def evaluate_script(self, websocket, script):
        """执行JavaScript脚本"""
        return await self.send_command(
            websocket,
            "Runtime.evaluate",
            {"expression": script, "returnByValue": True}
        )

async def extract_star_report():
    """提取星广报表数据"""
    import requests

    # 获取CDP端点
    try:
        response = requests.get("http://localhost:9222/json")
        pages = response.json()

        # 查找星广报表页面
        target_page = None
        for page in pages:
            if 'apex.whaleidea.cn/star/report' in page.get('url', ''):
                target_page = page
                break

        if not target_page:
            print("未找到星广报表页面")
            return []

        ws_url = target_page['webSocketDebuggerUrl']
        print(f"连接到页面: {target_page['url'][:80]}")

        all_data = []
        current_page = 1
        total_pages = 38

        async with websockets.connect(ws_url) as websocket:
            cdp = CDPClient(ws_url)

            # 提取当前页数据的JavaScript
            extract_script = """
            (function() {
                const rows = document.querySelectorAll('table tbody tr');
                const data = [];
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 11) {
                        const videoLink = cells[6].querySelector('a');
                        data.push({
                            '素材ID（巨量）': cells[0].innerText.trim(),
                            '标题': cells[1].innerText.trim(),
                            '星图任务ID': cells[2].innerText.trim(),
                            '星图任务名称': cells[3].innerText.trim(),
                            '抖音号昵称': cells[4].innerText.trim(),
                            '抖音号': cells[5].innerText.trim(),
                            '视频播放链接': videoLink ? videoLink.href : '',
                            '下单账户名称': cells[7].innerText.trim(),
                            '消耗': cells[8].innerText.trim(),
                            '产品名称': cells[9].innerText.trim(),
                            '数据统计日期': cells[10].innerText.trim()
                        });
                    }
                });
                return data;
            })();
            """

            # 点击下一页的JavaScript
            next_page_script = """
            (function() {
                const nextBtn = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)');
                if (nextBtn) {
                    nextBtn.click();
                    return true;
                }
                return false;
            })();
            """

            print(f"开始提取数据,共{total_pages}页...")

            while True:
                print(f"正在提取第 {current_page} 页...")

                # 提取数据
                result = await cdp.evaluate_script(websocket, extract_script)
                if result.get('result', {}).get('type') == 'object':
                    page_data = result['result']['value']
                    all_data.extend(page_data)
                    print(f"✓ 第 {current_page} 页: {len(page_data)} 条记录")

                if current_page >= total_pages:
                    print("已到达最后一页")
                    break

                # 点击下一页
                next_result = await cdp.evaluate_script(websocket, next_page_script)
                if not next_result.get('result', {}).get('value'):
                    print("没有下一页了")
                    break

                # 等待页面加载
                await asyncio.sleep(2.5)
                current_page += 1

        print(f"\n总共提取了 {len(all_data)} 条记录")

        # 筛选消耗>2000的记录
        filtered_data = []
        for item in all_data:
            try:
                cost_str = item['消耗'].replace('¥', '').replace(',', '').strip()
                cost = float(cost_str)
                if cost > 2000:
                    item['消耗值'] = cost
                    filtered_data.append(item)
            except:
                continue

        print(f"筛选出 {len(filtered_data)} 条消耗>2000的记录")

        return filtered_data, all_data

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return [], []

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    if not data:
        print("没有数据需要保存")
        return None

    fieldnames = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', '抖音号',
                  '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期']

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

    print(f"数据已保存到: {filename}")
    return filename

async def main():
    filtered_data, all_data = await extract_star_report()

    if not filtered_data:
        print("无超2000消耗数据")
        return

    # 保存数据
    current_time = datetime.now().strftime('%H%M%S')
    csv_filename = f'/workspace/star_report_cost_over_2000_2026-08-10_{current_time}.csv'
    save_to_csv(filtered_data, csv_filename)

    # 保存JSON数据
    with open('/workspace/all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    with open('/workspace/filtered_data.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

    print(f"\n任务完成!")
    print(f"- 总记录数: {len(all_data)}")
    print(f"- 筛选记录数: {len(filtered_data)}")
    print(f"- CSV文件: {csv_filename}")

    return filtered_data, csv_filename

if __name__ == "__main__":
    result = asyncio.run(main())