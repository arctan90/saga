from typing import Dict, Any

# OpenAI API配置
DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 1.0
DEFAULT_PRESENCE_PENALTY = 0.0
DEFAULT_FREQUENCY_PENALTY = 0.0
DEFAULT_MAX_CONTEXT = 4096

# 角色配置
DEFAULT_SYSTEM_PROMPT = "Write {char}'s next reply in a fictional chat between {char} and {user}."

# 消息格式化配置
CHARACTER_NAMES_BEHAVIOR = {
    "NONE": "none",
    "DEFAULT": "default",
    "CONTENT": "content",
    "COMPLETION": "completion"
}

# 默认设置
DEFAULT_SETTINGS: Dict[str, Any] = {
    "model": DEFAULT_MODEL,
    "max_tokens": DEFAULT_MAX_TOKENS,
    "temperature": DEFAULT_TEMPERATURE,
    "top_p": DEFAULT_TOP_P,
    "presence_penalty": DEFAULT_PRESENCE_PENALTY,
    "frequency_penalty": DEFAULT_FREQUENCY_PENALTY,
    "max_context": DEFAULT_MAX_CONTEXT,
    "names_behavior": CHARACTER_NAMES_BEHAVIOR["DEFAULT"],
    "system_prompt": DEFAULT_SYSTEM_PROMPT
}

# 令牌预算设置
TOKEN_BUDGET_SETTINGS = {
    "DEFAULT_MAX_CONTEXT": 4096,
    "DEFAULT_MAX_RESPONSE": 500,
}