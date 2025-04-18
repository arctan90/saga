from fastapi import APIRouter, File, Form, UploadFile, Depends
from fastapi.responses import JSONResponse
from project_base import authenticate_api
import os
import logging
from datetime import datetime
import platform
from ai_components.AudioSpliter.spliter import Splitter
from ai_components.Asr.asr import ASR
from utils.session import generate_session_id

router = APIRouter()

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)


@router.post('/csm/voice/update')
async def upload_ref_voice(voice: UploadFile = File(...), uid: str = Form(...), info: str = Form(...),
                           authenticated: bool = Depends(authenticate_api)):
    try:
        # 生成文件名：时间戳_原始文件名
        if voice.content_type != "audio/x-wav" and voice.content_type != "audio/wave" and voice.content_type != "audio/wav":
            return JSONResponse(status_code=403, content=f"Only WAV files are allowed. Error in file: {voice.filename}")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = voice.filename
        new_filename = f"{timestamp}_{original_filename}"

        session_id = generate_session_id()

        # 确保 voices 目录存在
        os.makedirs('voices', exist_ok=True)

        # 构建完整的文件路径
        file_path = os.path.join('voices', new_filename)

        # 读取并保存文件
        voice_content = await voice.read()
        with open(file_path, 'wb') as f:
            f.write(voice_content)

        # 解析抽取成token， 这是一个key-value的json对象，key是语音文件路径，value是对应文本
        annotation_info = asr_voice(file_path, uid, session_id=session_id)
         # todo 调用本地的python服务，完成解析


        return JSONResponse(content={
            'status': 'success',
            'message': 'upload success',
            'split_info': annotation_info,
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'message': f'upload failed: {str(e)}'
            }
        )


def _path_strip(path_str):
    if platform.system() == 'Windows':
        path_str = path_str.replace('/', '\\')
    return path_str.strip(" ").strip('"').strip("\n").strip('"').strip(" ")


def asr_voice(wav_file, uid, session_id):
    wav_split_folder = _path_strip("%s/asr_result/%s/%s/wav_split" % (PROJECT_ROOT, uid, session_id))

    # 确保 wav_split 文件夹存在
    os.makedirs(wav_split_folder, exist_ok=True)

    splitter = Splitter(wav_file, wav_split_folder)
    ret = splitter.begin_slice()
    if ret is not None:
        logger.warning(ret)
        raise Exception('analysis voice failed.')

    asr_out_folder = _path_strip("%s/asr_result/%s/%s/asr_out" % (PROJECT_ROOT, uid, session_id))
    # 确保 asr_out 文件夹存在
    os.makedirs(asr_out_folder, exist_ok=True)

    # step 2 asr分离出语料pairs
    asr = ASR(wav_split_folder, asr_out_folder, language='en')
    annotation_info = asr.open_asr()

    # 删除临时文件夹
    try:
        if os.path.exists(wav_file):
            os.remove(wav_file)
        # if os.path.exists(wav_split_folder):
        #     shutil.rmtree(wav_split_folder)

    except Exception as e:
        logger.warning(f"删除临时文件夹失败: {str(e)}")

    return annotation_info
