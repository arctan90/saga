import platform
import os
import ffmpeg
import traceback
import numpy as np
import json


def newest_file_in_folder(folder):
    # 获取文件夹中所有文件
    files = os.listdir(folder)
    # 排除文件夹，只保留文件
    files = [os.path.join(folder, file) for file in files if os.path.isfile(os.path.join(folder, file))]
    # 根据修改时间排序
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    # 返回生成时间最新的文件路径
    if files:
        return files[0]
    else:
        return None


def path_strip(path_str):
    if platform.system() == 'Windows':
        path_str = path_str.replace('/', '\\')
    return path_str.strip(" ").strip('"').strip("\n").strip('"').strip(" ")


def load_audio(file, sr):
    try:
        # https://github.com/openai/whisper/blob/main/whisper/audio.py#L26
        # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
        # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
        file = path_strip(file)  # 防止小白拷路径头尾带了空格和"和回车
        if not os.path.exists(file):
            raise RuntimeError(
                "You input a wrong audio path that does not exists, please fix it!"
            )
        out, _ = (
            ffmpeg.input(file, threads=0)
            .output("-", format="f32le", acodec="pcm_f32le", ac=1, ar=sr)
            .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
        )
    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Failed to load audio: {e}")

    return np.frombuffer(out, np.float32).flatten()


def get_hparams_from_file(config_path):
    with open(config_path, "r") as f:
        data = f.read()
    config = json.loads(data)

    hparams = HParams(**config)
    return hparams


class HParams:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if type(v) == dict:
                v = HParams(**v)
            self[k] = v

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def values(self):
        return self.__dict__.values()

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return self.__dict__.__repr__()
