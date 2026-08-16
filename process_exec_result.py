#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理 Exec 返回结果并写入到 all_pages_data.json
用法:
  python3 process_exec_result.py '<RAW_EXEC_RESULT>'
RAW_EXEC_RESULT 格式: Result: "ESCAPED_JSON"
"""
import json
import sys
import subprocess
import os

SNAPSHOT_FILE = "/workspace/all_pages_data.json"

def process_result(raw_result):
    # 1. 提取 Result: 后的内容
    if not raw_result.startswith('Result:'):
        print(f"ERROR: 结果不以 Result: 开头，前200字符: {repr(raw_result[:200])}", file=sys.stderr)
        return False
    
    json_str_quoted = raw_result[len('Result:'):].strip()
    
    if json_str_quoted == 'undefined':
        print("ERROR: Result is undefined", file=sys.stderr)
        return False
    
    try:
        # 2. 第一层 JSON 解析：解析带引号的字符串 -> 得到 JSON 字符串
        inner_json_str = json.loads(json_str_quoted)
        # 3. 第二层 JSON 解析：解析 JSON 字符串 -> 得到对象
        page_obj = json.loads(inner_json_str)
    except Exception as e:
        print(f"ERROR 两层解析失败: {e}", file=sys.stderr)
        print(f"  json_str_quoted[:200]: {repr(json_str_quoted[:200])}", file=sys.stderr)
        return False
    
    if not page_obj.get('success'):
        print(f"ERROR: page_obj.success=False, error={page_obj.get('error')}", file=sys.stderr)
        return False
    
    # 4. 调用 direct_insert_page.py
    page_obj_json = json.dumps(page_obj, ensure_ascii=False)
    result = subprocess.run(
        ['python3', '/workspace/direct_insert_page.py', page_obj_json],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR direct_insert_page.py 失败: {result.stderr}", file=sys.stderr)
        return False
    print(result.stdout.strip())
    return True

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        raw = sys.argv[1]
    else:
        raw = sys.stdin.read()
    ok = process_result(raw)
    sys.exit(0 if ok else 1)
