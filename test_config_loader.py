#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载与验证模块单元测试

该模块用于测试ISO 55001评估工具中配置加载和验证功能的准确性和可靠性。
主要测试内容包括：
- 配置文件加载功能 (config_loader.py)
- 配置文件验证功能 (config_validator.py)

测试覆盖各种边界情况，确保配置加载和验证的准确性和稳定性。
"""

import sys
import os
import pytest
import yaml

# 添加当前目录到Python路径，确保可以导入相关模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入要测试的函数和类
from config_loader import load_yaml, Config, CONFIG_DIR
from config_validator import validate_lang_config, validate_score_weights


# 测试配置加载功能
def test_load_yaml():    
    """测试YAML文件加载功能
    
    测试场景：
    - 加载存在的有效YAML文件
    - 验证返回的数据类型和内容
    """
    # 测试加载score_weights.yaml
    score_weights = load_yaml('score_weights.yaml')
    assert score_weights is not None, "YAML文件加载失败"
    assert isinstance(score_weights, dict), "YAML文件加载结果应为字典类型"
    
    # 验证配置文件包含必要的键
    assert 'section_weights' in score_weights, "score_weights.yaml缺少section_weights键"
    assert 'question_weights' in score_weights, "score_weights.yaml缺少question_weights键"
    assert 'question_type_base_scores' in score_weights, "score_weights.yaml缺少question_type_base_scores键"


def test_config_class_initialization():    
    """测试Config类的初始化
    
    测试场景：
    - Config类实例化后是否正确加载所有配置
    """
    config = Config()
    
    # 验证所有配置都已加载
    assert config.score_weights is not None, "Config类未正确加载score_weights配置"
    assert config.lang_zh is not None, "Config类未正确加载中文语言配置"
    assert config.lang_en is not None, "Config类未正确加载英文语言配置"
    assert config.general is not None, "Config类未正确加载通用配置"
    
    # 验证配置类型
    assert isinstance(config.score_weights, dict), "score_weights配置应为字典类型"
    assert isinstance(config.lang_zh, dict), "中文语言配置应为字典类型"
    assert isinstance(config.lang_en, dict), "英文语言配置应为字典类型"
    assert isinstance(config.general, dict), "通用配置应为字典类型"


# 测试配置验证功能
def test_validate_lang_config():    
    """测试语言配置验证功能
    
    测试场景：
    - 验证包含所有必要键的语言配置
    - 验证缺少必要键的语言配置
    """
    # 创建一个包含所有必要键的测试语言配置
    required_keys = ['app_title', 'section_scores', 'total_score']
    valid_lang_config = {
        'app_title': '测试应用',
        'section_scores': '章节得分',
        'total_score': '总分'
    }
    
    # 测试有效的语言配置
    try:
        validate_lang_config(valid_lang_config, required_keys, "test_lang.yaml")
    except ValueError:
        pytest.fail("validate_lang_config错误地拒绝了有效的语言配置")
    
    # 测试缺少必要键的语言配置
    invalid_lang_config = {
        'app_title': '测试应用',
        # 缺少section_scores和total_score
    }
    
    with pytest.raises(Exception) as excinfo:
        validate_lang_config(invalid_lang_config, required_keys, "test_lang.yaml")
    
    # 验证错误信息包含缺少的键
    error_message = str(excinfo.value)
    assert "section_scores" in error_message, "错误信息应包含缺少的键'section_scores'"
    assert "total_score" in error_message, "错误信息应包含缺少的键'total_score'"


def test_validate_score_weights():    
    """测试分值权重配置验证功能
    
    测试场景：
    - 验证结构完整的分值权重配置
    - 验证缺少必要结构的分值权重配置
    """
    # 创建一个结构完整的测试分值权重配置
    valid_score_weights = {
        'section_weights': {
            'organization_context': 50
        },
        'question_weights': {
            'org_1': 1
        },
        'question_type_base_scores': {
            'XO': 100,
            'PJ': 100,
            'PW': 100
        }
    }
    
    # 测试有效的分值权重配置
    try:
        validate_score_weights(valid_score_weights)
    except ValueError:
        pytest.fail("validate_score_weights错误地拒绝了有效的分值权重配置")
    
    # 测试缺少必要结构的分值权重配置
    missing_section_weights = {
        'question_weights': {
            'org_1': 1
        },
        'question_type_base_scores': {
            'XO': 100
        }
        # 缺少section_weights
    }
    
    with pytest.raises(Exception) as excinfo:
        validate_score_weights(missing_section_weights)
    
    # 验证错误信息包含缺少的结构
    assert "section_weights" in str(excinfo.value), "错误信息应包含缺少的结构'section_weights'"
    
    # 测试缺少其他必要结构
    missing_question_weights = {
        'section_weights': {
            'organization_context': 50
        },
        'question_type_base_scores': {
            'XO': 100
        }
        # 缺少question_weights
    }
    
    with pytest.raises(Exception) as excinfo:
        validate_score_weights(missing_question_weights)
    
    assert "question_weights" in str(excinfo.value), "错误信息应包含缺少的结构'question_weights'"
    
    missing_base_scores = {
        'section_weights': {
            'organization_context': 50
        },
        'question_weights': {
            'org_1': 1
        }
        # 缺少question_type_base_scores
    }
    
    with pytest.raises(Exception) as excinfo:
        validate_score_weights(missing_base_scores)
    
    assert "question_type_base_scores" in str(excinfo.value), "错误信息应包含缺少的结构'question_type_base_scores'"


if __name__ == "__main__":
    # 运行所有测试
    print("开始运行配置加载与验证模块单元测试...")
    
    test_load_yaml()
    print("✓ YAML文件加载测试通过")
    
    test_config_class_initialization()
    print("✓ Config类初始化测试通过")
    
    test_validate_lang_config()
    print("✓ 语言配置验证测试通过")
    
    test_validate_score_weights()
    print("✓ 分值权重配置验证测试通过")
    
    print("\n所有配置加载与验证模块测试通过！")
