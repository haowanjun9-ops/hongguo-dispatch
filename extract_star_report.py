#!/usr/bin/env python3
"""
鲸准3.0星广报表数据提取脚本
提取所有消耗超过2000的记录
"""
import time
import csv
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """设置浏览器驱动"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login(driver, username, password):
    """登录系统"""
    print("正在登录...")
    driver.get("https://apex.whaleidea.cn/login")
    time.sleep(2)
    
    # 输入用户名
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请输入用户名'], input[type='text']"))
    )
    username_input.clear()
    username_input.send_keys(username)
    
    # 输入密码
    password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    password_input.clear()
    password_input.send_keys(password)
    
    # 点击登录按钮
    login_button = driver.find_element(By.XPATH, "//button[contains(text(), '登录')]")
    login_button.click()
    
    # 等待登录成功
    time.sleep(3)
    print("登录成功")

def navigate_to_report(driver):
    """导航到报表页面"""
    print("正在导航到星广报表页面...")
    driver.get("https://apex.whaleidea.cn/star/report")
    time.sleep(3)
    print("已到达星广报表页面")

def click_query_button(driver):
    """点击查询按钮"""
    print("点击查询按钮...")
    try:
        query_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '查询')]"))
        )
        query_button.click()
        time.sleep(3)
        print("查询完成")
    except TimeoutException:
        print("查询按钮未找到或无法点击")

def get_total_pages(driver):
    """获取总页数"""
    try:
        # 查找分页信息
        pagination = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(text(), '36') or contains(@class, 'number')]"))
        )
        # 从页面上找最大页码
        page_numbers = driver.find_elements(By.CSS_SELECTOR, "li.number")
        if page_numbers:
            last_page = page_numbers[-1].text
            return int(last_page)
        return 36  # 默认36页
    except:
        return 36

def extract_table_data(driver):
    """提取表格数据"""
    data = []
    
    try:
        # 等待表格加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        
        # 获取所有数据行（排除汇总行）
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 11:
                # 提取各列数据
                material_id = cells[0].text.strip()
                title = cells[1].text.strip()
                star_task_id = cells[2].text.strip()
                star_task_name = cells[3].text.strip()
                douyin_nickname = cells[4].text.strip()
                douyin_id = cells[5].text.strip()
                video_link = cells[6].text.strip()
                order_account = cells[7].text.strip()
                cost = cells[8].text.strip()
                product_name = cells[9].text.strip()
                stat_date = cells[10].text.strip()
                
                # 跳过汇总行
                if material_id == "汇总":
                    continue
                
                # 提取消耗数值
                try:
                    cost_value = float(cost)
                except ValueError:
                    cost_value = 0.0
                
                record = {
                    '素材ID（巨量）': material_id,
                    '标题': title,
                    '星图任务ID': star_task_id,
                    '星图任务名称': star_task_name,
                    '抖音号昵称': douyin_nickname,
                    '抖音号': douyin_id,
                    '视频播放链接': video_link,
                    '下单账户名称': order_account,
                    '消耗': cost_value,
                    '产品名称': product_name,
                    '数据统计日期': stat_date
                }
                
                data.append(record)
        
    except Exception as e:
        print(f"提取数据时出错: {e}")
    
    return data

def go_to_next_page(driver, current_page):
    """翻到下一页"""
    try:
        # 找到下一页按钮或页码按钮
        next_buttons = driver.find_elements(By.CSS_SELECTOR, "li.number, li.btn-next")
        
        for btn in next_buttons:
            try:
                text = btn.text.strip()
                # 如果是数字且是下一页
                if text.isdigit() and int(text) == current_page + 1:
                    btn.click()
                    time.sleep(2)
                    return True
                # 如果是下一页按钮
                elif '下一页' in btn.get_attribute('class') or 'btn-next' in btn.get_attribute('class'):
                    if current_page < 36:  # 最后一页
                        btn.click()
                        time.sleep(2)
                        return True
            except:
                continue
        
        return False
    except:
        return False

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    if not data:
        return False
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['素材ID（巨量）', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', 
                      '抖音号', '视频播放链接', '下单账户名称', '消耗', '产品名称', '数据统计日期']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    return True

def filter_high_cost(data, threshold=2000):
    """筛选消耗超过阈值的记录"""
    return [record for record in data if record['消耗'] > threshold]

def main():
    """主函数"""
    username = "haowanjun@whalewh.cn"
    password = "?!]d<yI0"
    
    print("="*60)
    print("鲸准3.0星广报表数据提取开始")
    print("="*60)
    
    # 初始化浏览器
    driver = setup_driver()
    
    try:
        # 登录
        login(driver, username, password)
        
        # 导航到报表页面
        navigate_to_report(driver)
        
        # 点击查询按钮
        click_query_button(driver)
        
        # 获取总页数
        total_pages = get_total_pages(driver)
        print(f"总页数: {total_pages}")
        
        # 提取所有数据
        all_data = []
        
        for page in range(1, total_pages + 1):
            print(f"正在提取第 {page}/{total_pages} 页数据...")
            
            # 提取当前页数据
            page_data = extract_table_data(driver)
            all_data.extend(page_data)
            
            print(f"第 {page} 页提取了 {len(page_data)} 条记录")
            
            # 如果不是最后一页，翻到下一页
            if page < total_pages:
                if not go_to_next_page(driver, page):
                    print(f"无法翻到第 {page + 1} 页，停止提取")
                    break
        
        print(f"\n总共提取了 {len(all_data)} 条记录")
        
        # 筛选消耗超过2000的记录
        high_cost_data = filter_high_cost(all_data, 2000)
        print(f"消耗超过2000的记录: {len(high_cost_data)} 条")
        
        if not high_cost_data:
            print("\n无超2000消耗数据")
            driver.quit()
            return None, 0
        
        # 保存到CSV
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        csv_filename = f"/workspace/star_report_cost_over_2000_{timestamp}.csv"
        
        if save_to_csv(high_cost_data, csv_filename):
            print(f"\n数据已保存到: {csv_filename}")
        
        driver.quit()
        return csv_filename, len(high_cost_data)
        
    except Exception as e:
        print(f"执行过程中出错: {e}")
        driver.quit()
        return None, 0

if __name__ == "__main__":
    csv_file, count = main()
    if csv_file:
        print(f"\n任务完成！共筛选出 {count} 条消耗超过2000的记录")
    else:
        print("\n无超2000消耗数据")