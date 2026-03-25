import json
from typing import Type, Any, List, Optional

import httpx
import uvicorn
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import CallToolResult, TextContent
from pydantic import Field
from starlette.routing import Host

from models import ChatCompletionResponse, ErrorResponse, Message

# 创建MCP服务器实例
mcp = FastMCP(
    name="tripnow_mcp",
    instructions="MCP Server 航班管家 - 一站式航铁票务查询 实时动态智能追踪。覆盖机票、火车票实时查询，航铁动态精准追踪，内置铁路航空领域知识库，解答出行高频问题，为MCP广场用户提供一站式出行信息服务。",
    stateless_http=True,
    port=8000,
    host="0.0.0.0"
)

"""
TripNow 上游 API 鉴权：仅接受 MCP 入站 HTTP 请求头
Authorization: Bearer <API_KEY>（不再读取环境变量或 .env）
"""
tripnow_api_url = "https://tripnowengine.133.cn/tripnow/v1/chat/completions"


@mcp.tool(
    name="chat_completions", 
    description="调用TripNow旅行助手API，提供航铁票务实时查询、航铁动态精准追踪、航铁知识智能问答三大功能。支持机票、火车票实时查询，列车、航班动态追踪，以及铁路航空领域知识问答。"
)
async def chat_completions(ctx: Context,
                          messages: List[dict] = Field(description="消息列表，每个消息包含role和content字段。支持三种主要功能：1) 航铁票务实时查询（例如：'帮我查询明天北京到上海的火车票'）；2) 航铁动态精准追踪（例如：'帮我看看G123次列车现在到哪了'）；3) 航铁知识智能问答（例如：'学生票每年能买几次，要什么证件核验'）。"),) -> CallToolResult:
    """
    调用TripNow旅行助手API，提供以下三大功能：
    
    1. 航铁票务实时查询：支持机票、火车票实时查询，根据出发地、目的地、出行日期，快速返回对应航班/车次核心信息
    2. 航铁动态精准追踪：支持列车、航班动态实时查询，返回列车位置、检票口等信息及航班起降、登机口等状态
    3. 航铁知识智能问答：内置铁路、航空领域知识库，针对票务政策、退改签、行李规定等高频问题，快速给出精准、规范的解答
    
    Args:
        messages: 消息列表，支持多轮对话。每个消息应包含：
            - role: 消息角色，如 'user', 'assistant'
            - content: 消息内容（自然语言查询）
    """
    tripnow_api_key = get_api_key(ctx)
    # response_format = get_response_format(ctx)

    # 验证并转换消息格式
    formatted_messages = []
    for msg in messages:
        if isinstance(msg, dict):
            formatted_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        elif isinstance(msg, Message):
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        else:
            # 兼容旧格式：如果传入的是字符串，转换为用户消息
            formatted_messages.append({
                "role": "user",
                "content": str(msg)
            })

    # 构建请求体
    payload = {
        "model": "tripnow-travel-pro",
        "messages": formatted_messages,
        "stream": False
    }

    # 构建请求头
    headers = {
        "Authorization": f"Bearer {tripnow_api_key}",
        "Content-Type": "application/json"
    }

    # 发送POST请求
    response = await http_post(tripnow_api_url, headers=headers, json_data=payload)
    return handle_json_response(response, response_format="text", model_class=ChatCompletionResponse)


def _get_request_headers(ctx: Context):
    try:
        request_context = getattr(ctx, "request_context", None)
        if request_context:
            request = getattr(request_context, "request", None)
            if request:
                h = getattr(request, "headers", None)
                if h is not None:
                    return h
        request = getattr(ctx, "request", None)
        if request:
            h = getattr(request, "headers", None)
            if h is not None:
                return h
        h = getattr(ctx, "headers", None)
        if h is not None:
            return h
    except Exception:
        pass
    return None


