#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心分数计算模块单元测试

该模块用于测试ISO 55001评估工具中核心分数计算功能的准确性。
主要测试内容包括：
- 合规分数计算函数 (calculate_compliance_score)
- 总分计算函数 (calculate_total_score)

测试覆盖各种问题类型(XO/PJ/PW)和不同场景，确保分数计算的准确性。
"""

import sys
import os
import pytest

# 添加当前目录到Python路径，确保可以导入相关模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入要测试的函数
from app import calculate_compliance_score, calculate_total_score


def test_calculate_compliance_score_xo_type():
    """测试XO类型问题的合规分数计算
    
    测试场景：
    - XO类型问题回答"是"(4分)
    - XO类型问题回答"否"(0分)
    - 不同权重下的计算结果
    """
    # XO类型：回答"是"(4分)，权重1
    score = calculate_compliance_score(4, "XO", None, 1)
    assert score == 1.0, f"XO类型回答'是'，权重1时得分应为1.0，实际为{score}"
    
    # XO类型：回答"是"(4分)，权重10
    score = calculate_compliance_score(4, "XO", None, 10)
    assert score == 10.0, f"XO类型回答'是'，权重10时得分应为10.0，实际为{score}"
    
    # XO类型：回答"否"(0分)，权重1
    score = calculate_compliance_score(0, "XO", None, 1)
    assert score == 0.0, f"XO类型回答'否'，权重1时得分应为0.0，实际为{score}"
    
    # XO类型：回答"否"(0分)，权重5
    score = calculate_compliance_score(0, "XO", None, 5)
    assert score == 0.0, f"XO类型回答'否'，权重5时得分应为0.0，实际为{score}"
    
    # XO类型：回答其他值(2分)，权重1
    score = calculate_compliance_score(2, "XO", None, 1)
    assert score == 0.0, f"XO类型回答非'是'(2分)，权重1时得分应为0.0，实际为{score}"


def test_calculate_compliance_score_pj_type():
    """测试PJ类型问题的合规分数计算
    
    测试场景：
    - 不同评分等级(0-4分)下的得分
    - 不同权重下的计算结果
    """
    # PJ类型：0分(未实施)，权重1
    score = calculate_compliance_score(0, "PJ", None, 1)
    assert score == 0.0, f"PJ类型0分，权重1时得分应为0.0，实际为{score}"
    
    # PJ类型：1分(初步实施)，权重1
    score = calculate_compliance_score(1, "PJ", None, 1)
    assert score == 0.25, f"PJ类型1分，权重1时得分应为0.25，实际为{score}"
    
    # PJ类型：2分(部分实施)，权重1
    score = calculate_compliance_score(2, "PJ", None, 1)
    assert score == 0.5, f"PJ类型2分，权重1时得分应为0.5，实际为{score}"
    
    # PJ类型：3分(大部分实施)，权重1
    score = calculate_compliance_score(3, "PJ", None, 1)
    assert score == 0.75, f"PJ类型3分，权重1时得分应为0.75，实际为{score}"
    
    # PJ类型：4分(完全实施)，权重1
    score = calculate_compliance_score(4, "PJ", None, 1)
    assert score == 1.0, f"PJ类型4分，权重1时得分应为1.0，实际为{score}"
    
    # PJ类型：3分，权重20
    score = calculate_compliance_score(3, "PJ", None, 20)
    assert score == 15.0, f"PJ类型3分，权重20时得分应为15.0，实际为{score}"
    
    # PJ类型：4分，权重15
    score = calculate_compliance_score(4, "PJ", None, 15)
    assert score == 15.0, f"PJ类型4分，权重15时得分应为15.0，实际为{score}"


def test_calculate_compliance_score_pw_type():
    """测试PW类型问题的合规分数计算
    
    测试场景：
    - 不同子问题选中比例下的得分
    - 不同权重下的计算结果
    - 子问题为空的情况
    """
    # PW类型：3个子问题选中2个，权重1
    sub_responses = {"sub_1": True, "sub_2": True, "sub_3": False}
    score = calculate_compliance_score(0, "PW", sub_responses, 1)
    assert score == pytest.approx(0.6667, 0.001), f"PW类型选中2/3，权重1时得分应为0.6667，实际为{score}"
    
    # PW类型：5个子问题选中3个，权重10
    sub_responses = {
        "sub_1": True, "sub_2": True, "sub_3": True, 
        "sub_4": False, "sub_5": False
    }
    score = calculate_compliance_score(0, "PW", sub_responses, 10)
    assert score == 6.0, f"PW类型选中3/5，权重10时得分应为6.0，实际为{score}"
    
    # PW类型：全部选中，权重5
    sub_responses = {"sub_1": True, "sub_2": True, "sub_3": True}
    score = calculate_compliance_score(0, "PW", sub_responses, 5)
    assert score == 5.0, f"PW类型全部选中，权重5时得分应为5.0，实际为{score}"
    
    # PW类型：全部未选中，权重1
    sub_responses = {"sub_1": False, "sub_2": False, "sub_3": False}
    score = calculate_compliance_score(0, "PW", sub_responses, 1)
    assert score == 0.0, f"PW类型全部未选中，权重1时得分应为0.0，实际为{score}"
    
    # PW类型：子问题为空，权重1
    score = calculate_compliance_score(0, "PW", {}, 1)
    assert score == 0.0, f"PW类型子问题为空，权重1时得分应为0.0，实际为{score}"
    
    # PW类型：子问题为None，权重1
    score = calculate_compliance_score(0, "PW", None, 1)
    assert score == 0.0, f"PW类型子问题为None，权重1时得分应为0.0，实际为{score}"


def test_calculate_compliance_score_edge_cases():
    """测试合规分数计算的边界情况
    
    测试场景：
    - 无效的问题类型
    - 无效的分数值
    - 极端权重值
    """
    # 无效的问题类型
    score = calculate_compliance_score(4, "INVALID", None, 1)
    assert score == 0.0, f"无效问题类型时得分应为0.0，实际为{score}"
    
    # 极端权重值
    score = calculate_compliance_score(4, "XO", None, 0)
    assert score == 0.0, f"权值为0时得分应为0.0，实际为{score}"
    
    # 非常大的权重值
    score = calculate_compliance_score(4, "XO", None, 1000)
    assert score == 1000.0, f"权值为1000时得分应为1000.0，实际为{score}"


def test_calculate_total_score():
    """测试总分计算函数
    
    测试场景：
    - 正常章节得分
    - 空的章节得分
    - 极端值情况
    """
    # 正常章节得分
    section_scores = {
        "organization_context": 45.5,
        "leadership": 120.3,
        "planning": 135.2,
        "support": 140.1,
        "operation": 280.7,
        "performance_evaluation": 130.5,
        "improvement": 45.6
    }
    total = calculate_total_score(section_scores)
    expected_total = sum(section_scores.values())
    assert total == expected_total, f"总分应为{expected_total}，实际为{total}"
    
    # 空的章节得分
    total = calculate_total_score({})
    assert total == 0.0, f"空章节得分时总分应为0.0，实际为{total}"
    
    # None值情况
    total = calculate_total_score(None)
    assert total == 0.0, f"章节得分为None时总分应为0.0，实际为{total}"


if __name__ == "__main__":
    # 运行所有测试
    print("开始运行核心分数计算模块单元测试...")
    
    test_calculate_compliance_score_xo_type()
    print("✓ XO类型问题测试通过")
    
    test_calculate_compliance_score_pj_type()
    print("✓ PJ类型问题测试通过")
    
    test_calculate_compliance_score_pw_type()
    print("✓ PW类型问题测试通过")
    
    test_calculate_compliance_score_edge_cases()
    print("✓ 边界情况测试通过")
    
    test_calculate_total_score()
    print("✓ 总分计算测试通过")
    
    print("\n所有测试通过！")
