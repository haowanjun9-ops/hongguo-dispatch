# 红果素材分发平台（多人实时共享版）

一个给「红果素材上传」做账号 / 任务分发与统计的小工具：

- 一个账号 = 一个任务，每天上限 **6 条**，次日凌晨自动刷新。
- 按素材类型分：**真人 / AI / 二剪**，账号和任务各自归类。
- 输入需要的条数，自动挑出可用账号 + 对应任务派单，并实时统计剩余。
- 多人同时打开实时同步（SSE），**不会重复占用同一个号 / 同一个任务**。
- 写操作带权限：**管理员**可派单、增删账号/任务、±1、刷新；**普通用户**只能查看剩余次数。

## 权限模型（两级）

| 角色 | 密码变量 | 能做什么 |
| --- | --- | --- |
| 👑 管理员 | `ADMIN_PASSCODE` | 全部：派单、新增/删除账号与任务、改绑、±1、刷新今日 |
| 👁 普通用户 | `PASSCODE` | 仅查看剩余次数与账号/任务列表（只读） |

> `ADMIN_PASSCODE` 未单独设置时退化为等于 `PASSCODE`（即一个密码同时是管理员）。
> 想区分两級，把 `ADMIN_PASSCODE` 设成和 `PASSCODE` 不同的值即可。

## 本地运行

```bash
npm install
# 管理员密码=admin123，普通用户密码=user123
PORT=3000 PASSCODE=user123 ADMIN_PASSCODE=admin123 node server.js
# 打开 http://localhost:3000
```

数据存在 `data.json`（首次运行自动用内置种子初始化；删除即重置）。

## 一键部署到 Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/haowanjun9-ops/hongguo-dispatch)

点上面的按钮（或把链接里的 `USERNAME/REPO` 换成你的仓库）即可一键部署。

部署后 Render 会自动生成一个随机 `PASSCODE`（普通用户密码），你可以在控制台的 **Environment** 里：
- 把 `PASSCODE` 改成你想给普通同事的密码；
- 给 `ADMIN_PASSCODE` 设一个**不同的**值作为管理员密码（不填则默认等于 `PASSCODE`）。
改完保存即自动重新部署。

> **免费实例数据不持久**：免费计划没有持久盘，每次重新部署/服务重启后 `data.json` 会重置为初始种子数据（账号/任务清单还在，当日计数和新增账号会丢失）。
> 若需完整持久化，请在 Render 控制台把实例升到付费计划，并在 `render.yaml` 里加回 `disk` 配置 + `DATA_DIR=/data`。

## 接口一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/state` | 公开状态（账号/任务/剩余/今日是否需密码） |
| POST | `/api/auth` | 校验密码，返回 `{ok, role}`（`admin` / `user`） |
| GET | `/api/events` | SSE 实时推送 |
| POST | `/api/dispatch` | 派单 `{type,need}`（需**管理员**） |
| POST | `/api/inc` `/api/dec` | 账号 +1 / −1（需**管理员**） |
| POST | `/api/account` `/api/task` | 新增账号 / 任务（需**管理员**） |
| POST | `/api/reassign` | 改绑任务（需**管理员**） |
| POST | `/api/reset` | 清零今日计数（需**管理员**） |
| DELETE | `/api/account/:id` | 删除账号（需**管理员**） |
