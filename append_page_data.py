#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
追加采集的分页数据到总数据文件
"""
import json
import sys
import os

WORKSPACE = "/workspace"
SNAPSHOT_FILE = os.path.join(WORKSPACE, "all_pages_data.json")

def append_page(page_json_str):
    """追加单页数据到文件"""
    try:
        page_data = json.loads(page_json_str)
    except Exception as e:
        print(f"解析JSON失败: {e}", file=sys.stderr)
        return False, 0
    
    existing = []
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except:
            existing = []
    
    # 检查是否已有该页
    current_page = page_data.get('currentPage', 'unknown')
    existing = [p for p in existing if p.get('currentPage') != current_page]
    existing.append(page_data)
    
    # 按页码排序
    def sort_key(p):
        try:
            return int(p.get('currentPage', '0'))
        except:
            return 0
    existing.sort(key=sort_key)
    
    with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    return True, len(existing)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: append_page_data.py <json_string>")
        sys.exit(1)
    json_str = sys.argv[1]
    ok, n = append_page(json_str)
    if ok:
        print(f"追加成功，当前共 {n} 页数据")
    else:
        print("追加失败")
        sys.exit(1)
