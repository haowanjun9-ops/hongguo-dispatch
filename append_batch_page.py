#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单追加单页数据到批量文件 all_batches.txt
用法: append_batch_page.py <page_num> <raw_result_string>
raw_result_string 就是 Exec 返回的 Result: "{...}" 的整个字符串
"""
import sys
import os

BATCH_FILE = "/workspace/all_batches.txt"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("ERROR: need page_num and raw_result")
        sys.exit(1)
    page_num = sys.argv[1]
    raw_result = sys.argv[2]
    # 处理直接传整个 Result: "..." 字符串
    with open(BATCH_FILE, 'a', encoding='utf-8') as f:
        f.write(f"===PAGE_{page_num}==={raw_result}\n")
    print(f"追加 PAGE_{page_num} 成功，原始字符串长度={len(raw_result)}")
