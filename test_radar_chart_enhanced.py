#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雷达图生成功能增强单元测试

该模块用于测试ISO 55001评估工具中雷达图生成功能的准确性和可靠性。
主要测试内容包括：
- 雷达图生成函数 (create_radar_chart)
- 百分比计算逻辑
- 不同场景下的图表生成

测试覆盖各种边界情况，确保雷达图生成的准确性和稳定性。
"""

import sys
import os
import pytest
import numpy as np

# 添加当前目录到Python路径，确保可以导入相关模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入要测试的函数
from app import create_radar_chart


def test_create_radar_chart_basic():
    """测试基本雷达图生成
    
    测试场景：
    - 正常的章节得分数据
    - 检查图表是否成功生成
    - 验证图表数据的基本结构
    """
    section_scores = {
        "organization_context": 45.5,
        "leadership": 120.3,
        "planning": 135.2,
        "support": 140.1,
        "operation": 280.7,
        "performance_evaluation": 130.5,
        "improvement": 45.6
    }
    
    # 生成雷达图
    fig = create_radar_chart(section_scores)
    
    # 验证图表是否成功生成
    assert fig is not None, "雷达图生成失败，返回了None"
    
    # 验证图表数据的基本结构
    assert hasattr(fig, 'data'), "图表对象缺少data属性"
    assert len(fig.data) > 0, "图表数据为空"
    
    # 验证雷达图的类型
    assert fig.data[0].type == 'scatterpolar', f"图表类型应为scatterpolar，实际为{fig.data[0].type}"
    
    # 验证数据点数量（应与章节数量一致）
    assert len(fig.data[0].r) == len(section_scores), f"数据点数量应与章节数量一致，预期{len(section_scores)}个，实际{len(fig.data[0].r)}个"
    assert len(fig.data[0].theta) == len(section_scores), f"角度点数量应与章节数量一致，预期{len(section_scores)}个，实际{len(fig.data[0].theta)}个"


def test_create_radar_chart_empty_scores():
    """测试空的章节得分情况
    
    测试场景：
    - 空的section_scores
    - None值作为输入
    """
    # 空的section_scores
    fig = create_radar_chart({})
    assert fig is None, "空的section_scores时应返回None，实际返回了图表对象"
    
    # None值作为输入
    fig = create_radar_chart(None)
    assert fig is None, "None作为输入时应返回None，实际返回了图表对象"


def test_create_radar_chart_percentage_calculation():
    """测试雷达图中的百分比计算逻辑
    
    测试场景：
    - 满分情况（应显示100%）
    - 接近满分情况（浮点数精度处理）
    - 零分情况（应显示0%）
    - 中间值情况
    """
    # 测试满分情况
    section_scores = {
        "organization_context": 90,   # 满分90
        "leadership": 120,            # 满分120
        "planning": 100               # 满分100
    }
    
    fig = create_radar_chart(section_scores)
    assert fig is not None, "雷达图生成失败"
    
    # 获取计算后的百分比值
    percentage_values = fig.data[0].r
    
    # 验证百分比计算
    assert all(value == 100 for value in percentage_values), f"满分情况下所有百分比应等于100，实际值为{percentage_values}"
    
    # 测试接近满分情况（考虑浮点数精度）
    section_scores = {
        "organization_context": 89.999999999,  # 接近满分90
        "leadership": 119.999999999            # 接近满分120
    }
    
    fig = create_radar_chart(section_scores)
    percentage_values = fig.data[0].r
    
    # 验证接近满分时是否处理为100%（差值<1e-6）
    assert all(value == 100 for value in percentage_values), f"接近满分情况下所有百分比应等于100，实际值为{percentage_values}"
    
    # 测试零分情况
    section_scores = {
        "organization_context": 0,  # 零分
        "leadership": 0             # 零分
    }
    
    fig = create_radar_chart(section_scores)
    percentage_values = fig.data[0].r
    
    # 验证零分时百分比是否为0
    assert all(value == 0 for value in percentage_values), f"零分情况下所有百分比应等于0，实际值为{percentage_values}"


def test_create_radar_chart_rounding():
    """测试雷达图中百分比的四舍五入逻辑
    
    验证百分比值是否正确四舍五入到1位小数。
    """
    # 设置特定分数，确保计算结果会触发四舍五入
    section_scores = {
        "organization_context": 67.5,   # 90分制，75.0%，无需四舍五入
        "leadership": 89.87,            # 120分制，74.8917%，应四舍五入为74.9% 
        "planning": 55.12               # 100分制，55.12%，应四舍五入为55.1% 
    }
    
    fig = create_radar_chart(section_scores)
    assert fig is not None, "雷达图生成失败"
    
    # 获取计算后的百分比值
    percentage_values = fig.data[0].r
    
    # 验证四舍五入结果
    expected_values = [75.0, 74.9, 55.1]
    
    for i, (actual, expected) in enumerate(zip(percentage_values, expected_values)):
        assert np.isclose(actual, expected, rtol=1e-4), f"百分比值四舍五入不正确，索引{i}：实际{actual}，预期{expected}"


def test_create_radar_chart_chinese_display():
    """测试中文显示情况下的雷达图生成
    
    验证中文环境下的图表生成功能。
    """
    import streamlit as st
    
    # 保存原始语言设置
    original_language = st.session_state.get('language', 'zh')
    
    try:
        # 设置为中文环境
        st.session_state.language = 'zh'
        
        section_scores = {
            "organization_context": 45.5,
            "leadership": 120.3,
        }
        
        fig = create_radar_chart(section_scores)
        assert fig is not None, "中文环境下雷达图生成失败"
        
        # 验证图表包含中文标签
        theta_values = fig.data[0].theta
        assert "组织环境" in theta_values, "雷达图应包含中文标签'组织环境'"
        assert "领导作用" in theta_values, "雷达图应包含中文标签'领导作用'"
        
    finally:
        # 恢复原始语言设置
        st.session_state.language = original_language


def test_create_radar_chart_english_display():
    """测试英文显示情况下的雷达图生成
    
    验证英文环境下的图表生成功能。
    """
    import streamlit as st
    
    # 保存原始语言设置
    original_language = st.session_state.get('language', 'zh')
    
    try:
        # 设置为英文环境
        st.session_state.language = 'en'
        
        section_scores = {
            "organization_context": 45.5,
            "leadership": 120.3,
        }
        
        fig = create_radar_chart(section_scores)
        assert fig is not None, "英文环境下雷达图生成失败"
        
        # 验证图表包含英文标签
        theta_values = fig.data[0].theta
        assert "Organization Context" in theta_values, "雷达图应包含英文标签'Organization Context'"
        assert "Leadership" in theta_values, "雷达图应包含英文标签'Leadership'"
        
    finally:
        # 恢复原始语言设置
        st.session_state.language = original_language


if __name__ == "__main__":
    # 运行所有测试
    print("开始运行雷达图生成功能增强单元测试...")
    
    test_create_radar_chart_basic()
    print("✓ 基本雷达图生成测试通过")
    
    test_create_radar_chart_empty_scores()
    print("✓ 空数据测试通过")
    
    test_create_radar_chart_percentage_calculation()
    print("✓ 百分比计算测试通过")
    
    test_create_radar_chart_rounding()
    print("✓ 四舍五入逻辑测试通过")
    
    test_create_radar_chart_chinese_display()
    print("✓ 中文显示测试通过")
    
    test_create_radar_chart_english_display()
    print("✓ 英文显示测试通过")
    
    print("\n所有雷达图测试通过！")
