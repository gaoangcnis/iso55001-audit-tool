import yaml
import os
import logging
import traceback
from functools import wraps

# 自定义异常类
class AppError(Exception):
    """应用程序基础异常类"""
    pass

class ConfigError(AppError):
    """配置加载和处理相关异常"""
    pass

# 异常处理装饰器
def handle_errors(default_return_value=None, error_type=AppError):
    """统一异常处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"函数 {func.__name__} 执行失败: {str(e)}")
                logging.error(traceback.format_exc())
                if default_return_value is not None:
                    return default_return_value
                raise error_type(str(e)) from e
        return wrapper
    return decorator

# 配置文件目录常量
CONFIG_DIR = 'config'  # 存放所有YAML配置文件的目录

@handle_errors(default_return_value={}, error_type=ConfigError)
def load_yaml(filename):
    """加载YAML配置文件
    
    从配置文件目录加载指定的YAML文件，并返回解析后的Python对象。
    
    参数:
        filename (str): YAML配置文件的名称（不带路径）
        
    返回:
        dict: 解析后的YAML配置内容
        None: 如果文件不存在或解析失败
    """
    path = os.path.join(CONFIG_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class Config:
    """配置管理类
    
    统一加载和管理应用程序的所有配置文件，提供集中式的配置访问接口。
    
    属性:
        score_weights (dict): 分值权重配置，包含章节权重、问题权重和问题类型基础分值
        lang_zh (dict): 中文语言配置，包含界面文本和提示信息的中文翻译
        lang_en (dict): 英文语言配置，包含界面文本和提示信息的英文翻译
        general (dict): 通用配置，包含应用程序的基本设置
    """
    def __init__(self):
        self.score_weights = load_yaml('score_weights.yaml')  # 加载分值权重配置
        self.lang_zh = load_yaml('lang_zh.yaml')  # 加载中文语言配置
        self.lang_en = load_yaml('lang_en.yaml')  # 加载英文语言配置
        self.general = load_yaml('config.yaml')  # 加载通用配置

# 全局配置实例，供应用程序其他模块直接使用
config = Config() 