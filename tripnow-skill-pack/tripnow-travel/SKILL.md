---
name: tripnow-travel
description: >-
  Uses TripNow travel assistant for train/flight ticket search, real-time rail
  and flight status, and rail/aviation policy Q&A. Use when the user asks about
  火车票、机票、车次、航班、动态、学生票、退改签、行李规定, or needs help
  configuring TripNow API access and running the bundled call script.
---

# TripNow 旅行助手（Cursor Skill）

## 能力说明

在已配置 **TripNow API Key** 的前提下，通过本 Skill 目录内的脚本调用 TripNow 旅行助手，支持：

1. **票务查询**：出发地、目的地、日期；火车票或机票等自然语言查询。
2. **动态信息**：车次或航班号相关的状态类问题。
3. **出行政策与常识**：退改签、行李、证件核验等铁路/民航相关问答。

## 何时启用

- 用户需要**查询票务、列车/航班状态、出行政策**，且应使用 TripNow 官方能力而非凭空编造时刻表或规则。
- 用户需要**检查密钥是否生效**、**在终端验证接口**或**排查连接错误**。

## Agent 操作指引

1. **密钥**：确认用户已在环境中设置 `tripnow_api_key` 或 `TRIPNOW_API_KEY`（见 [reference.md](reference.md)）。可运行 `scripts/verify_tripnow_env.py` 做快速检查。
2. **发起查询**：在工作区根目录下，使用本 Skill 内的 `scripts/call_tripnow.py`，将用户问题作为 `-m` 参数传入。默认路径示例（若 Skill 安装在标准位置）：

   ```bash
   python .cursor/skills/tripnow-travel/scripts/call_tripnow.py -m "用户原话或整理后的查询"
   ```

   若项目中的 Skill 路径不同，请将命令中的路径改为实际的 `tripnow-travel/scripts/call_tripnow.py` 位置。
3. **多轮对话**：使用 `-j` 传入 JSON 数组形式的 `messages`，或 `-f` 指向包含 `messages` 数组的 JSON 文件（格式见 [reference.md](reference.md)）。
4. **自有系统集成**：需要 HTTP 对接时，把 [reference.md](reference.md) 中的接口地址、请求头与 JSON 体说明提供给开发者；不要臆造字段。

## 详细说明与接入

- 接口与环境变量：[reference.md](reference.md)
- 分发给使用者的步骤与接入第三方服务：解压包内 [INTEGRATION.md](../INTEGRATION.md)

## 官方入口

开放平台：<https://tripnowengine.133.cn/tripnow-ai-open-platform/#/>
