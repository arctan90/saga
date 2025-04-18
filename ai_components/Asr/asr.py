# ASR语音转文字打标
from tqdm import tqdm
from utils import file_util
from funasr import AutoModel

import os
import traceback
import torch

# 这三个路径是模型
path_asr = 'ai_components/Asr/models/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch'
path_vad = 'ai_components/Asr/models/speech_fsmn_vad_zh-cn-16k-common-pytorch'
path_punc = 'ai_components/Asr/models/punc_ct-transformer_zh-cn-common-vocab272727-pytorch'

voice_device = None
if torch.cuda.is_available():
    voice_device = "cuda"
else:
    voice_device = "cpu"

model = AutoModel(
    model=path_asr,
    model_revision="v2.0.4",
    vad_model=path_vad,
    vad_model_revision="v2.0.4",
    punc_model=path_punc,
    punc_model_revision="v2.0.4",
    disable_update=True,  # 关闭检查更新
    device=voice_device,
)


class ASR:
    def __init__(self, input_wav_folder="./", output_folder="./", language="zh"):
        self.asr_model_name = '达摩 ASR (中文)'
        self.asr_model_scale = 'large'
        self.asr_language = language

        self.input_wav_folder = file_util.path_strip(input_wav_folder)
        self.output_folder = file_util.path_strip(output_folder)

    def open_asr(self):
        return _execute_asr(
            input_folder=self.input_wav_folder,
            language=self.asr_language,
        )

    def stop(self):
        return None

    def model_list(self):
        return [
            {
                'name': '达摩 ASR (中文)',
                'lang': ['zh'],
                'size': ['large'],
            },
            {
                'name': 'Faster Whisper (Multi language',
                'lang': ['auto', 'zh', 'en', 'ja'],
                'size': [
                    "tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en",
                    "large", "large-v1", "large-v2", "large-v3"],
            }
        ]


def _execute_asr(input_folder, language):
    input_file_names = os.listdir(input_folder)
    input_file_names.sort()

    output = {}

    for name in tqdm(input_file_names):
        try:
            text = model.generate(input="%s/%s" % (input_folder, name), language=language)[0]["text"]
            file_path = f"{input_folder}/{name}"
            output[file_path] = text
        except Exception as e:
            print(traceback.format_exc())
            raise RuntimeError(f"Failed to asr: {e}")

    return output
