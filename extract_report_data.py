#!/usr/bin/env python3
"""
完整的鲸准3.0星广报表数据提取脚本
使用playwright自动化浏览器
"""
import asyncio
import csv
from datetime import datetime
from playwright.async_api import async_playwright

async def extract_all_pages():
    """提取所有页面数据"""
    print("="*60)
    print("鲸准3.0星广报表数据提取开始")
    print("="*60)
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 登录
            print("正在登录...")
            await page.goto("https://apex.whaleidea.cn/login", timeout=60000)
            await page.wait_for_load_state("networkidle")
            await page.fill("input[type='text']", "haowanjun@whalewh.cn")
            await page.fill("input[type='password']", "?!]d<yI0")
            await page.click("button:has-text('登录')")
            await page.wait_for_load_state("networkidle")
            print("登录成功")
            
            # 导航到报表页面
            print("正在导航到星广报表页面...")
            await page.goto("https://apex.whaleidea.cn/star/report", timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            # 点击查询按钮
            print("点击查询按钮...")
            await page.click("button:has-text('查询')")
            await page.wait_for_load_state("networkidle")
            
            # 获取总页数
            print("获取总页数...")
            page_numbers = await page.locator("li.number").all_text_contents()
            if page_numbers:
                total_pages = int(page_numbers[-1])
            else:
                total_pages = 36
            
            print(f"总页数: {total_pages}")
            
            # 提取所有数据
            all_data = []
            
            for current_page in range(1, total_pages + 1):
                print(f"正在提取第 {current_page}/{total_pages} 页...")
                
                # 提取当前页数据
                rows = await page.locator("table tbody tr").all()
                
                for row in rows[1:]:  # 跳过第一行（汇总行）
                    try:
                        cells = await row.locator("td").all()
                        if len(cells) >= 11:
                            material_id = await cells[0].text_content()
                            if material_id.strip() == "汇总":
                                continue
                            
                            cost_text = await cells[8].text_content()
                            try:
                                cost = float(cost_text.strip())
                            except:
                                cost = 0.0
                            
                            all_data.append({
                                '素材ID（巨量）': material_id.strip(),
                                '标题': (await cells[1].text_content()).strip(),
                                '星图任务ID': (await cells[2].text_content()).strip(),
                                '星图任务名称': (await cells[3].text_content()).strip(),
                                '抖音号昵称': (await cells[4].text_content()).strip(),
                                '抖音号': (await cells[5].text_content()).strip(),
                                '视频播放链接': (await cells[6].text_content()).strip(),
                                '下单账户名称': (await cells[7].text_content()).strip(),
                                '消耗': cost,
                                '产品名称': (await cells[9].text_content()).strip(),
                                '数据统计日期': (await cells[10].text_content()).strip()
                            })
                    except Exception as e:
                        print(f"提取行数据出错: {e}")
                        continue
                
                print(f"第 {current_page} 页提取完成，累计 {len(all_data)} 条")
                
                # 翻到下一页
                if current_page < total_pages:
                    try:
                        # 点击下一页按钮或页码
                        next_page_btn = page.locator(f"li.number:has-text('{current_page + 1}')")
                        if await next_page_btn.count() > 0:
                            await next_page_btn.click()
                            await page.wait_for_load_state("networkidle")
                        else:
                            # 尝试点击下一页箭头
                            await page.click("li.btn-next")
                            await page.wait_for_load_state("networkidle")
                    except Exception as e:
                        print(f"翻页失败: {e}")
                        break
            
            print(f"\n总共提取了 {len(all_data)} 条记录")
            
            # 筛选消耗超过2000的记录
            high_cost_data = [item for item in all_data if item['消耗'] > 2000]
            print(f"消耗超过2000的记录: {len(high_cost_data)} 条")
            
            await browser.close()
            
            if not high_cost_data:
                print("\n无超2000消耗数据")
                return None, 0
            
            # 保存到CSV
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            csv_file = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', 
                              '抖音号', '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(high_cost_data)
            
            print(f"数据已保存到: {csv_file}")
            
            return csv_file, len(high_cost_data)
            
        except Exception as e:
            print(f"执行出错: {e}")
            await browser.close()
            return None, 0

if __name__ == "__main__":
    csv_file, count = asyncio.run(extract_all_pages())
    if csv_file:
        print(f"\n任务完成！共筛选出 {count} 条消耗超过2000的记录")
    else:
        print("\n无超2000消耗数据")