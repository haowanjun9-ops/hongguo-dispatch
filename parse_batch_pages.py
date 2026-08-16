#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析浏览器Exec返回的包含多个===PAGE_X===标记的文本
提取每页JSON并追加到all_pages_data.json
"""
import json
import re
import sys
import os

WORKSPACE = "/workspace"
SNAPSHOT_FILE = os.path.join(WORKSPACE, "all_pages_data.json")

def extract_and_append(batch_text):
    """从文本中提取 ===PAGE_X===Result: "JSON" 格式数据，解析并追加"""
    pattern = re.compile(r'===PAGE_(\d+)===Result:\s*(".*?")\s*(?=\n===PAGE|\Z)', re.DOTALL)
    pattern2 = re.compile(r'===PAGE_(\d+)===(.+?)(?=\n===PAGE|\Z)', re.DOTALL)
    
    pages_added = []
    
    existing = []
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except:
            existing = []
    
    for m in pattern2.finditer(batch_text):
        page_num = m.group(1)
        content = m.group(2).strip()
        # content 可能是 Result: "JSON" 或 Result: undefined
        if content.startswith('Result: undefined'):
            print(f"PAGE {page_num}: undefined, 跳过")
            continue
        # 去掉 Result: 前缀
        json_str_raw = content[len('Result:'):].strip()
        # 此时 json_str_raw 应该是一个被引号包裹的字符串 "{\"headers\":...}"
        try:
            # 第一层解析：得到JSON字符串（因为JSON.stringify的值是一个带引号的string）
            inner = json.loads(json_str_raw)
            # 第二层解析：得到真正的对象
            page_obj = json.loads(inner)
            page_obj['currentPage'] = str(page_obj.get('currentPage', page_num))
            pages_added.append(page_obj)
            print(f"PAGE {page_obj.get('currentPage')}: 解析成功，{len(page_obj.get('data',[]))} 行")
        except Exception as e:
            print(f"PAGE {page_num}: 解析失败 {e}")
            print(f"  raw前200字符: {repr(json_str_raw[:200])}")
            continue
    
    # 合并去重
    merged = {p.get('currentPage'): p for p in existing}
    for p in pages_added:
        merged[p.get('currentPage')] = p
    final = list(merged.values())
    
    def sort_key(p):
        try:
            return int(p.get('currentPage', '0'))
        except:
            return 0
    final.sort(key=sort_key)
    
    with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
    
    print(f"\\n总页数：{len(final)}")
    return pages_added, final

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 从stdin读取
        text = sys.stdin.read()
    else:
        # 从文件读取
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()
    extract_and_append(text)
