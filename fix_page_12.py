#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辅助脚本：解析 page_12_batch.txt 的格式问题并修复
标题中有未转义的双引号："口粮" -> 需要转义
"""
import json
import re
import os

SNAPSHOT_FILE = "/workspace/all_pages_data.json"

def smart_fix_json(json_str, page_num):
    """尝试智能修复 JSON"""
    # 尝试找出有问题的字段并修复
    # 问题出在："标题":{"text":"红果短剧：看剧也能攒 "口粮"，太贴心lh..."}
    # 这里 "口粮" 的双引号应该转义
    
    fixes = [
        # 找出 text 字段值中未转义的双引号模式
        # 策略：找出 "text":"...", 中间如果有单独的 " 不是紧跟 , 或 } 的，就是问题
    ]
    
    # 方法：逐行查找问题位置
    # 已知问题在 char 6646 附近
    # 让我手动修复已知问题： 攒 "口粮" -> 攒 \"口粮\"
    
    fixed = json_str.replace('攒 "口粮"', '攒 \\"口粮\\"')
    
    # 检查是否还有其他类似问题
    # 查找 text 字段中的双引号问题
    pattern = r'"text":"(.*?)"(?=\s*,\s*"link"|$)'
    
    try:
        obj = json.loads(fixed)
        return obj
    except json.JSONDecodeError as e:
        print(f"  修复后仍然错误: {e}")
        print(f"  位置 {e.pos} 附近: {repr(fixed[max(0,e.pos-50):e.pos+50])}")
        return None

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    m = re.match(r'===PAGE_(\d+)===', content)
    if not m:
        return None
    page_num = m.group(1)
    rest = content[m.end():].strip()
    
    if rest.startswith('Result: "') and rest.endswith('"'):
        json_str = rest[len('Result: "'):-1]
    else:
        return None
    
    # 先尝试直接解析
    try:
        obj = json.loads(json_str)
        obj['currentPage'] = str(obj.get('currentPage', page_num))
        return obj
    except json.JSONDecodeError:
        pass
    
    # 尝试智能修复
    return smart_fix_json(json_str, page_num)

if __name__ == "__main__":
    existing = []
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except:
            existing = []
    
    obj = process_file('page_12_batch.txt')
    if obj:
        print(f"page_12 修复成功! page={obj.get('currentPage')}, {len(obj.get('data',[]))} 行")
        cp = str(obj.get('currentPage'))
        existing = [p for p in existing if str(p.get('currentPage')) != cp]
        existing.append(obj)
        
        def sort_key(p):
            try:
                return int(str(p.get('currentPage', '0')))
            except:
                return 0
        existing.sort(key=sort_key)
        
        with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        
        pages = [str(p.get('currentPage','?')) for p in existing]
        print(f"当前总页数: {len(existing)}, 页码: {','.join(pages)}")
        print(f"每页行数: {[len(p.get('data',[])) for p in existing]}")
    else:
        print("page_12 修复失败，需要进一步手动处理")
