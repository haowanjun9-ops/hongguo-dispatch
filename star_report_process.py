import json
import csv
import os
from datetime import datetime

SNAPSHOT_DATA = """[{"mid":"7670531977377202230","title":"简单一键签到，省去复杂操作领取福利 #网赚 #签到 #真人实拍 #福利多多 #抖音商城","nickname":"我的智能外挂","dyid":"97830164197","vurl":"https://douyin.com/video/7670532019411062056","acct":"抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1","cost":"26892.18","prod":"抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1","date":"2026-08-17"},{"mid":"7673933091103309874","title":"简单每日签到行动，时光回馈各式各样暖心礼遇 #网赚 #签到 #抖音商城  #福利多多 #AI","nickname":"效率火箭","dyid":"60057878563","vurl":"https://douyin.com/video/7673933564391476480","acct":"抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1","cost":"6122.77","prod":"抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1","date":"2026-08-17"},{"mid":"7670154435016540169","title":"长久坚守每日签到，累计打卡时日越多福利等级越高 #抖音商城 #签到 #网赚 #福利多多 #剪辑制作","nickname":"苏苏说说看","dyid":"97720499428","vurl":"https://douyin.com/video/7670154522911657250","acct":"抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1","cost":"5290.27","prod":"抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1","date":"2026-08-17"},{"mid":"7670910071551918126","title":"每日福利更新，签到抢先拿到限时权益 #网赚 #签到 #真人实拍 #福利多多 #抖音商城","nickname":"苏苏有话说","dyid":"91733539137","vurl":"https://douyin.com/video/7670910194758520090","acct":"抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1","cost":"2566.14","prod":"抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1","date":"2026-08-17"}]"""


def extract_table_data(snapshot_text):
    """解析快照数据，提取所有表格行"""
    records = json.loads(snapshot_text)
    return records


def filter_mall_records(records):
    """筛选产品名称包含'抖音商城'的记录"""
    return [r for r in records if r.get("prod") and "抖音商城" in r["prod"]]


def calc_total_cost(records):
    """计算总消耗"""
    return sum(float(r.get("cost", 0)) for r in records)


def filter_cost_over(records, threshold):
    """筛选消耗超过阈值的记录"""
    return [r for r in records if float(r.get("cost", 0)) > threshold]


def save_csv(records, filename):
    """保存CSV到/workspace"""
    filepath = f"/workspace/{filename}.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["抖音号昵称", "标题", "消耗", "视频链接", "日期"])
        for r in records:
            writer.writerow([
                r.get("nickname", ""),
                r.get("title", ""),
                r.get("cost", ""),
                r.get("vurl", ""),
                r.get("date", ""),
            ])
    return filepath


def build_markdown_message(records, total_cost):
    """构造markdown消息"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "## 【消耗预警】星广报表抖音商城消耗统计",
        "",
        f"统计时间：{now}",
        "",
        "| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |",
        "|---|---|---|---|---|",
    ]
    for r in records:
        lines.append(
            f"| {r['nickname']} | {r['title'][:30]} | {r['cost']} | [观看]({r['vurl']}) | {r['date']} |"
        )
    lines.append("")
    lines.append(f"共{len(records)}条记录消耗超过2000元")
    lines.append(f"抖音商城总消耗：{total_cost:.2f}元")
    return "\n".join(lines)


def send_lark_message(md_content):
    """发送飞书消息（由外部lark-cli调用执行）"""
    print("需要发送以下飞书消息：")
    print(md_content)
    return True


def main():
    print("=" * 60)
    print("星广报表抖音商城消耗统计")
    print("=" * 60)

    # Step a: 解析数据
    records = extract_table_data(SNAPSHOT_DATA)
    print(f"\n共解析 {len(records)} 条记录")

    # Step b: 筛选抖音商城记录
    mall_records = filter_mall_records(records)
    print(f"抖音商城记录: {len(mall_records)} 条")

    # Step c: 若为空或总消耗<=0，结束
    if not mall_records:
        print("抖音商城记录为空，结束流程")
        return

    total_cost = calc_total_cost(mall_records)
    if total_cost <= 0:
        print(f"抖音商城总消耗为 {total_cost}，结束流程")
        return

    # Step d: 计算总消耗
    print(f"抖音商城总消耗: {total_cost:.2f} 元")

    # Step e: 筛选消耗>2000
    over_threshold = filter_cost_over(mall_records, 2000)
    print(f"消耗超过2000元的记录: {len(over_threshold)} 条")

    # Step f: 保存CSV
    csv_path = save_csv(over_threshold, "mall_cost_over_2000")
    print(f"CSV已保存: {csv_path}")

    # Step g: 构造markdown
    md_content = build_markdown_message(over_threshold, total_cost)
    print(f"\nMarkdown消息已构造")

    # Step h: 发送飞书消息
    send_lark_message(md_content)
    print("\n流程完成！")


if __name__ == "__main__":
    main()