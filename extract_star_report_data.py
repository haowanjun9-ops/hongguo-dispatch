#!/usr/bin/env python3
"""
鲸准3.0星广报表数据提取脚本
用于提取消耗超过2000的记录并通过飞书发送通知
"""

import json
import csv
import subprocess
from datetime import datetime
from pathlib import Path

# 从浏览器提取的数据
extracted_data_json = '''
[
  {"素材ID(巨量)": "7665251108878778395", "标题": "居家休闲神器，红果海量短剧随便看 #红果短剧 #AI #HWJLYM", "星图任务ID": "7626972396727304228", "星图任务名称": "红果-NG星广ad-短剧综述AI-鲸鱼", "抖音号昵称": "小余爱追剧", "抖音号": "38139081311", "视频播放链接": "https://douyin.com/video/7665251159195618602", "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1", "消耗": "6449.69", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7665252172604293120", "标题": "碎片时间解闷，打开红果畅快刷短剧 #红果短剧 #AI #HWJLYM", "星图任务ID": "7626972396727304228", "星图任务名称": "红果-NG星广ad-短剧综述AI-鲸鱼", "抖音号昵称": "小余爱追剧", "抖音号": "38139081311", "视频播放链接": "https://douyin.com/video/7665251894918466879", "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1", "消耗": "6010.82", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7660509756013215754", "标题": "点击视频下方链接，就能领红包 #抖音商城 #福利多多 #剪辑制作 #签到 #网赚", "星图任务ID": "7657431178504634394", "星图任务名称": "新LOGO-抖音商城APP-NG-AI签到01-鲸鱼", "抖音号昵称": "智能效率社", "抖音号": "42513895368", "视频播放链接": "https://douyin.com/video/7660509798789696787", "下单账户名称": "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1", "消耗": "2305.75", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7670162447438086207", "标题": "收纳每一日签到光阴，相守越久福利持续加码 #抖音商城 #福利多多 #网赚 #签到 #剪辑制作", "星图任务ID": "7657431178504634394", "星图任务名称": "新LOGO-抖音商城APP-NG-AI签到01-鲸鱼", "抖音号昵称": "小余爱追剧", "抖音号": "38139081311", "视频播放链接": "https://douyin.com/video/7670162481460809011", "下单账户名称": "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1", "消耗": "1580.57", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7577295876219912198", "标题": "熬夜追完！脑子喊停手却很诚实mh #番茄小说 #爆火短剧 #免费短剧", "星图任务ID": "7571363215192948779", "星图任务名称": "番茄短剧-综述NG-霍尔果斯海洋无限", "抖音号昵称": "出片达人小葵", "抖音号": "50499034533", "视频播放链接": "https://douyin.com/video/7577295879841926434", "下单账户名称": "鲸鱼-UG星广-内广星广番茄2.0-主账户", "消耗": "1247.42", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7579978533608062976", "标题": "熬夜冠军：这短剧我能再追十集mh #番茄小说 #爆火短剧 #免费短剧", "星图任务ID": "7576919195879833609", "星图任务名称": "koc番茄小说-NG星广ad-真人短剧综述-鲸鱼", "抖音号昵称": "外卖阿彭", "抖音号": "42068123484", "视频播放链接": "https://douyin.com/video/7579978441886403892", "下单账户名称": "KOC达人-番茄小说-鲸鱼-站内-1", "消耗": "1234.29", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7670146998571548710", "标题": "抖音商城天天打卡，签到红包福利领不停 #网赚 #签到 #真人实拍 #福利多多 #抖音商城", "星图任务ID": "7641104807520763955", "星图任务名称": "新LOGO-抖音商城APP-NG-签到01-鲸鱼", "抖音号昵称": "NPCCCCC", "抖音号": "69225019744", "视频播放链接": "https://douyin.com/video/7670147074964409638", "下单账户名称": "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1", "消耗": "956.8", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7670744432280993843", "标题": "在家躺着刷短剧，红果海量剧集随便看 #红果短剧 #AI #HWJLYM", "星图任务ID": "7660403527034355763", "星图任务名称": "红果-NG星广ad-短剧综述AI-02-鲸鱼", "抖音号昵称": "推啊推啊推", "抖音号": "70750480392", "视频播放链接": "https://douyin.com/video/7670744515669429523", "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1", "消耗": "900.99", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7668598813511712802", "标题": "利用碎片时间放松，完整版短剧随时刷起来 #hwj #红果短剧 #潜力", "星图任务ID": "7661895222078521354", "星图任务名称": "红果-NG星广ad-真人综述-实拍-01-鲸鱼", "抖音号昵称": "会爆", "抖音号": "48733321382", "视频播放链接": "https://douyin.com/video/7668598758090788115", "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1", "消耗": "689.24", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7657491700799012915", "标题": "结伴打卡乐趣多，大奖轻松瓜分 #网赚 #签到 #真人实拍 #福利多多 #抖音商城", "星图任务ID": "7641104807520763955", "星图任务名称": "新LOGO-抖音商城APP-NG-签到01-鲸鱼", "抖音号昵称": "追剧充电站", "抖音号": "50669015630", "视频播放链接": "https://douyin.com/video/7657491794162208054", "下单账户名称": "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1", "消耗": "622.68", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7582185373347086379", "标题": "免费短剧大揭秘 #ZR #番茄小说 #爆火短剧 #jh", "星图任务ID": "7571363521675231241", "星图任务名称": "番茄短剧-综述03NG-霍尔果斯海洋无限", "抖音号昵称": "乐乐和毛毛", "抖音号": "75420498098", "视频播放链接": "https://douyin.com/video/7582185342334192911", "下单账户名称": "鲸鱼-UG星广-内广星广番茄2.0-主账户", "消耗": "580.01", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7649358822086426633", "标题": "省钱羊毛党速蹲！抖音商城一分起购，好物包邮带回家 #电商 #1分购 #真人实拍 #福利多多 #抖音商城", "星图任务ID": "7641104691696533513", "星图任务名称": "新LOGO-抖音商城APP-NG-电商真人实拍01-鲸鱼", "抖音号昵称": "智能效率社", "抖音号": "42513895368", "视频播放链接": "https://douyin.com/video/7649358873077321012", "下单账户名称": "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1", "消耗": "508.35", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7644849828461150234", "标题": "随心点开，欢乐即刻抵达 #红果短剧 #真人 #zcsc #H13", "星图任务ID": "7566459273833037878", "星图任务名称": "红果-NG星广ad-真人综述-02-霍尔果斯海洋无限", "抖音号昵称": "寻剧千百遍", "抖音号": "90287096322", "视频播放链接": "https://douyin.com/video/7644849847031319844", "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1", "消耗": "488.0", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7621132232400945179", "标题": "如何跟crush聊天！ #多闪 #多闪app #H9", "星图任务ID": "7605914191668625427", "星图任务名称": "多闪|AD星广联投高佣达人投稿任务x海洋无限xM1【ai精灵01】-鲸鱼", "抖音号昵称": "超荟看剧", "抖音号": "84179057014", "视频播放链接": "https://douyin.com/video/7621132221570764083", "下单账户名称": "UG多闪-站内-拉新-鲸鱼折扣-次双-and-25", "消耗": "401.06", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7579170957429800970", "标题": "红果短剧开黑？快乐直接翻倍mh #红果 #刷剧好搭档 #爆火短剧 #ZR", "星图任务ID": "7566460022732111881", "星图任务名称": "红果-NG星广ad-真人综述-03-霍尔果斯海洋无限", "抖音号昵称": "券券喂饱你", "抖音号": "54621012853", "视频播放链接": "https://douyin.com/video/7579170967709142287", "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1", "消耗": "396.81", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7580438677732687912", "标题": "红果短剧太绝，无聊全部溶解mh #红果短剧 #刷剧好搭档 #爆火短剧 #ZR", "星图任务ID": "7566460022732111881", "星图任务名称": "红果-NG星广ad-真人综述-03-霍尔果斯海洋无限", "抖音号昵称": "出片达人小葵", "抖音号": "50499034533", "视频播放链接": "https://douyin.com/video/7580438215606226210", "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1", "消耗": "394.57", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7647373173966159912", "标题": "高分热播短剧齐全，全篇剧情轻轻松松看完 #真人 #H8 #zcsc #红果短剧", "星图任务ID": "7565814540873711643", "星图任务名称": "红果短剧-NG综述-02-霍尔果斯海洋无限", "抖音号昵称": "出片达人小葵", "抖音号": "50499034533", "视频播放链接": "https://douyin.com/video/7647373123767094543", "下单账户名称": "鲸鱼-UG星广-内广星广红果2.0-20", "消耗": "338.78", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7670531977377202230", "标题": "简单一键签到，省去复杂操作领取福利 #网赚 #签到 #真人实拍 #福利多多 #抖音商城", "星图任务ID": "7641104807520763955", "星图任务名称": "新LOGO-抖音商城APP-NG-签到01-鲸鱼", "抖音号昵称": "我的智能外挂", "抖音号": "97830164197", "视频播放链接": "https://douyin.com/video/7670532019411062056", "下单账户名称": "抖音商城版-端拉新-星广联投-占位-内广-欧阳朔-霍尔果斯-1", "消耗": "338.46", "数据统计日期": "2026-08-07"},
  {"素材ID(巨量)": "7668947650973466633", "标题": "上千部完整版短剧，通勤摸鱼随便刷 #红果短剧 #潜力 #hwj", "星图任务ID": "7661895222078521354", "星图任务名称": "红果-NG星广ad-真人综述-实拍-01-鲸鱼", "抖音号昵称": "会爆", "抖音号": "48733321382", "视频播放链接": "https://douyin.com/video/7668947802197642534", "下单账户名称": "红果KOC-鲸鱼-站内-拉新-1", "消耗": "332.66", "数据统计日期": "2026-08-07"}
]
'''

