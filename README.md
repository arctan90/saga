# Saga 项目

## 项目简介
这是一个基于 Python 的语音处理项目，主要功能包括语音文件上传、语音分割和语音识别（ASR）等。

## 项目结构
```
.
├── ai_components/           # AI 组件目录
│   └── csm/                # 语音处理相关组件
│       ├── AudioSpliter/   # 音频分割组件
│       └── Asr/            # 语音识别组件
├── chat_function/          # 聊天功能模块
├── database/              # 数据库相关模块
├── router/               # 路由模块
│   └── csm.py           # 语音处理相关路由
├── utils/               # 工具函数模块
├── voices/             # 语音文件存储目录
├── main.py            # 主程序入口
├── project_base.py    # 项目基础配置
├── env_helper.py     # 环境变量助手
├── requirements.txt  # 项目依赖
└── .env            # 环境变量配置
```

## 主要功能模块

### 1. 语音处理模块 (router/csm.py)
- 语音文件上传接口 (`/csm/voice/update`)
  - 支持 WAV 格式音频文件上传
  - 自动生成带时间戳的文件名
  - 文件存储在 voices 目录
- 语音识别功能
  - 音频分割处理
  - ASR 语音识别
  - 自动清理临时文件

### 2. AI 组件 (ai_components/)
- AudioSpliter: 音频分割组件
- Asr: 语音识别组件

### 3. 工具模块 (utils/)
- 通用工具函数
- 路径处理工具

## 环境要求
- Python 3.x
- 依赖包列表见 requirements.txt

## 快速开始
1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量：复制 env_example 为 .env 并填写相应配置
4. 运行项目：`python main.py`

## API 接口说明

### 语音上传接口
- 端点：`/csm/voice/update`
- 方法：POST
- 参数：
  - voice: WAV 格式音频文件
  - uid: 用户标识
  - info: 附加信息
- 返回：
  - 成功：返回文件路径和状态信息
  - 失败：返回错误信息

## 开发指南
1. 代码规范遵循 PEP 8
2. 所有新功能需要添加相应的单元测试
3. 提交代码前请确保通过所有测试 

pip3 安装moshi需要运行  . "$HOME/.cargo/env" 

## 下载模型
[Damo ASR Model](https://modelscope.cn/models/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch/files)
```
modelscope download --model iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
mv $HOME/.cache/modelscope/hub/models/iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch ./ai_components/Asr/models/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
```
[Damo VAD Model](https://modelscope.cn/models/damo/speech_fsmn_vad_zh-cn-16k-common-pytorch/files)
```
modelscope download --model iic/speech_fsmn_vad_zh-cn-16k-common-pytorch
mv $HOME/.cache/modelscope/hub/models/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch ./ai_components/Asr/models/speech_fsmn_vad_zh-cn-16k-common-pytorch

```
[Damo Punc Model](https://modelscope.cn/models/damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch/files)

```
modelscope download --model iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch
mv $HOME/.cache/modelscope/hub/models/iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch ./ai_components/Asr/models/punc_ct-transformer_zh-cn-common-vocab272727-pytorch
```


