import os
from typing import Optional


class EnvHelper:
    @staticmethod
    def get_env_value(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        动态读取.env文件中的配置值
        :param key: 配置键名
        :param default: 默认值
        :return: 配置值或默认值
        """
        # 获取当前工作目录（即项目根目录）下的 .env 文件
        env_path = os.path.join(os.getcwd(), '.env')
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            k, v = line.split('=', 1)
                            if k.strip() == key:
                                return v.strip()
                        except ValueError:
                            continue
        except FileNotFoundError:
            print(f"警告: 未找到.env文件在路径 {env_path}")
        except Exception as e:
            print(f"读取.env文件时发生错误: {str(e)}")
            
        return default