def extract_data():
    """解析JSON数据"""
    try:
        data = json.loads(extracted_data_json)
        return data
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return []

def filter_high_cost_records(data, threshold=2000):
    """筛选消耗超过阈值的记录"""
    filtered_records = []
    
    for record in data:
        try:
            # 提取消耗字段的数值
            cost_str = record.get('消耗', '0')
            # 移除可能的逗号和其他字符，转换为浮点数
            cost = float(cost_str.replace(',', '').replace(' ', ''))
            
            if cost > threshold:
                filtered_records.append(record)
        except (ValueError, AttributeError) as e:
            print(f"解析消耗字段失败: {record.get('消耗')}, 错误: {e}")
            continue
    
    return filtered_records

def save_to_csv(data, file_path):
    """保存数据到CSV文件"""
    if not data:
        return False
    
    # 定义CSV列顺序
    fieldnames = ['素材ID(巨量)', '标题', '星图任务ID', '星图任务名称', '抖音号昵称', 
                  '抖音号', '视频播放链接', '下单账户名称', '消耗', '数据统计日期']
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        return True
    except Exception as e:
        print(f"保存CSV失败: {e}")
        return False

def create_feishu_message(records):
    """创建飞书消息内容"""
    if not records:
        return None
    
    # 获取当前时间
    now = datetime.now()
    time_str = now.strftime('%Y-%m-%d %H:%M')
    date_str = now.strftime('%Y-%m-%d')
    
    # 构建markdown消息
    message_lines = [
        "## 【消耗预警】星广报表实时消耗>2000",
        f"统计时间：{time_str}",
        "",
        "| 抖音号昵称 | 标题 | 消耗 | 视频链接 | 日期 |",
        "|-----------|------|------|---------|------|"
    ]
    
    for record in records:
        nickname = record.get('抖音号昵称', '')
        title = record.get('标题', '')
        cost = record.get('消耗', '')
        video_url = record.get('视频播放链接', '')
        date = record.get('数据统计日期', date_str)
        
        # 截断过长的标题
        if len(title) > 30:
            title = title[:30] + '...'
        
        # 格式化视频链接为markdown链接
        video_link = f"[观看]({video_url})" if video_url else ''
        
        message_lines.append(f"| {nickname} | {title} | {cost} | {video_link} | {date} |")
    
    message_lines.append(f"\n共{len(records)}条记录消耗超过2000元")
    
    return '\n'.join(message_lines)

