#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接把指定的页数据对象追加/更新到 all_pages_data.json
不经过 ===PAGE_X=== 文本格式，直接操作JSON。
用法：
  python3 direct_insert_page.py '<page_json_object_string>'
  或通过stdin传入JSON对象字符串
"""
import json
import sys
import os

SNAPSHOT_FILE = "/workspace/all_pages_data.json"

def main():
    # 读取JSON对象字符串
    if len(sys.argv) >= 2:
        json_str = sys.argv[1]
    else:
        json_str = sys.stdin.read()
    
    try:
        page_obj = json.loads(json_str)
    except Exception as e:
        print(f"ERROR 解析JSON对象失败: {e}", file=sys.stderr)
        print(f"输入前200字符: {repr(json_str[:200])}", file=sys.stderr)
        sys.exit(1)
    
    current_page = str(page_obj.get('currentPage', 'unknown'))
    if not page_obj.get('data') or len(page_obj.get('data')) == 0:
        print(f"WARNING page {current_page}: data为空，跳过", file=sys.stderr)
    
    # 读取已有的数据
    existing = []
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = []
    
    # 按currentPage去重替换
    existing = [p for p in existing if str(p.get('currentPage')) != current_page]
    existing.append(page_obj)
    
    # 排序
    def sort_key(p):
        try:
            return int(str(p.get('currentPage', '0')))
        except Exception:
            return 0
    existing.sort(key=sort_key)
    
    with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"OK 已写入页 {current_page}，合计 {len(existing)} 页，本页 {len(page_obj.get('data',[]))} 行数据")

if __name__ == "__main__":
    main()