def _bearer_token_from_authorization(auth: str) -> Optional[str]:
    if not auth or not str(auth).strip():
        return None
    auth = str(auth).strip()
    lower = auth.lower()
    if lower.startswith("bearer "):
        token = auth[7:].strip()
        return token or None
    return None


def get_api_key(ctx: Context) -> str:
    """
    仅从入站请求的 Authorization 头获取 TripNow API Key：
    Authorization: Bearer <API_KEY>
    """
    headers = _get_request_headers(ctx)
    if not headers or not hasattr(headers, "get"):
        raise Exception(
            'error: missing request headers; set "Authorization: Bearer <API_KEY>" on the MCP HTTP request'
        )
    auth = headers.get("authorization")
    tripnow_api_key = _bearer_token_from_authorization(auth) if auth else None
    if not tripnow_api_key:
        raise Exception(
            'error: missing or invalid Authorization header; expected "Authorization: Bearer <API_KEY>"'
        )
    return tripnow_api_key


def get_response_format(ctx: Context) -> str:
    """
    从header中获取数据返回格式类型
    """
    # 安全地获取 headers
    response_format = None
    try:
        request_context = getattr(ctx, 'request_context', None)
        if request_context:
            request = getattr(request_context, 'request', None)
            if request:
                headers = getattr(request, 'headers', None)
                if headers:
                    response_format = (headers.get("responseFormat")
                                      or headers.get("ResponseFormat")
                                      or headers.get("response_format"))
    except Exception:
        # 如果访问 request_context 出错，使用默认值
        pass
    
    if not response_format:
        return 'markdown'
    return response_format


async def http_post(url: str,
                   headers: dict,
                   json_data: dict) -> str:
    """
    发送HTTP POST请求
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=json_data, timeout=30.0)
            # 如果状态码不是 2xx，尝试获取错误详情
            if not response.is_success:
                error_detail = f"Status {response.status_code}"
                try:
                    error_body = response.text
                    if error_body:
                        error_detail += f": {error_body[:500]}"  # 限制错误信息长度
                except:
                    pass
                raise httpx.HTTPStatusError(
                    message=f"HTTP {response.status_code} {error_detail}",
                    request=response.request,
                    response=response
                )
            return response.text
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP request failed: {e.response.status_code} {e.response.reason_phrase}"
        try:
            error_body = e.response.text
            if error_body:
                error_msg += f"\n响应内容: {error_body[:500]}"
        except:
            pass
        raise Exception(error_msg) from e
    except httpx.HTTPError as e:
        raise Exception(f"HTTP request failed: {str(e)}") from e
    except KeyError as e:
        raise Exception(f"Failed to parse response: {str(e)}") from e


def handle_json_response(
        response: str,
        response_format: str,
        model_class: Type[Any], ) -> CallToolResult:
    """
    通用 JSON 响应处理器，用于：
    - 解析 JSON 字符串
    - 实例化 Pydantic 模型
    - 调用 .markdown() 方法生成 Markdown
    - 返回标准化的 CallToolResult

    :param response: 原始 API 返回的字符串（JSON 格式）
    :param response_format: 响应格式，可选 "json" 或 "markdown"
    :param model_class: Pydantic 模型类，如 ChatCompletionResponse
    :return: CallToolResult
    """
    if response_format == "json":
        json_response = json.loads(response)
        # 实例化模型
        try:
            vo_instance = model_class(**json_response)
        except Exception as e:
            vo_instance = ErrorResponse(**json_response)
        # 生成 Markdown（要求模型有 .markdown() 方法）
        markdown_text = vo_instance.markdown()
        return CallToolResult(
            content=[TextContent(type="text", text=markdown_text)],
            structuredContent=json_response,
            isError=False,
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=response)],
            isError=False,
        )


if __name__ == "__main__":
    # Streamable HTTP 模式
    # mcp.run(transport="streamable-http")
    # STDIO 模式（标准输入输出）
    mcp.run()