def send_feishu_message(message, chat_id='oc_74cf357efbbda7b35af5078abcb29bdb'):
    """发送飞书消息"""
    try:
        # 使用lark-cli发送消息
        cmd = [
            'lark-cli', 'im', '+messages-send',
            '--as', 'user',
            '--chat-id', chat_id,
            '--markdown', message
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, "飞书消息发送成功"
        else:
            return False, f"飞书消息发送失败: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "飞书消息发送超时"
    except Exception as e:
        return False, f"发送飞书消息异常: {str(e)}"

def main():
    """主函数"""
    print("=" * 60)
    print("鲸准3.0星广报表数据提取任务开始")
    print("=" * 60)
    
    # 1. 提取数据
    print("\n1. 提取数据...")
    all_data = extract_data()
    print(f"   共提取 {len(all_data)} 条数据")
    
    # 2. 筛选消耗>2000的记录
    print("\n2. 筛选消耗>2000的记录...")
    filtered_data = filter_high_cost_records(all_data, threshold=2000)
    print(f"   共筛选出 {len(filtered_data)} 条消耗>2000的记录")
    
    # 3. 检查是否有符合条件的数据
    if not filtered_data:
        print("\n无超2000消耗数据，任务结束")
        return {
            'success': True,
            'total_records': len(all_data),
            'filtered_records': 0,
            'message_sent': False,
            'message': '无超2000消耗数据'
        }
    
    # 4. 保存CSV文件
    print("\n3. 保存CSV文件...")
    now = datetime.now()
    csv_filename = f"/workspace/star_report_cost_over_2000_{now.strftime('%Y-%m-%d_%H-%M')}.csv"
    
    if save_to_csv(filtered_data, csv_filename):
        print(f"   CSV文件保存成功: {csv_filename}")
    else:
        print(f"   CSV文件保存失败")
    
    # 5. 发送飞书消息
    print("\n4. 发送飞书消息...")
    message = create_feishu_message(filtered_data)
    
    if message:
        success, msg = send_feishu_message(message)
        if success:
            print(f"   {msg}")
        else:
            print(f"   {msg}")
    else:
        success = False
        msg = "创建飞书消息失败"
        print(f"   {msg}")
    
    # 6. 输出结果
    print("\n" + "=" * 60)
    print("任务执行完成")
    print("=" * 60)
    print(f"总数据条数: {len(all_data)}")
    print(f"筛选出消耗>2000的记录: {len(filtered_data)}")
    print(f"飞书消息发送状态: {'成功' if success else '失败'}")
    
    # 显示筛选出的记录详情
    if filtered_data:
        print("\n消耗>2000的记录:")
        for i, record in enumerate(filtered_data, 1):
            print(f"{i}. {record.get('抖音号昵称')} - {record.get('消耗')}元 - {record.get('标题')[:30]}...")
    
    return {
        'success': True,
        'total_records': len(all_data),
        'filtered_records': len(filtered_data),
        'csv_file': csv_filename if filtered_data else None,
        'message_sent': success
    }

if __name__ == '__main__':
    result = main()
    print(f"\n任务结果: {json.dumps(result, ensure_ascii=False, indent=2)}")