#!/usr/bin/env python3
"""
星广报表数据自动提取脚本
通过MCP浏览器接口循环提取52页数据
"""

import json
import subprocess
import time
import sys
from pathlib import Path

# 配置
TOTAL_PAGES = 52
OUTPUT_JSON = "/workspace/all_data.json"
OUTPUT_CSV = "/workspace/high_cost_records.csv"

# JavaScript提取脚本
EXTRACT_SCRIPT = """
const tbody = document.querySelector('.arco-table-body');
if (!tbody) return JSON.stringify({error: 'No tbody found'});

const trs = tbody.querySelectorAll('tr.arco-table-tr');
const rows = [];

for (let i = 1; i < trs.length; i++) {
    const tr = trs[i];
    const cells = tr.querySelectorAll('td.arco-table-td');
    
    if (cells.length >= 11) {
        const row = {
            materialId: cells[0].textContent.trim(),
            title: cells[1].textContent.trim(),
            taskId: cells[2].textContent.trim(),
            taskName: cells[3].textContent.trim(),
            douyinNickname: cells[4].textContent.trim(),
            douyinId: cells[5].textContent.trim(),
            videoUrl: cells[6].textContent.trim(),
            accountName: cells[7].textContent.trim(),
            cost: parseFloat(cells[8].textContent.trim()) || 0,
            productName: cells[9].textContent.trim(),
            date: cells[10].textContent.trim()
        };
        rows.push(row);
    }
}

window.ALL_DATA.push(...rows);
return JSON.stringify({
    success: true,
    page: window.CURRENT_PAGE,
    rowCount: rows.length,
    totalSoFar: window.ALL_DATA.length
});
"""

# 点击下一页脚本
NEXT_PAGE_SCRIPT = """
const nextBtn = document.querySelector('.arco-pagination-item-next');
if (nextBtn && !nextBtn.classList.contains('arco-pagination-item-disabled')) {
    nextBtn.click();
    window.CURRENT_PAGE++;
    return 'clicked';
}
return 'disabled';
"""

# 获取所有数据脚本
GET_ALL_DATA_SCRIPT = """
return JSON.stringify({
    totalRecords: window.ALL_DATA.length,
    data: window.ALL_DATA
});
"""


def run_mcp_tool(tool_name, args=None):
    """
    调用MCP浏览器工具
    注意：这里使用subprocess调用MCP CLI客户端
    """
    if args is None:
        args = {}
    
    # 构造MCP调用命令
    # 这里假设可以通过Python的MCP接口调用
    # 实际实现取决于MCP服务器的配置方式
    
    cmd_args = {
        'server_name': 'integrated_browser',
        'tool_name': tool_name,
        'args': args
    }
    
    # 通过subprocess调用（这里需要实际的MCP客户端命令）
    # 由于当前环境可能没有MCP CLI，我们使用另一种方法
    return cmd_args


def extract_page_data():
    """提取当前页数据"""
    print("正在提取当前页数据...")
    # 这里需要实际的浏览器执行逻辑
    # 由于没有直接的MCP工具，我们返回模拟数据或报错
    return None


def click_next_page():
    """点击下一页按钮"""
    print("点击下一页...")
    return None


def wait_for_load(seconds=2):
    """等待页面加载"""
    print(f"等待 {seconds} 秒...")
    time.sleep(seconds)


def save_to_json(data, filepath):
    """保存数据到JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到: {filepath}")


def filter_and_save_csv(data, min_cost=2000):
    """筛选消耗大于指定值的记录并保存为CSV"""
    import csv
    
    filtered = [row for row in data if row.get('cost', 0) > min_cost]
    
    if not filtered:
        print(f"没有找到消耗大于 {min_cost} 的记录")
        return
    
    output_path = OUTPUT_CSV
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        if filtered:
            fieldnames = filtered[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered)
    
    print(f"已筛选出 {len(filtered)} 条消耗>{min_cost}的记录，保存到: {output_path}")


def main():
    """主函数：循环提取所有页面数据"""
    print("=" * 60)
    print("星广报表数据自动提取脚本")
    print("=" * 60)
    print(f"总页数: {TOTAL_PAGES}")
    print(f"输出JSON: {OUTPUT_JSON}")
    print(f"输出CSV: {OUTPUT_CSV}")
    print("=" * 60)
    
    # 注意：这个脚本需要通过MCP工具来实际控制浏览器
    # 由于当前环境限制，这里提供框架代码
    # 实际执行需要配合MCP浏览器服务器
    
    print("\n警告：此脚本需要MCP浏览器接口支持")
    print("请使用提供的JavaScript脚本手动执行，或配置MCP环境\n")
    
    # 提供手动执行的JavaScript代码
    print("请在浏览器控制台执行以下代码来完成提取：")
    print("\n1. 初始化全局变量（已执行）")
    print("window.CURRENT_PAGE = 1; window.ALL_DATA = [];\n")
    
    print("2. 循环提取脚本（复制到控制台执行）：")
    print("-" * 60)
    
    # 生成完整的浏览器控制台脚本
    console_script = f"""
// 循环提取所有页面数据
const totalPages = {TOTAL_PAGES};

async function extractAllPages() {{
    for (let i = 0; i < totalPages; i++) {{
        // 提取当前页数据
        {EXTRACT_SCRIPT.strip()}
        
        console.log(`已提取第 ${{window.CURRENT_PAGE}} 页，累计 ${{window.ALL_DATA.length}} 条记录`);
        
        // 点击下一页
        {NEXT_PAGE_SCRIPT.strip()}
        
        // 等待2秒
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 检查是否还有下一页
        const nextBtn = document.querySelector('.arco-pagination-item-next');
        if (!nextBtn || nextBtn.classList.contains('arco-pagination-item-disabled')) {{
            console.log('已到达最后一页');
            break;
        }}
    }}
    
    // 保存数据
    const dataStr = JSON.stringify(window.ALL_DATA, null, 2);
    console.log('\\n========== 数据提取完成 ==========');
    console.log(`总共提取 ${{window.ALL_DATA.length}} 条记录`);
    console.log('\\n数据已保存在 window.ALL_DATA 中');
    console.log('使用以下命令复制数据:');
    console.log('copy(window.ALL_DATA)');
    
    // 筛选消耗>2000的记录
    const highCost = window.ALL_DATA.filter(row => row.cost > 2000);
    console.log(`\\n消耗>2000的记录: ${{highCost.length}} 条`);
    
    return {{
        total: window.ALL_DATA.length,
        highCost: highCost.length,
        data: window.ALL_DATA
    }};
}}

// 执行提取
extractAllPages().then(result => {{
    console.log('\\n提取完成！', result);
}});
"""
    print(console_script)
    print("-" * 60)
    
    print("\n3. 提取完成后，使用以下命令复制数据：")
    print("copy(JSON.stringify(window.ALL_DATA, null, 2))")
    print("\n4. 将数据粘贴到此文件中使用Python处理")
    
    print("\n" + "=" * 60)
    print("提示：由于当前环境缺少浏览器自动化接口，")
    print("请使用上述JavaScript脚本在浏览器控制台执行。")
    print("=" * 60)


if __name__ == "__main__":
    main()