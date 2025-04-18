import json
import asyncio
import logging
from typing import Dict, List, Any, Union
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from env_helper import EnvHelper
from .config import *

API_DEEPSEEK = 'https://api.deepseek.com/'
logger = logging.getLogger(__name__)

# 文本完成模型列表
TEXT_COMPLETION_MODELS = [
    # 在这里添加文本完成模型的列表
    'gpt-3.5-turbo-instruct',
    'gpt-3.5-turbo-instruct-0914',
    'text-davinci-003',
    'text-davinci-002',
    'text-davinci-001',
    'text-curie-001',
    'text-babbage-001',
    'text-ada-001',
    'code-davinci-002',
    'code-davinci-001',
    'code-cushman-002',
    'code-cushman-001',
    'text-davinci-edit-001',
    'code-davinci-edit-001',
    'text-embedding-ada-002',
    'text-similarity-davinci-001',
    'text-similarity-curie-001',
    'text-similarity-babbage-001',
    'text-similarity-ada-001',
    'text-search-davinci-doc-001',
    'text-search-curie-doc-001',
    'text-search-babbage-doc-001',
    'text-search-ada-doc-001',
    'code-search-babbage-code-001',
    'code-search-ada-code-001',
]


async def send_deepseek_request(request_data: Dict[str, Any], cancel_event: asyncio.Event):
    """
    发送请求到Deepseek API
    """
    api_url = API_DEEPSEEK
    api_key = EnvHelper.get_env_value('API_KEY')

    if not api_key and not request_data.get('reverse_proxy'):
        logger.error('Deepseek API key is missing.')
        return JSONResponse(status_code=400, content={"error": True})

    # 初始化请求参数
    headers = {}
    body_params = {}

    # 判断是否为文本补全请求
    is_text_completion = bool(
        request_data.get('model') and request_data['model'] in TEXT_COMPLETION_MODELS) or isinstance(
        request_data.get('messages'), str)

    # 根据is_text_completion的值决定是否转换文本补全提示
    text_prompt = convert_text_completion_prompt(request_data['messages']) if is_text_completion else ''
    # 如果不是文本补全请求，并且请求中包含工具数组且不为空
    if not is_text_completion and isinstance(request_data.get('tools'), list) and len(
            request_data.get('tools', [])) > 0:
        body_params['tools'] = request_data['tools']
        body_params['tool_choice'] = request_data.get('tool_choice')

    # 处理logprobs参数
    if request_data.get('logprobs', 0) > 0:
        body_params['top_logprobs'] = request_data['logprobs']
        body_params['logprobs'] = True

    # 处理消息
    messages = post_process_prompt(
        request_data['messages'],
        'deepseek',
        get_prompt_names(request_data)
    )

    # 添加自定义停止序列
    if isinstance(request_data.get('stop'), list) and len(request_data['stop']) > 0:
        body_params['stop'] = request_data['stop']

    # 构建请求体
    request_body = {
        'messages': messages if not is_text_completion else None,
        # 如果是文本补全请求，则包含prompt字段
        'prompt': text_prompt if is_text_completion else None,
        'model': request_data['model'],
        'temperature': request_data.get('temperature', DEFAULT_TEMPERATURE),
        'max_tokens': request_data.get('max_tokens', DEFAULT_MAX_TOKENS),
        'max_completion_tokens': request_data.get('max_completion_tokens'),
        'stream': request_data.get('stream', False),
        'presence_penalty': request_data.get('presence_penalty', DEFAULT_PRESENCE_PENALTY),
        'frequency_penalty': request_data.get('frequency_penalty', DEFAULT_FREQUENCY_PENALTY),
        'top_p': request_data.get('top_p', 1),
        'top_k': request_data.get('top_k'),
        'stop': request_data.get('stop'),
        'logit_bias': request_data.get('logit_bias'),
        'seed': request_data.get('seed'),
        'n': request_data.get('n', 1),
        **body_params
    }

    logger.info(f"Deepseek request: {request_body}")

    # 发送请求
    return await make_request(
        api_url=api_url,
        api_key=api_key,
        request_body=request_body,
        cancel_event=cancel_event,
        stream=request_data.get('stream', False),
        headers=headers
    )


async def convert_text_completion_prompt(messages: Union[List[Dict[str, Any]], str]) -> str:
    """
    将消息数组转换为文本格式的提示

    Args:
        messages: 消息数组或字符串

    Returns:
        转换后的文本提示
    """
    # 如果messages是字符串，直接返回
    if isinstance(messages, str):
        return messages

    # 初始化消息字符串列表
    message_strings = []

    # 遍历消息数组
    for m in messages:
        # 系统消息且没有名称
        if m.get('role') == 'system' and m.get('name') is None:
            message_strings.append('System: ' + m.get('content', ''))
        # 系统消息且有名称
        elif m.get('role') == 'system' and m.get('name') is not None:
            message_strings.append(m.get('name') + ': ' + m.get('content', ''))
        # 其他类型的消息
        else:
            message_strings.append(m.get('role', '') + ': ' + m.get('content', ''))

    # 将所有消息连接起来，并在末尾添加assistant:
    return '\n'.join(message_strings) + '\nassistant:'


