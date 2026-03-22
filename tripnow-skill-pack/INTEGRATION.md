# TripNow 旅行助手 — 接入说明

本文说明如何将 **TripNow 官方旅行助手服务**接入到你的环境：本地终端、自有后端、以及 Cursor 编辑器中的 Agent Skill。

---

## 1. 获取 API Key

在 TripNow 开放平台申请并开通服务，获取专属 **API Key**。  
开放平台：<https://tripnowengine.133.cn/tripnow-ai-open-platform/#/>

请妥善保管 Key，不要提交到公开仓库。

---

## 2. 环境变量（推荐）

在运行脚本或启动你的应用前设置：

```bash
export tripnow_api_key="你的API_KEY"
```

部分环境也支持名称 `TRIPNOW_API_KEY`，二者选其一即可。

在桌面会话中可将上述行写入 shell 配置文件（如 `~/.zshrc`），或在 IDE「运行配置」里为子进程注入同名环境变量。

---

## 3. 使用本包内的 Python 脚本

本包 `requirements.txt` 仅依赖 `httpx`。安装：

```bash
cd /path/to/tripnow-skill-pack
pip install -r requirements.txt
```

验证 Key 是否已被当前环境识别：

```bash
python tripnow-travel/scripts/verify_tripnow_env.py
```

发起一次对话请求（将路径换为你解压后的实际目录）：

```bash
python tripnow-travel/scripts/call_tripnow.py -m "帮我查询明天北京到上海的火车票"
```

多轮或复杂 `messages` 见 `tripnow-travel/reference.md`。

---

## 4. 接入自有服务（HTTP 直连）

若你在后端、网关或定时任务中直接调用 TripNow，请使用：

- **方法**：`POST`
- **URL**：`https://tripnowengine.133.cn/tripnow/v1/chat/completions`
- **请求头**：`Authorization: Bearer <API Key>`，`Content-Type: application/json`
- **请求体**：见 `tripnow-travel/reference.md` 中的 JSON 示例

响应为 JSON 文本，请按业务需要解析 `choices` 等字段展示给用户。

---

## 5. 在 Cursor 中使用本 Skill

1. 将整个文件夹 `tripnow-travel` 复制到你的项目下的：  
   **`<项目根>/.cursor/skills/tripnow-travel/`**  
   （若 `.cursor/skills` 不存在，请自行创建。）
2. 用 Cursor 打开该项目，Agent 会自动加载该 Skill。
3. 在终端或 Cursor 集成的终端里为当前工作区配置 `tripnow_api_key`，以便执行 `tripnow-travel/scripts/` 下的脚本。

Skill 主文件为 `tripnow-travel/SKILL.md`，其中说明了 Agent 应在何时协助用户调用 TripNow。

---

## 6. 常见问题

**Q：脚本提示找不到 Key？**  
确认在同一终端会话中已 `export`，或在该终端启动 Cursor/子进程时能继承到该变量。

**Q：能否改名 `tripnow-travel` 文件夹？**  
可以，但请同步修改文档与命令中的路径；Skill 的 `name` 字段在 `SKILL.md`  frontmatter 中，一般保持 `tripnow-travel` 便于识别。

**Q：官方接口或域名变更怎么办？**  
以 TripNow 开放平台当前文档为准，并相应更新 `tripnow-travel/scripts/call_tripnow.py` 中的 `TRIPNOW_API_URL`（如有需要）。
