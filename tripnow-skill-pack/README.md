# TripNow 旅行助手 · Cursor Skill 分发包

本压缩包（文件夹）内含 Cursor Agent Skill 说明、命令行脚本与接入文档，**不包含**任何其他产品源码。

---

## 包里有什么

| 内容 | 说明 |
|------|------|
| `tripnow-travel/` | Cursor Skill（含 `SKILL.md`、`reference.md`、`scripts/`） |
| `requirements.txt` | 运行脚本所需 Python 依赖（`httpx`） |
| `INTEGRATION.md` | **接入指南**：密钥、环境变量、脚本、HTTP 对接、Cursor 安装步骤 |

---

## 收件人快速开始

1. 解压到任意目录。
2. 阅读 [INTEGRATION.md](INTEGRATION.md)，完成 **API Key** 与 **环境变量** 配置。
3. 若使用 **Cursor**：将 `tripnow-travel` 文件夹复制到目标项目的 `.cursor/skills/tripnow-travel/`。
4. 可选：执行 `pip install -r requirements.txt` 后，按 `INTEGRATION.md` 运行验证脚本。

---

## 官方产品

TripNow 开放平台：<https://tripnowengine.133.cn/tripnow-ai-open-platform/#/>
