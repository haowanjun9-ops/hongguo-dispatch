import subprocess

markdown_content = """## 【消耗预警】星广报表实时消耗>2000
统计时间：2026-08-05 06:23
| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |
|-----------|------|------|---------|------|
| 智能效率社 | 点击视频下方链接，就能领红包 #抖音商城 #福利多多 #剪辑制作 #签到 #网赚 | 13148.6 | [观看](https://douyin.com/video/7660509798789696787) | 2026-08-05 |
| 小余爱追剧 | 碎片时间解闷，打开红果畅快刷短剧 #红果短剧 #AI #HWJLYM | 8488.31 | [观看](https://douyin.com/video/7665251894918466879) | 2026-08-05 |
| 小余爱追剧 | 居家休闲神器，红果海量短剧随便看 #红果短剧 #AI #HWJLYM | 2627.91 | [观看](https://douyin.com/video/7665251159195618602) | 2026-08-05 |
共3条记录消耗超过2000元"""

args = [
    "lark-cli",
    "im",
    "+messages-send",
    "--as",
    "user",
    "--chat-id",
    "oc_74cf357efbbda7b35af5078abcb29bdb",
    "--markdown",
    markdown_content,
]

result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")

print("返回码:", result.returncode)
print("stdout:")
print(result.stdout)
print("stderr:")
print(result.stderr)

if result.returncode != 0:
    print("错误：命令执行失败，返回码非0")
