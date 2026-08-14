import json
import os
import sys

def save_page(page_num, json_str):
    """保存单页JSON数据"""
    filepath = f"/workspace/page_data/page_{page_num}.json"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(json_str)
    data = json.loads(json_str)
    print(f"[保存] page_{page_num}.json: {len(data.get('rows',[]))} 行数据")

if __name__ == "__main__":
    # 第一页数据（从命令行传入）
    if len(sys.argv) > 2:
        page_num = int(sys.argv[1])
        json_file = sys.argv[2]
        with open(json_file, 'r', encoding='utf-8') as f:
            save_page(page_num, f.read())
    print("done")