async def make_request(
        api_url: str,
        api_key: str,
        headers,
        request_body: Dict[str, Any],
        cancel_event: asyncio.Event,
        stream: bool = False,
        retries: int = 5,
        timeout: int = 5000

) -> Union[JSONResponse, StreamingResponse]:
    """
    向API端点发送请求
    """
    try:
        # 检查是否已取消
        if cancel_event.is_set():
            logger.info('Request cancelled by client')
            return JSONResponse(status_code=499, content={"error": {"message": "Request cancelled by client"}})

        # 使用httpx发送异步请求
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(
                f"{api_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    **headers
                },
                json=request_body
            )

            # 检查是否已取消
            if cancel_event.is_set():
                logger.info('Request cancelled by client after response received')
                return JSONResponse(status_code=499, content={"error": {"message": "Request cancelled by client"}})

            # 处理流式响应
            if stream:
                logger.info('Streaming request in progress')

                # 创建异步生成器
                async def stream_response():
                    async for chunk in response.aiter_bytes():
                        # 检查是否已取消
                        if cancel_event.is_set():
                            logger.info('Request cancelled during streaming')
                            break
                        yield chunk

                # 返回StreamingResponse
                return StreamingResponse(
                    stream_response(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )

            # 处理非流式响应
            if response.status_code == 200:
                json_data = response.json()
                logger.info(f"Deepseek response: {json_data}")
                return JSONResponse(content=json_data)
            elif response.status_code == 429 and retries > 0:
                logger.info(f"Out of quota, retrying in {round(timeout / 1000)}s")

                # 等待重试，但检查取消事件
                for _ in range(int(timeout / 100)):
                    if cancel_event.is_set():
                        logger.info('Request cancelled by client during retry')
                        return JSONResponse(status_code=499,
                                            content={"error": {"message": "Request cancelled by client"}})
                    await asyncio.sleep(0.1)

                # 递归重试
                return await make_request(
                    api_url=api_url,
                    api_key=api_key,
                    request_body=request_body,
                    cancel_event=cancel_event,
                    stream=stream,
                    retries=retries - 1,
                    timeout=timeout * 2, headers=headers)
            else:
                # 处理错误响应
                error_text = response.text
                error_data = json.loads(error_text) if error_text else {}

                message = response.reason_phrase or 'Unknown error occurred'
                quota_error = response.status_code == 429 and error_data.get('error', {}).get(
                    'type') == 'insufficient_quota'

                logger.error(f'Chat completion request error: {message} {error_text}')

                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": {"message": message}, "quota_error": quota_error}
                )

    except httpx.ConnectError as error:
        # 处理连接错误
        logger.error('Connection error', exc_info=error)
        message = f"Connection refused: {str(error)}"

        return JSONResponse(status_code=502, content={"error": {"message": message}})
    except Exception as error:
        # 处理其他错误
        logger.error('Generation failed', exc_info=error)
        message = str(error) or 'Unknown error occurred'

        return JSONResponse(status_code=502, content={"error": {"message": message}})


# 辅助函数
def post_process_prompt(messages: List[Dict[str, Any]], in_type: str, names: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    对生成的消息应用后处理步骤
    """
    if in_type == 'deepseek':
        return merge_messages(messages, names, True, False)
    elif in_type == 'merge':
        return merge_messages(messages, names, False, False)
    elif in_type == 'semi':
        return merge_messages(messages, names, True, False)
    elif in_type == 'strict':
        return merge_messages(messages, names, True, True)
    else:
        return messages


def merge_messages(messages: List[Dict[str, Any]], names: Dict[str, str],
                   strict: bool = False, strict_system: bool = False) -> List[Dict[str, Any]]:
    """
    合并消息，处理系统提示和用户/助手消息
    """
    result = []
    for msg in messages:
        if msg.get('role') == 'system':
            if strict_system:
                pass
            result.append(msg)
        elif msg.get('role') in ['user', 'assistant']:
            result.append(msg)
    return result


def get_prompt_names(request_data: Dict[str, Any]) -> Dict[str, str]:
    """
    获取提示名称
    """
    return {
        'system': request_data.get('system_name', 'system'),
        'user': request_data.get('user_name', 'user'),
        'assistant': request_data.get('assistant_name', 'assistant')
    }
