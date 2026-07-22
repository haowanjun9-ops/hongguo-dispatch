# 红果素材分发平台（多人实时共享版）

一个给「红果素材上传」做账号 / 任务分发与统计的小工具：

- 一个账号 = 一个任务，每天上限 **6 条**，次日凌晨自动刷新。
- 按素材类型分：**真人 / AI / 二剪**，账号和任务各自归类。
- 输入需要的条数，自动挑出可用账号 + 对应任务派单，并实时统计剩余。
- 多人同时打开实时同步（SSE），**不会重复占用同一个号 / 同一个任务**。
- 写操作带访问密码（环境变量 `PASSCODE`），防止外人乱改。

## 本地运行

```bash
npm install
PORT=3000 PASSCODE=你的密码 node server.js
# 打开 http://localhost:3000
```

数据存在 `data.json`（首次运行自动用内置种子初始化；删除即重置）。

## 一键部署到 Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/haowanjun9-ops/hongguo-dispatch)

点上面的按钮（或把链接里的 `USERNAME/REPO` 换成你的仓库）即可一键部署。

部署后在 Render 控制台的 **Environment** 里设置 `PASSCODE`（访问密码）。
数据持久化：仓库已配置 `DATA_DIR=/data` 并挂了持久盘，账号/任务/每日计数重启后保留。
（持久盘需要付费实例；用免费实例时重启会回到初始种子数据。）

## 接口一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/state` | 公开状态（账号/任务/剩余/今日是否需密码） |
| GET | `/api/events` | SSE 实时推送 |
| POST | `/api/dispatch` | 派单 `{type,need}`（需密码） |
| POST | `/api/inc` `/api/dec` | 账号 +1 / −1（需密码） |
| POST | `/api/account` `/api/task` | 新增账号 / 任务（需密码） |
| POST | `/api/reassign` | 改绑任务（需密码） |
| POST | `/api/reset` | 清零今日计数（需密码） |
| DELETE | `/api/account/:id` | 删除账号（需密码） |
