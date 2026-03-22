# TripNow 旅行助手 — 接口与配置参考

## 鉴权

任选其一：

| 方式 | 说明 |
|------|------|
| 环境变量 `tripnow_api_key` | 推荐在本地终端、CI、本 Skill 附带脚本中使用 |
| 环境变量 `TRIPNOW_API_KEY` | 与上一项等价，二选一即可 |

请求 HTTP 接口时，使用请求头：

```http
Authorization: Bearer <你的 API Key>
Content-Type: application/json
```

## 接口地址

- **Chat Completions（旅行助手对话）**  
  `POST https://tripnowengine.133.cn/tripnow/v1/chat/completions`

## 请求体（JSON）

```json
{
  "model": "tripnow-travel-pro",
  "messages": [
    { "role": "user", "content": "自然语言问题，例如：帮我查询明天北京到上海的火车票" }
  ],
  "stream": false
}
```

`messages` 支持多轮：按顺序追加 `user` / `assistant` 消息即可。

## 附带脚本

在已安装 `httpx` 且已设置环境变量后，于项目根目录（请按实际路径调整）：

```bash
python .cursor/skills/tripnow-travel/scripts/verify_tripnow_env.py
python .cursor/skills/tripnow-travel/scripts/call_tripnow.py -m "G123次列车现在到哪了"
python .cursor/skills/tripnow-travel/scripts/call_tripnow.py -j '[{"role":"user","content":"学生票核验需要什么证件"}]'
```

## 故障排查

| 现象 | 建议 |
|------|------|
| 提示未设置 Key | 检查当前 shell / 运行环境是否已 `export tripnow_api_key=...` |
| HTTP 4xx/5xx | 核对 Key 是否有效、本机网络能否访问上述域名 |
| 超时 | 适当增大 `call_tripnow.py` 的 `--timeout` 参数 |
