#!/usr/bin/env python3
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """设置浏览器驱动"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 使用已存在的浏览器实例
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_table_data(driver):
    """提取当前页面的表格数据"""
    try:
        # 等待表格加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        data = []
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 11:
                # 提取每个单元格的数据
                row_data = {
                    '素材ID（巨量）': cells[0].text.strip(),
                    '标题': cells[1].text.strip(),
                    '星图任务ID': cells[2].text.strip(),
                    '星图任务名称': cells[3].text.strip(),
                    '抖音号昵称': cells[4].text.strip(),
                    '抖音号': cells[5].text.strip(),
                    '视频播放链接': cells[6].find_element(By.TAG_NAME, "a").get_attribute("href") if cells[6].find_elements(By.TAG_NAME, "a") else cells[6].text.strip(),
                    '下单账户名称': cells[7].text.strip(),
                    '消耗': cells[8].text.strip(),
                    '产品名称': cells[9].text.strip(),
                    '数据统计日期': cells[10].text.strip()
                }
                data.append(row_data)
        
        return data
    except Exception as e:
        print(f"提取数据时出错: {e}")
        return []

def click_next_page(driver):
    """点击下一页按钮"""
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, ".ant-pagination-next:not(.ant-pagination-disabled)")
        next_button.click()
        time.sleep(2)  # 等待页面加载
        return True
    except Exception as e:
        print(f"无法点击下一页: {e}")
        return False

def get_current_page_info(driver):
    """获取当前页码和总页数"""
    try:
        pagination = driver.find_element(By.CSS_SELECTOR, ".ant-pagination")
        page_items = pagination.find_elements(By.CSS_SELECTOR, ".ant-pagination-item")
        total_pages = len(page_items)
        
        active_page = pagination.find_element(By.CSS_SELECTOR, ".ant-pagination-item-active")
        current_page = int(active_page.text)
        
        return current_page, total_pages
    except:
        return 1, 1

def main():
    driver = setup_driver()
    all_data = []
    
    try:
        print("开始提取数据...")
        
        # 获取初始页面信息
        current_page, total_pages = get_current_page_info(driver)
        print(f"总页数: {total_pages}")
        
        # 遍历所有页面
        page_count = 0
        while True:
            page_count += 1
            print(f"正在提取第 {page_count} 页...")
            
            # 提取当前页数据
            page_data = extract_table_data(driver)
            all_data.extend(page_data)
            print(f"第 {page_count} 页提取了 {len(page_data)} 条记录")
            
            # 尝试点击下一页
            if not click_next_page(driver):
                print("已到达最后一页")
                break
        
        print(f"\n总共提取了 {len(all_data)} 条记录")
        
        # 保存原始数据
        with open('/workspace/all_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
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
        
        # 保存筛选后的数据
        with open('/workspace/filtered_data.json', 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        
        return filtered_data
        
    except Exception as e:
        print(f"执行过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        # 不关闭浏览器,因为我们使用的是已存在的实例
        pass

if __name__ == "__main__":
    result = main()
    print(f"\n任务完成,共筛选出 {len(result)} 条记录")