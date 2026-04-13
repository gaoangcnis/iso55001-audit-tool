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

"""
配置验证工具

用于验证ISO55001评估系统的配置文件是否符合规范，确保系统正常运行。

验证内容:
    - 多语言配置文件(lang_zh.yaml, lang_en.yaml)的完整性
    - 分值权重配置文件(score_weights.yaml)的结构完整性

使用方法:
    python config_validator.py

验证逻辑:
    1. 加载需要验证的配置文件
    2. 检查多语言配置是否包含所有必要的键
    3. 检查分值权重配置是否包含所有必要的结构
    4. 输出验证结果
"""

@handle_errors(error_type=ConfigError)
def validate_lang_config(lang_config, required_keys, lang_name):
    """验证多语言配置文件的完整性
    
    检查指定的多语言配置文件是否包含所有必要的键，确保界面文本显示正常。
    
    参数:
        lang_config (dict): 多语言配置内容
        required_keys (list): 必须包含的键列表
        lang_name (str): 配置文件名称(用于错误信息)
        
    异常:
        ValueError: 如果缺少必要的键，抛出包含缺失键列表的异常
    """
    missing = [k for k in required_keys if k not in lang_config]
    if missing:
        raise ValueError(f"{lang_name} 缺少以下多语言键: {missing}")

@handle_errors(error_type=ConfigError)
def validate_score_weights(score_weights):
    """验证分值权重配置文件的结构完整性
    
    检查分值权重配置文件是否包含所有必要的结构，确保分值计算正常。
    
    参数:
        score_weights (dict): 分值权重配置内容
        
    异常:
        ValueError: 如果缺少必要的结构，抛出包含缺失结构的异常
    
    验证项:
        - 章节权重(section_weights)
        - 问题权重(question_weights)
        - 问题类型基础分值(question_type_base_scores)
    """
    # 检查主要结构是否完整
    for key in ['section_weights', 'question_weights', 'question_type_base_scores']:
        if key not in score_weights:
            raise ValueError(f"score_weights.yaml 缺少关键字段: {key}")
    # 可进一步校验每个 section/question 的结构和类型，但目前仅进行基础结构检查

if __name__ == "__main__":
    CONFIG_DIR = 'config'
    # 加载配置
    def load_yaml(filename):
        path = os.path.join(CONFIG_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    lang_zh = load_yaml('lang_zh.yaml')
    lang_en = load_yaml('lang_en.yaml')
    score_weights = load_yaml('score_weights.yaml')

    lang_required_keys = [
        'app_title', 'section_scores', 'total_score', 'save_progress', 'load_progress',
        'progress_saved', 'progress_loaded', 'report_title', 'report_generate_time',
        'radar_chart', 'section_table', 'assessment_detail', 'export_pdf', 'export_excel',
        'zh_button', 'en_button', 'last_saved', 'system_assessment', 'result_analysis', 'report_export',
        'generate_excel_report', 'generating_excel_report', 'download_excel_report', 'excel_report_generated',
        'error_generating_excel_report', 'radar_chart_data', 'assessment_results',
        'generate_pdf_report', 'generating_pdf_report', 'download_pdf_report', 'pdf_report_generated',
        'failed_generating_pdf_report', 'overall_score', 'element_scores', 'cannot_generate_radar_chart',
        'score', 'question', 'type', 'weight', 'sub_question_scores', 'answer_yes', 'answer_no',
        'progress_auto_saved', 'last_progress_loaded', 'error_saving_progress', 'error_loading_progress',
        'element', 'element_scores_detail', 'detailed_assessment_results'
    ]
    try:
        validate_lang_config(lang_zh, lang_required_keys, "lang_zh.yaml")
        print("lang_zh.yaml 校验通过！")
        validate_lang_config(lang_en, lang_required_keys, "lang_en.yaml")
        print("lang_en.yaml 校验通过！")
        validate_score_weights(score_weights)
        print("score_weights.yaml 校验通过！")
    except Exception as e:
        print(f"配置校验失败: {e}") 