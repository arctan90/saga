from fastapi import Header, HTTPException

import os

current_directory = os.path.dirname(os.path.abspath(__file__))

need_authenticate = False

from env_helper import EnvHelper

SAGA_VERSION = EnvHelper.get_env_value('SAGA_VERSION')


async def authenticate_api(saga_version: str = Header(...)):
    if saga_version != SAGA_VERSION:
        # todo 打印日志，记录攻击
        raise HTTPException(status_code=403, detail="Invalid api version")
    return True


async def authenticate_web_chatgpt_api(mc: str = Header(...)):
    if mc != SAGA_VERSION:
        # todo 打印日志，记录攻击
        raise HTTPException(status_code=403, detail="Invalid api version")
    return True
