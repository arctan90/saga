import random
import base64
from typing import List, Dict, Any

# 常量定义
PROMPT_PLACEHOLDER = "Let's get started."  # 这里应该从配置中获取


class PromptNames:
    """表示提示名称的对象"""

    def __init__(self, char_name: str = "", user_name: str = "", group_names: List[str] = None):
        self.char_name = char_name
        self.user_name = user_name
        self.group_names = group_names or []

    def starts_with_group_name(self, message: str) -> bool:
        """检查消息是否以组名开头"""
        return any(message.startswith(f"{name}: ") for name in self.group_names)


def get_prompt_names(request) -> PromptNames:
    """
    从请求中提取角色名称、用户名称和组成员名称

    Args:
        request: 请求对象

    Returns:
        PromptNames: 包含名称信息的对象
    """
    return PromptNames(
        char_name=str(request.body.get('char_name', '')),
        user_name=str(request.body.get('user_name', '')),
        group_names=[str(name) for name in request.body.get('group_names', [])]
    )


def post_process_prompt(messages: List[Dict[str, Any]], in_type: str, names: PromptNames) -> List[Dict[str, Any]]:
    """
    对生成的消息应用后处理步骤

    Args:
        messages: 要后处理的消息列表
        in_type: 提示转换类型
        names: 提示名称对象

    Returns:
        处理后的消息列表
    """
    if in_type in ['merge', 'claude']:
        return merge_messages(messages, names, False, False)
    elif in_type == 'semi':
        return merge_messages(messages, names, True, False)
    elif in_type == 'strict':
        return merge_messages(messages, names, True, True)
    elif in_type == 'deepseek':
        # 使用lambda函数处理deepseek特殊情况
        processed = merge_messages(messages, names, True, False)
        if processed and (processed[-1]['role'] != 'assistant' or processed[-1].get('prefix', False)):
            return processed
        return processed
    else:
        return messages


def merge_messages(messages: List[Dict[str, Any]], names: PromptNames, strict: bool, placeholders: bool) -> List[
    Dict[str, Any]]:
    """
    合并具有相同连续角色的消息，如果存在则删除名称

    Args:
        messages: 要合并的消息
        names: 提示名称对象
        strict: 启用严格模式：只允许开头有一个系统消息，强制用户第一条消息
        placeholders: 在严格模式下向消息添加用户占位符

    Returns:
        合并后的消息列表
    """
    merged_messages = []
    content_tokens = {}  # 用于存储内容令牌

    # 从消息中删除名称
    for message in messages:
        if 'content' not in message:
            message['content'] = ''

        # 展平内容并用随机令牌替换图片URL
        if isinstance(message['content'], list):
            text_parts = []
            for content in message['content']:
                if content['type'] == 'text':
                    text_parts.append(content['text'])
                elif content['type'] == 'image_url':
                    # 生成随机令牌
                    token = base64.b64encode(random.randbytes(32)).decode('utf-8')
                    content_tokens[token] = content
                    text_parts.append(token)
                else:
                    text_parts.append('')
            message['content'] = '\n\n'.join(text_parts)

        # 处理角色名称
        if message['role'] == 'system' and message.get('name') == 'example_assistant':
            if names.char_name and not message['content'].startswith(
                    f"{names.char_name}: ") and not names.starts_with_group_name(message['content']):
                message['content'] = f"{names.char_name}: {message['content']}"

        if message['role'] == 'system' and message.get('name') == 'example_user':
            if names.user_name and not message['content'].startswith(f"{names.user_name}: "):
                message['content'] = f"{names.user_name}: {message['content']}"

        if message.get('name') and message['role'] != 'system':
            if not message['content'].startswith(f"{message['name']}: "):
                message['content'] = f"{message['name']}: {message['content']}"

        if message['role'] == 'tool':
            message['role'] = 'user'

        # 删除不需要的字段
        if 'name' in message:
            del message['name']
        if 'tool_calls' in message:
            del message['tool_calls']
        if 'tool_call_id' in message:
            del message['tool_call_id']

    # 合并具有相同角色的连续消息
    for message in messages:
        if merged_messages and merged_messages[-1]['role'] == message['role'] and message['content']:
            merged_messages[-1]['content'] += '\n\n' + message['content']
        else:
            merged_messages.append(message)

    # 防止合并后的消息数组为空
    if not merged_messages:
        merged_messages.insert(0, {
            'role': 'user',
            'content': PROMPT_PLACEHOLDER
        })

    # 检查内容令牌并用实际内容对象替换它们
    if content_tokens:
        for message in merged_messages:
            has_valid_token = any(token in message['content'] for token in content_tokens.keys())

            if has_valid_token:
                split_content = message['content'].split('\n\n')
                merged_content = []

                for content in split_content:
                    if content in content_tokens:
                        merged_content.append(content_tokens[content])
                    else:
                        if merged_content and merged_content[-1]['type'] == 'text':
                            merged_content[-1]['text'] += f"\n\n{content}"
                        else:
                            merged_content.append({'type': 'text', 'text': content})

                message['content'] = merged_content

    # 处理严格模式
    if strict:
        for i in range(len(merged_messages)):
            # 强制将中间提示的系统消息转换为用户消息
            if i > 0 and merged_messages[i]['role'] == 'system':
                merged_messages[i]['role'] = 'user'

        if merged_messages and placeholders:
            if merged_messages[0]['role'] == 'system' and (
                    len(merged_messages) == 1 or merged_messages[1]['role'] != 'user'):
                merged_messages.insert(1, {'role': 'user', 'content': PROMPT_PLACEHOLDER})
            elif merged_messages[0]['role'] != 'system' and merged_messages[0]['role'] != 'user':
                merged_messages.insert(0, {'role': 'user', 'content': PROMPT_PLACEHOLDER})

        return merge_messages(merged_messages, names, False, placeholders)

    return merged_messages
