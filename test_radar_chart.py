#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雷达图百分比计算测试工具

该模块用于测试和验证ISO 55001评估工具中雷达图百分比计算的准确性。
主要功能包括：
- 对比修改前后的雷达图百分比计算逻辑
- 测试各种分数场景的计算结果
- 验证浮点数精度处理的有效性
- 确保百分比显示的一致性和可读性

修改说明：
- 修改前：直接计算百分比，可能产生多位小数
- 修改后：四舍五入保留1位小数，提高可读性和一致性
- 特殊处理：当得分接近满分时（差值<1e-6），直接显示为100%
"""

import sys
import os

# 添加当前目录到Python路径，确保可以导入相关模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def calculate_radar_value(score, max_score):
    """计算雷达图百分比值
    
    对比修改前后的雷达图百分比计算逻辑，验证修改效果。
    
    参数:
        score (float): 实际得分
        max_score (float): 满分
    
    返回:
        tuple: (修改前百分比, 修改后百分比)
            - 修改前百分比: 未四舍五入的原始百分比值
            - 修改后百分比: 四舍五入到1位小数的百分比值
    
    计算逻辑:
        1. 如果得分与满分的差值小于1e-6（浮点数精度考虑），直接返回100%
        2. 如果满分不为0，计算得分/满分*100
        3. 如果满分为0，返回0%以避免除零错误
    """
    # 修改前的逻辑：直接计算，可能产生多位小数
    old_value = 100 if abs(score - max_score) < 1e-6 else (score / max_score * 100 if max_score else 0)
    
    # 修改后的逻辑：四舍五入到1位小数，提高可读性
    new_value = 100 if abs(score - max_score) < 1e-6 else (round(score / max_score * 100, 1) if max_score else 0)
    
    return old_value, new_value


def test_radar_chart_calculation():
    """测试雷达图百分比计算逻辑
    
    测试各种分数场景下修改前后的计算结果，验证修改效果。
    输出测试结果表格，包括分数、满分、修改前后的百分比值和差异。
    
    测试场景覆盖：
    - 满分场景
    - 整百分比场景
    - 半分场景
    - 接近满分场景
    - 接近零分场景
    - 小数得分场景
    """
    print("测试雷达图百分比计算逻辑...")
    print("\n" + "-" * 70)
    print(f"{'分数':<10} {'满分':<10} {'修改前百分比':<15} {'修改后百分比':<15} {'差异':<10}")
    print("-" * 70)
    
    # 测试场景定义
    test_cases = [
        (10, 10),      # 满分场景
        (9, 10),       # 整百分比场景
        (7.5, 10),     # 半分场景
        (5, 10),       # 中间值场景
        (2.5, 10),     # 低百分比场景
        (0, 10),       # 零分场景
        (34.5, 50),    # 部分得分场景
        (123.45, 150), # 小数得分场景
        (99.99, 100),  # 接近满分场景
        (0.01, 100),   # 接近零分场景
    ]
    
    # 执行测试并输出结果
    for score, max_score in test_cases:
        old_value, new_value = calculate_radar_value(score, max_score)
        difference = abs(old_value - new_value)
        print(f"{score:<10.2f} {max_score:<10} {old_value:<15.2f} {new_value:<15.1f} {difference:<10.2f}")
    
    print("-" * 70)
    print("\n测试完成！")


if __name__ == "__main__":
    # 主程序入口：执行雷达图计算测试
    test_radar_chart_calculation()
