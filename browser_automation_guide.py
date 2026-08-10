#!/usr/bin/env python3
"""
星广报表数据提取脚本
从 https://apex.whaleidea.cn/star/report 提取所有消耗>2000的记录
"""

import json
import time

def main():
    """
    主函数 - 用于在浏览器控制台中执行
    
    使用方法：
    1. 打开浏览器开发者工具 (F12)
    2. 切换到 Console 标签
    3. 复制并粘贴此脚本的内容
    4. 按回车执行
    5. 脚本将自动提取所有页面的数据并筛选消耗>2000的记录
    """
    
    # 用于存储所有数据的数组
    all_data = []
    
    # 提取当前页面数据的函数
    def extract_current_page():
        """提取当前页面的表格数据"""
        # 查找表格 - 尝试多种选择器
        table = document.querySelector('table') || \
                document.querySelector('.ant-table table') || \
                document.querySelector('[role="table"]')
        
        if not table:
            console.error('未找到表格元素')
            return []
        
        # 获取所有行
        all_rows = Array.from(table.querySelectorAll('tr'))
        
        # 跳过前两行（汇总行和表头）
        data_rows = all_rows.slice(2)
        
        extracted = []
        
        for row in data_rows:
            cells = Array.from(row.querySelectorAll('td, th'))
            
            if cells.length < 11:
                continue
            
            # 提取11列数据
            # 0: 素材ID（巨量）
            # 1: 标题
            # 2: 星图任务ID
            # 3: 星图任务名称
            # 4: 抖音号昵称
            # 5: 抖音号
            # 6: 视频播放链接
            # 7: 下单账户名称
            # 8: 消耗
            # 9: 产品名称
            # 10: 数据统计日期
            
            cost_text = cells[8]?.textContent?.trim() || '0'
            cost_value = parseFloat(cost_text.replace(/[¥,]/g, ''))
            
            row_data = {
                '素材ID（巨量）': cells[0]?.textContent?.trim() || '',
                '标题': cells[1]?.textContent?.trim() || '',
                '星图任务ID': cells[2]?.textContent?.trim() || '',
                '星图任务名称': cells[3]?.textContent?.trim() || '',
                '抖音号昵称': cells[4]?.textContent?.trim() || '',
                '抖音号': cells[5]?.textContent?.trim() || '',
                '视频播放链接': cells[6]?.querySelector('a')?.href || cells[6]?.textContent?.trim() || '',
                '下单账户名称': cells[7]?.textContent?.trim() || '',
                '消耗': cost_value,
                '产品名称': cells[9]?.textContent?.trim() || '',
                '数据统计日期': cells[10]?.textContent?.trim() || ''
            }
            
            extracted.append(row_data)
        
        return extracted
    
    # 点击下一页的函数
    async def click_next_page():
        """点击下一页按钮"""
        # 尝试多种方式找到下一页按钮
        next_button = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)') || \
                      document.querySelector('[aria-label="下一页"]') || \
                      document.querySelector('.pagination .next:not(.disabled)')
        
        if next_button && !next_button.classList.contains('ant-pagination-disabled')) {
            next_button.click()
            return True
        }
        
        return False
    
    # 主提取流程
    async def extract_all_pages():
        """提取所有页面的数据"""
        console.log('开始提取数据...')
        
        total_pages = 39
        current_page = 1
        
        while current_page <= total_pages:
            console.log(`正在提取第 ${current_page}/${total_pages} 页数据...`)
            
            # 提取当前页面数据
            page_data = extract_current_page()
            all_data.push(...page_data)
            console.log(`第 ${current_page} 页提取完成，获取 ${page_data.length} 条数据`)
            
            if current_page < total_pages:
                # 点击下一页
                has_next = click_next_page()
                
                if not has_next:
                    console.log('没有下一页了，停止提取')
                    break
                
                # 等待数据加载
                await new Promise(resolve => setTimeout(resolve, 3000))
            
            current_page += 1
        
        console.log(`数据提取完成！共获取 ${all_data.length} 条数据`)
        
        # 筛选消耗>2000的记录
        filtered_data = all_data.filter(row => row['消耗'] > 2000)
        console.log(`筛选完成！消耗>2000的记录共 ${filtered_data.length} 条`)
        
        # 输出结果
        console.log('筛选结果：')
        console.log(filtered_data)
        
        return filtered_data
    
    # 执行提取
    return await extract_all_pages()


if __name__ == '__main__':
    # 这个Python脚本不会直接运行，而是作为参考
    # 实际执行需要在浏览器控制台中运行JavaScript代码
    print("""
    ===================================
    浏览器自动化数据提取指南
    ===================================
    
    由于需要在已登录的浏览器中执行，请按照以下步骤操作：
    
    方法一：在浏览器控制台中手动执行
    1. 打开 https://apex.whaleidea.cn/star/report
    2. 按 F12 打开开发者工具
    3. 切换到 Console 标签
    4. 复制 browser_console_script.js 的内容并粘贴执行
    
    方法二：使用浏览器自动化工具（如需要）
    请使用 Playwright 或 Puppeteer 等工具来自动化浏览器
    
    ===================================
    """)