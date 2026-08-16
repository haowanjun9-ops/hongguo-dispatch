import sys, json
headers = ['素材ID（巨量）','标题','星图任务ID','星图任务名称','抖音号昵称','抖音号','视频播放链接','下单账户名称','消耗','产品名称','数据统计日期']
cells_str = sys.argv[1]  # comma-separated cell values (200 items = 20 rows x 10 cols, product_name is empty)
page = sys.argv[2]

items = []
current = []
in_quote = False
buf = ""
for ch in cells_str:
    if ch == '"' and (not buf or buf[-1] != '\\'):
        in_quote = not in_quote
    elif ch == ',' and not in_quote:
        current.append(buf)
        buf = ""
        if len(current) == 10:
            # Insert empty product name at position 9 (index 9)
            row = {}
            for i, h in enumerate(headers):
                if i < 9:
                    val = current[i]
                elif i == 9:
                    val = ''
                else:
                    val = current[i-1]
                # For link fields (video link=index 6), keep link empty; we don't have it in snapshot
                if h == '视频播放链接':
                    row[h] = {'text': val, 'link': val if val.startswith('http') else ''}
                else:
                    row[h] = {'text': val, 'link': ''}
            items.append(row)
            current = []
    else:
        buf += ch
if buf:
    current.append(buf)
if len(current) == 10:
    row = {}
    for i, h in enumerate(headers):
        if i < 9:
            val = current[i]
        elif i == 9:
            val = ''
        else:
            val = current[i-1]
        if h == '视频播放链接':
            row[h] = {'text': val, 'link': val if val.startswith('http') else ''}
        else:
            row[h] = {'text': val, 'link': ''}
    items.append(row)

page_obj = {
    'headers': headers,
    'currentPage': str(page),
    'data': items,
    'dataCount': len(items),
    'success': True
}

import subprocess
json_str = json.dumps(page_obj, ensure_ascii=False)
result = subprocess.run(['python3', '/workspace/direct_insert_page.py'], 
                       input=json_str, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])
