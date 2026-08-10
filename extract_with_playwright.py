#!/usr/bin/env python3
import asyncio
import json
import csv
import os
from datetime import datetime
from playwright.async_api import async_playwright

async def extract_all_data():
    """提取所有页面的数据"""
    async with async_playwright() as p:
        # 连接到已存在的浏览器
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")

        # 获取所有上下文和页面
        contexts = browser.contexts
        if not contexts:
            print("没有找到浏览器上下文")
            return []

        page = None
        # 查找包含目标URL的页面
        for context in contexts:
            pages = context.pages
            for p in pages:
                if 'apex.whaleidea.cn/star/report' in p.url:
                    page = p
                    break
            if page:
                break

        if not page:
            print("未找到星广报表页面")
            return []

        print(f"找到页面: {page.url}")

        all_data = []
        page_num = 1
        total_pages = 38

        # 提取当前页数据的函数
        async def extract_current_page():
            rows = await page.query_selector_all('table tbody tr')
            page_data = []

            for row in rows:
                cells = await row.query_selector_all('td')
                if len(cells) >= 11:
                    # 提取文本内容
                    texts = []
                    for cell in cells:
                        text = await cell.inner_text()
                        texts.append(text.strip())

                    # 提取视频链接
                    video_link_cell = cells[6]
                    video_link = await video_link_cell.query_selector('a')
                    video_url = ""
                    if video_link:
                        video_url = await video_link.get_attribute('href')

                    row_data = {
                        '素材ID（巨量）': texts[0],
                        '标题': texts[1],
                        '星图任务ID': texts[2],
                        '星图任务名称': texts[3],
                        '抖音号昵称': texts[4],
                        '抖音号': texts[5],
                        '视频播放链接': video_url if video_url else texts[6],
                        '下单账户名称': texts[7],
                        '消耗': texts[8],
                        '产品名称': texts[9],
                        '数据统计日期': texts[10]
                    }
                    page_data.append(row_data)

            return page_data

        # 点击下一页的函数
        async def go_to_next_page():
            next_btn = await page.query_selector('.ant-pagination-next:not(.ant-pagination-disabled)')
            if next_btn:
                await next_btn.click()
                await page.wait_for_timeout(2000)  # 等待2秒
                return True
            return False

        # 主循环 - 遍历所有页面
        print(f"开始提取数据,共{total_pages}页...")

        while True:
            print(f"正在提取第 {page_num} 页...")

            # 提取当前页数据
            page_data = await extract_current_page()
            all_data.extend(page_data)
            print(f"第 {page_num} 页提取了 {len(page_data)} 条记录")

            if page_num >= total_pages:
                print("已到达最后一页")
                break

            # 点击下一页
            has_next = await go_to_next_page()
            if not has_next:
                print("没有下一页了")
                break

            page_num += 1

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
            except Exception as e:
                print(f"解析消耗字段失败: {item['消耗']}, 错误: {e}")
                continue

        print(f"筛选出 {len(filtered_data)} 条消耗>2000的记录")

        return filtered_data, all_data

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
    filtered_data, all_data = await extract_all_data()

    if not filtered_data:
        print("无超2000消耗数据")
        return

    # 保存数据
    current_time = datetime.now().strftime('%H%M%S')
    csv_filename = f'/workspace/star_report_cost_over_2000_2026-08-10_{current_time}.csv'
    save_to_csv(filtered_data, csv_filename)

    # 保存完整数据到JSON(用于调试)
    with open('/workspace/all_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    with open('/workspace/filtered_data.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

    print(f"\n共筛选出 {len(filtered_data)} 条消耗>2000的记录")
    print(f"CSV文件: {csv_filename}")

    return filtered_data, csv_filename

if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        filtered_data, csv_filename = result
        print(f"\n任务完成!")
        print(f"- 筛选记录数: {len(filtered_data)}")
        print(f"- CSV文件: {csv_filename}")