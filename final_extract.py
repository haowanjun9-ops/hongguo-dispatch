#!/usr/bin/env python3
"""
通过CDP WebSocket自动提取星广报表数据
"""
import json
import csv
import asyncio
import websockets
from datetime import datetime

class CDPClient:
    def __init__(self):
        self.message_id = 0

    async def send_command(self, websocket, method, params=None):
        """发送CDP命令并等待响应"""
        self.message_id += 1
        command = {
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        await websocket.send(json.dumps(command))

        # 等待响应
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            if data.get('id') == self.message_id:
                return data

    async def evaluate_script(self, websocket, script):
        """执行JavaScript脚本并返回结果"""
        result = await self.send_command(
            websocket,
            "Runtime.evaluate",
            {
                "expression": script,
                "returnByValue": True,
                "timeout": 60000,
                "awaitPromise": True
            }
        )
        return result

async def extract_all_pages():
    """提取所有页面的数据"""
    import requests

    try:
        # 连接到CDP
        response = requests.get("http://localhost:9222/json")
        pages = response.json()

        if not pages:
            print("错误: 没有找到浏览器页面")
            return [], []

        # 使用第一个页面
        ws_url = pages[0]['webSocketDebuggerUrl']
        print(f"连接到浏览器: {pages[0].get('url', 'unknown')}")

        all_data = []
        current_page = 1
        total_pages = 38

        async with websockets.connect(ws_url, max_size=10*1024*1024) as websocket:
            cdp = CDPClient()

            print(f"开始提取数据,预计{total_pages}页...\n")

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
                if (nextBtn && !nextBtn.classList.contains('ant-pagination-disabled')) {
                    nextBtn.click();
                    return true;
                }
                return false;
            })();
            """

            while True:
                print(f"📖 正在提取第 {current_page} 页...", flush=True)

                # 提取当前页数据
                result = await cdp.evaluate_script(websocket, extract_script)

                page_data = []
                if 'result' in result and 'result' in result['result']:
                    value = result['result']['result'].get('value')
                    if isinstance(value, list):
                        page_data = value

                if page_data:
                    all_data.extend(page_data)
                    print(f"✅ 第 {current_page} 页: {len(page_data)} 条记录 (累计: {len(all_data)} 条)", flush=True)
                else:
                    print(f"⚠️ 第 {current_page} 页没有数据", flush=True)

                # 检查是否到达最后一页
                if current_page >= total_pages:
                    print("\n✅ 已处理完所有页面", flush=True)
                    break

                # 点击下一页
                next_result = await cdp.evaluate_script(websocket, next_page_script)

                if next_result.get('result', {}).get('result', {}).get('value') == True:
                    # 等待页面加载
                    await asyncio.sleep(2.5)
                    current_page += 1
                else:
                    print("\nℹ️ 已到达最后一页", flush=True)
                    break

        print(f"\n📊 提取完成! 总共提取了 {len(all_data)} 条记录", flush=True)

        # 筛选消耗>2000的记录
        print("\n🔍 开始筛选消耗>2000的记录...", flush=True)

        filtered_data = []
        for item in all_data:
            try:
                # 清理消耗字符串
                cost_str = item['消耗'].replace('¥', '').replace('￥', '').replace(',', '').replace('，', '').replace('元', '').strip()
                cost = float(cost_str)

                if cost > 2000:
                    item['消耗值'] = cost
                    filtered_data.append(item)
            except:
                # 尝试提取数字
                try:
                    import re
                    numbers = re.findall(r'\d+\.?\d*', item['消耗'])
                    if numbers:
                        cost = float(numbers[0])
                        if cost > 2000:
                            item['消耗值'] = cost
                            filtered_data.append(item)
                except:
                    pass

        print(f"✅ 筛选完成: {len(filtered_data)} 条消耗>2000的记录", flush=True)

        return filtered_data, all_data

    except Exception as e:
        print(f"❌ 错误: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return [], []

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    if not data:
        return None

    fieldnames = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', '抖音号',
                  '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期']

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ CSV文件已保存: {filename}", flush=True)
    return filename

async def main():
    print("=== 星广报表数据提取任务开始 ===\n", flush=True)

    filtered_data, all_data = await extract_all_pages()

    if not filtered_data:
        print("\n⚠️ 无超2000消耗数据", flush=True)
        return None, 0

    # 保存数据
    current_time = datetime.now().strftime('%H%M%S')
    csv_filename = f'/workspace/star_report_cost_over_2000_2026-08-10_{current_time}.csv'
    save_to_csv(filtered_data, csv_filename)

    # 保存JSON数据
    with open('/workspace/all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    with open('/workspace/filtered_data.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

    print(f"\n✨ 任务完成!", flush=True)
    print(f"- 总记录数: {len(all_data)}", flush=True)
    print(f"- 筛选记录数: {len(filtered_data)}", flush=True)
    print(f"- CSV文件: {csv_filename}", flush=True)

    return csv_filename, len(filtered_data)

if __name__ == "__main__":
    result = asyncio.run(main())
    if result[0]:
        print(f"\n✓ 成功完成!", flush=True)
        print(f"  CSV: {result[0]}", flush=True)
        print(f"  记录数: {result[1]}", flush=True)