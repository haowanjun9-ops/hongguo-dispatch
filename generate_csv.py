#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import os
from datetime import datetime

# 获取当前时间
now = datetime.now()
date_str = now.strftime('%Y-%m-%d')
time_str = now.strftime('%H-%M')
csv_path = f'/workspace/self_video_daily_by_editor_{date_str}_{time_str}.csv'

# 今日明细数据 (2026-08-05)
detail_data = [
    {
        'videoId': '26080509500548',
        'title': '红果短剧不用解锁解锁直达大结局!',
        'director': '杨婷婷',
        'editor': '刘东傲',
        'starAuditStatus': '持续计费中',
        'uploadTime': '2026-08-05 09:49:57',
        'teamSource': '内部团队/星广五组',
        'materialCategory': '素材剪辑（无达人出镜）',
        'orderId': '102311',
        'douyinAccount': '29826331833',
        'douyinNickname': '动态漫不打烊',
        'orderName': 'M8W1-红果短剧koc-刘振华-1100',
        'publishStatus': '已发布',
        'internalAuditStatus': '通过',
        'materialIdJuliang': '7670370689322090532'
    },
    {
        'videoId': '26080509472368',
        'title': '告别片荒 红果短剧无套路追剧!',
        'director': '董千雨',
        'editor': '刘东傲',
        'starAuditStatus': '持续计费中',
        'uploadTime': '2026-08-05 09:47:15',
        'teamSource': '内部团队/星广五组',
        'materialCategory': '素材剪辑（无达人出镜）',
        'orderId': '102311',
        'douyinAccount': '70750480392',
        'douyinNickname': '推啊推啊推',
        'orderName': 'M8W1-红果短剧koc-刘振华-1100',
        'publishStatus': '已发布',
        'internalAuditStatus': '通过',
        'materialIdJuliang': '7670370794804445230'
    },
    {
        'videoId': '26080509472371',
        'title': '红果短剧看短剧无烦恼',
        'director': '董千雨',
        'editor': '刘东傲',
        'starAuditStatus': '持续计费中',
        'uploadTime': '2026-08-05 09:47:15',
        'teamSource': '内部团队/星广五组',
        'materialCategory': '素材剪辑（无达人出镜）',
        'orderId': '102311',
        'douyinAccount': '70750480392',
        'douyinNickname': '推啊推啊推',
        'orderName': 'M8W1-红果短剧koc-刘振华-1100',
        'publishStatus': '已发布',
        'internalAuditStatus': '通过',
        'materialIdJuliang': '7670375820704448522'
    },
    {
        'videoId': '26080509472382',
        'title': '红果短剧能免费看类型齐全满足你',
        'director': '杨婷婷',
        'editor': '刘东傲',
        'starAuditStatus': '持续计费中',
        'uploadTime': '2026-08-05 09:47:15',
        'teamSource': '内部团队/星广五组',
        'materialCategory': '素材剪辑（无达人出镜）',
        'orderId': '102311',
        'douyinAccount': '70750480392',
        'douyinNickname': '推啊推啊推',
        'orderName': 'M8W1-红果短剧koc-刘振华-1100',
        'publishStatus': '已发布',
        'internalAuditStatus': '通过',
        'materialIdJuliang': '7670374352144760872'
    },
    {
        'videoId': '26080509472378',
        'title': '告别片荒无套路追剧!',
        'director': '武丽婷',
        'editor': '刘东傲',
        'starAuditStatus': '持续计费中',
        'uploadTime': '2026-08-05 09:47:15',
        'teamSource': '内部团队/星广五组',
        'materialCategory': '素材剪辑（无达人出镜）',
        'orderId': '102311',
        'douyinAccount': '70750480392',
        'douyinNickname': '推啊推啊推',
        'orderName': 'M8W1-红果短剧koc-刘振华-1100',
        'publishStatus': '已发布',
        'internalAuditStatus': '通过',
        'materialIdJuliang': '7670373450922737704'
    },
    {
        'videoId': '26080509472364',
        'title': '热门短剧任意看 就在红果短剧',
        'director': '董千雨',
        'editor': '刘东傲',
        'starAuditStatus': '持续计费中',
        'uploadTime': '2026-08-05 09:47:15',
        'teamSource': '内部团队/星广五组',
        'materialCategory': '素材剪辑（无达人出镜）',
        'orderId': '102311',
        'douyinAccount': '70750480392',
        'douyinNickname': '推啊推啊推',
        'orderName': 'M8W1-红果短剧koc-刘振华-1100',
        'publishStatus': '已发布',
        'internalAuditStatus': '通过',
        'materialIdJuliang': '7670370772951990307'
    },
    {
        'videoId': '26080509472375',
        'title': '告别付费短剧红果短剧免费看全集',
        'director': '董千雨',
        'editor': '刘东傲',
        'starAuditStatus': '服务商审核中',
        'uploadTime': '2026-08-05 09:47:15',
        'teamSource': '内部团队/星广五组',
        'materialCategory': '素材剪辑（无达人出镜）',
        'orderId': '102311',
        'douyinAccount': '70750480392',
        'douyinNickname': '推啊推啊推',
        'orderName': 'M8W1-红果短剧koc-刘振华-1100',
        'publishStatus': '已发布',
        'internalAuditStatus': '通过',
        'materialIdJuliang': '7670372578793259054'
    }
]

# 按后期汇总统计
summary = {}
for row in detail_data:
    editor = row['editor'] or '(未填写)'
    if editor not in summary:
        summary[editor] = {
            'total': 0,
            '持续计费中': 0,
            '审核未通过': 0,
            '其他': 0
        }
    summary[editor]['total'] += 1
    status = row['starAuditStatus']
    if status == '持续计费中':
        summary[editor]['持续计费中'] += 1
    elif status == '审核未通过':
        summary[editor]['审核未通过'] += 1
    else:
        summary[editor]['其他'] += 1  # 已通过、服务商审核中、其他

# 写入CSV文件
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    
    # 汇总部分
    writer.writerow(['=== 汇总统计 ==='])
    writer.writerow(['统计日期', date_str])
    writer.writerow(['统计时间', now.strftime('%H:%M')])
    writer.writerow([])
    writer.writerow(['后期', '上传数量', '持续计费中', '审核未通过', '其他状态'])
    
    total_all = 0
    for editor, stats in summary.items():
        writer.writerow([
            editor,
            stats['total'],
            stats['持续计费中'],
            stats['审核未通过'],
            stats['其他']
        ])
        total_all += stats['total']
    writer.writerow(['合计', total_all, '', '', ''])
    writer.writerow([])
    writer.writerow([])
    
    # 明细部分
    writer.writerow(['=== 明细数据 ==='])
    writer.writerow([
        '视频ID', '标题', '编导', '后期', '星广审核状态',
        '上传时间', '团队来源', '素材分类', '订单ID', '订单名称',
        '抖音号', '抖音昵称', '发布状态', '内部审核状态', '素材ID（巨量）'
    ])
    
    for row in detail_data:
        writer.writerow([
            row['videoId'], row['title'], row['director'], row['editor'],
            row['starAuditStatus'], row['uploadTime'], row['teamSource'],
            row['materialCategory'], row['orderId'], row['orderName'],
            row['douyinAccount'], row['douyinNickname'], row['publishStatus'],
            row['internalAuditStatus'], row['materialIdJuliang']
        ])

print(f'CSV文件已生成: {csv_path}')
print(f'今日共 {total_all} 条素材')
print(f'汇总: {summary}')
