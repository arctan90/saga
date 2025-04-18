# 语料分离器
import threading

from utils import file_util
import os
import traceback
from ai_components.AudioSpliter.slicer import Slicer
import numpy as np
from scipy.io import wavfile


class Splitter:
    def __init__(self, input_path="./", output_path="./out"):
        # volume_threshold: 音量小于这个值视作静音的备选切割点
        self.volume_threshold = -34
        # hop_size: 怎么算音量曲线，越小精度越大计算量越高（不是精度越大效果越好）
        self.hop_size = 10
        # split_interval: 最短切割间隔
        self.min_split_interval = 300
        # split_interval 每段最小多长，如果第一段太短一直和后面段连起来直到超过这个值，单位毫秒
        # max_sil_kept: 切完后静音最多留多长, 单位毫秒
        self.max_sil_kept = 500
        # min_length: 每段最小多长，如果第一段太短一直和后面段连起来直到超过这个值
        self.min_length = 4000
        self.input_path = file_util.path_strip(input_path)
        self.output_path = file_util.path_strip(output_path)

        # 音频归一化后最大值
        self._max = 0.9
        # 混多少比例归一化后音频进来
        self.alpha_mix = 0.25

        # 处理进程列表，用于join
        self.thread_list = []

        self.exit_event = threading.Event()

    def begin_slice(self):
        if not os.path.exists(self.input_path):
            return "输入路径不存在"

        os.makedirs(self.output_path, exist_ok=True)

        input_files = []  # 待处理的文件列表
        if os.path.isfile(self.input_path):
            input_files = [self.input_path]
        elif os.path.isdir(self.input_path):
            input_files = [os.path.join(self.input_path, name) for name in sorted(list(os.listdir(self.input_path)))]

        for one_file in input_files:
            t = threading.Thread(target=self._split_wav_file, args=(one_file,))
            t.start()
            self.thread_list.append(t)

        for t in self.thread_list:
            t.join()
        return None

    def close_slice(self):
        self.exit_event.set()
        for t in self.thread_list:
            if t.is_alive():
                t.join()

    def _split_wav_file(self, file):
        slicer = Slicer(
            sr=32000,  # 长音频采样率
            threshold=int(self.volume_threshold),  # 音量小于这个值视作静音的备选切割点
            min_length=int(self.min_length),  # 每段最小多长，如果第一段太短一直和后面段连起来直到超过这个值
            min_interval=int(self.min_split_interval),  # 最短切割间隔
            hop_size=int(self.hop_size),  # 怎么算音量曲线，越小精度越大计算量越高（不是精度越大效果越好）
            max_sil_kept=int(self.max_sil_kept),  # 切完后静音最多留多长
        )
        self._max = float(self._max)
        self.alpha_mix = float(self.alpha_mix)

        try:
            name = os.path.basename(file)
            audio = file_util.load_audio(file, 32000)

            for chunk, start, end in slicer.slice(audio):  # start和end是帧数
                tmp_max = np.abs(chunk).max()
                if tmp_max > 1:
                    chunk /= tmp_max
                chunk = (chunk / tmp_max * (self._max * self.alpha_mix)) + (1 - self.alpha_mix) * chunk
                wavfile.write(
                    "%s/%s_%010d_%010d.wav" % (self.output_path, name, start, end),
                    32000,
                    # chunk.astype(np.float32),
                    (chunk * 32767).astype(np.int16),
                )
            # print(file, " Done")
        except Exception as e:
            print(file, "->fail->", traceback.format_exc())
            raise RuntimeError(f"Failed to split audio: {e}")
