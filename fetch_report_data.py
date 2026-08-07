#!/usr/bin/env python3
"""
鲸准3.0星广报表数据提取 - 使用Selenium自动化
"""
import json
import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """设置Chrome浏览器"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def login(driver, username, password):
    """登录系统"""
    print("正在登录...")
    driver.get("https://apex.whaleidea.cn/login")
    time.sleep(2)
    
    # 输入用户名和密码
    driver.find_element(By.CSS_SELECTOR, "input[type='text']").send_keys(username)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(password)
    
    # 点击登录
    driver.find_element(By.XPATH, "//button[contains(text(), '登录')]").click()
    time.sleep(3)
    print("登录成功")

def extract_page_data(driver):
    """提取当前页的表格数据"""
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    data = []
    
    for row in rows:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 11:
                material_id = cells[0].text.strip()
                if material_id == "汇总":
                    continue
                
                cost_text = cells[8].text.strip()
                try:
                    cost = float(cost_text)
                except:
                    cost = 0.0
                
                data.append({
                    '素材ID（巨量）': material_id,
                    '标题': cells[1].text.strip(),
                    '星图任务ID': cells[2].text.strip(),
                    '星图任务名称': cells[3].text.strip(),
                    '抖音号昵称': cells[4].text.strip(),
                    '抖音号': cells[5].text.strip(),
                    '视频播放链接': cells[6].text.strip(),
                    '下单账户名称': cells[7].text.strip(),
                    '消耗': cost,
                    '产品名称': cells[9].text.strip(),
                    '数据统计日期': cells[10].text.strip()
                })
        except Exception as e:
            continue
    
    return data

def get_total_pages(driver):
    """获取总页数"""
    try:
        # 查找页码按钮
        page_numbers = driver.find_elements(By.CSS_SELECTOR, "li.number")
        if page_numbers:
            last_page = int(page_numbers[-1].text)
            return last_page
    except:
        pass
    return 36

def click_page(driver, page_num):
    """点击指定页码"""
    try:
        page_buttons = driver.find_elements(By.CSS_SELECTOR, "li.number")
        for btn in page_buttons:
            if btn.text.strip() == str(page_num):
                btn.click()
                return True
    except:
        pass
    return False

def main():
    """主函数"""
    username = "haowanjun@whalewh.cn"
    password = "?!]d<yI0"
    
    print("="*60)
    print("鲸准3.0星广报表数据提取")
    print("="*60)
    
    driver = setup_driver()
    
    try:
        # 登录
        login(driver, username, password)
        
        # 导航到报表页面
        print("正在导航到星广报表页面...")
        driver.get("https://apex.whaleidea.cn/star/report")
        time.sleep(3)
        
        # 点击查询按钮
        print("点击查询按钮...")
        driver.find_element(By.XPATH, "//button[contains(text(), '查询')]").click()
        time.sleep(3)
        
        # 获取总页数
        total_pages = get_total_pages(driver)
        print(f"总页数: {total_pages}")
        
        # 提取所有数据
        all_data = []
        
        for page in range(1, total_pages + 1):
            print(f"正在提取第 {page}/{total_pages} 页...")
            
            if page > 1:
                if not click_page(driver, page):
                    print(f"无法跳转到第 {page} 页，停止提取")
                    break
                time.sleep(2)
            
            page_data = extract_page_data(driver)
            all_data.extend(page_data)
            print(f"第 {page} 页提取了 {len(page_data)} 条记录，累计 {len(all_data)} 条")
        
        print(f"\n总共提取了 {len(all_data)} 条记录")
        
        # 筛选消耗超过2000的记录
        high_cost_data = [item for item in all_data if item['消耗'] > 2000]
        print(f"消耗超过2000的记录: {len(high_cost_data)} 条")
        
        driver.quit()
        
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
        driver.quit()
        return None, 0

if __name__ == "__main__":
    csv_file, count = main()
    if csv_file:
        print(f"\n任务完成！共筛选出 {count} 条消耗超过2000的记录")
    else:
        print("\n无超2000消耗数据")