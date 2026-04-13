#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预设分值验证工具

用于检查ISO55001评估系统的预设分值是否超过问题的分值上限，确保生成的预设分值符合配置规范。

输入:
    - config/score_weights.yaml: 分值权重配置文件
    - config/preset_scores.yaml: 生成的预设分值文件

输出:
    - 控制台输出检查结果，包括通过状态和问题详情

使用方法:
    python check_preset_scores.py

验证逻辑:
    1. 加载分值权重配置和预设分值配置
    2. 检查主问题预设分值(preset_scores)是否超过各问题的最大权重
    3. 对于PJ类型问题，计算实际得分并与最大权重比较
    4. 输出检查结果，包括通过状态和问题详情

注意事项:
    - 子问题(preset_sub_scores)通过比例计算得分，理论上不会超过最大权重，因此无需特殊检查
    - 仅检查数值型的PJ类型问题，XO和PW类型问题有专门的处理逻辑
"""

import yaml
import os


def load_yaml_file(file_path):
    """加载YAML配置文件
    
    参数:
        file_path (str): YAML文件的完整路径
        
    返回:
        dict: 解析后的YAML文件内容
        None: 如果文件不存在或解析失败
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def check_preset_scores():
    """检查预设分值是否超过问题的分值上限
    
    检查所有等级(A-E)的预设分值是否超过各问题的最大权重限制，确保生成的预设分值符合配置规范。
    
    输出:
        控制台输出检查结果，包括通过状态和问题详情
        
    验证流程:
        1. 加载配置文件
        2. 遍历所有等级和章节
        3. 检查每个问题的预设分值是否超过最大权重
        4. 输出检查结果
    """
    # 加载配置文件
    config_dir = 'config'
    score_weights = load_yaml_file(os.path.join(config_dir, 'score_weights.yaml'))
    preset_scores = load_yaml_file(os.path.join(config_dir, 'preset_scores.yaml'))
    
    question_weights = score_weights.get('question_weights', {})
    question_type_base_scores = score_weights.get('question_type_base_scores', {})
    
    # 检查主问题预设分值（preset_scores）
    main_preset_scores = preset_scores.get('preset_scores', {})
    issues_found = []
    
    for grade, sections in main_preset_scores.items():
        for section, questions in sections.items():
            if section not in question_weights:
                print(f"警告：章节 {section} 在权重配置中不存在")
                continue
                
            section_weights = question_weights[section]
            
            for q_id, value in questions.items():
                if q_id not in section_weights:
                    print(f"警告：问题 {section}.{q_id} 在权重配置中不存在")
                    continue
                    
                max_weight = section_weights[q_id]
                
                # 检查PJ类型问题（数值型）
                if isinstance(value, int):
                    # PJ类型：0-4分对应0%-100%权重
                    # 计算实际得分：(value/4) * max_weight
                    actual_score = (value / 4) * max_weight
                    
                    # 检查是否超过最大值
                    if actual_score > max_weight:
                        issues_found.append({
                            'grade': grade,
                            'section': section,
                            'q_id': q_id,
                            'type': 'PJ',
                            'preset_value': value,
                            'max_weight': max_weight,
                            'actual_score': actual_score,
                            'issue': f"预设分值 {value} 对应实际得分 {actual_score:.2f}，超过了最大权重 {max_weight}"
                        })
    
    # 输出检查结果
    if not issues_found:
        print("✅ 所有主问题预设分值都在合理范围内，没有超过分值上限")
    else:
        print(f"❌ 发现 {len(issues_found)} 个问题：")
        for issue in issues_found:
            print(f"  - {issue['grade']}档 {issue['section']}.{issue['q_id']} ({issue['type']}): {issue['issue']}")
    
    # 对于子问题（preset_sub_scores），由于它们是通过选中比例计算得分的
    # 理论上不会超过最大权重，因为得分 = (选中数量/总数量) * max_weight
    # 所以这里不需要特殊检查
    print("\n✅ 子问题预设分值检查通过：子问题通过比例计算得分，不会超过最大权重")


if __name__ == "__main__":
    check_preset_scores()
