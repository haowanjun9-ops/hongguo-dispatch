#!/bin/bash
# 构造消息并发送

# 获取当前时间
DATE=$(date '+%Y-%m-%d')
TIME=$(date '+%H:%M')

# 构造Markdown消息
read -r -d '' MARKDOWN << 'EOF'
## 【每日统计】自产视频后期素材上传+审核状态

统计时间：2026-08-05 06:07
日期：2026-08-05

| 后期 | 上传数量 | 持续计费中 | 审核未通过 | 其他 |
|------|---------|-----------|------------|------|
| 刘东傲 | 7 | 6 | 0 | 1 |

合计：7条素材
EOF

echo "发送消息内容："
echo "$MARKDOWN"
echo ""

# 发送消息
lark-cli im +messages-send --as user --chat-id oc_74cf357efbbda7b35af5078abcb29bdb --markdown "$MARKDOWN"
