import csv
import os

CSV_PATH = "/workspace/star_report_cost_over_2000_2026-08-05_06-23.csv"

headers = [
    "素材ID（巨量）", "标题", "星图任务ID", "星图任务名称",
    "抖音号昵称", "抖音号", "视频播放链接", "下单账户名称",
    "消耗", "产品名称", "数据统计日期"
]

rows = [
    [
        "7660509756013215754",
        "点击视频下方链接，就能领红包 #抖音商城 #福利多多 #剪辑制作 #签到 #网赚",
        "7657431178504634394",
        "新LOGO-抖音商城APP-NG-AI签到01-鲸鱼",
        "智能效率社",
        "42513895368",
        "https://douyin.com/video/7660509798789696787",
        "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1",
        "13148.6",
        "",
        "2026-08-05"
    ],
    [
        "7665252172604293120",
        "碎片时间解闷，打开红果畅快刷短剧 #红果短剧 #AI #HWJLYM",
        "7626972396727304228",
        "红果-NG星广ad-短剧综述AI-鲸鱼",
        "小余爱追剧",
        "38139081311",
        "https://douyin.com/video/7665251894918466879",
        "红果KOC-鲸鱼-站内-拉新-1",
        "8488.31",
        "",
        "2026-08-05"
    ],
    [
        "7665251108878778395",
        "居家休闲神器，红果海量短剧随便看 #红果短剧 #AI #HWJLYM",
        "7626972396727304228",
        "红果-NG星广ad-短剧综述AI-鲸鱼",
        "小余爱追剧",
        "38139081311",
        "https://douyin.com/video/7665251159195618602",
        "红果KOC-鲸鱼-站内-拉新-1",
        "2627.91",
        "",
        "2026-08-05"
    ]
]

with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

sorted_rows = sorted(rows, key=lambda r: float(r[8]), reverse=True)

md_lines = []
md_lines.append("## 【消耗预警】星广报表实时消耗>2000")
md_lines.append("统计时间：2026-08-05 06:23")
md_lines.append("| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |")
md_lines.append("|-----------|------|------|---------|------|")

for row in sorted_rows:
    nickname = row[4]
    title = row[1]
    cost = row[8]
    video_url = row[6]
    date = row[10]
    md_lines.append(f"| {nickname} | {title} | {cost} | [观看]({video_url}) | {date} |")

md_lines.append(f"共{len(sorted_rows)}条记录消耗超过2000元")

feishu_msg = "\n".join(md_lines)
print(feishu_msg)
