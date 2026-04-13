#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预设分值生成工具

该脚本用于为ISO55001评估系统生成不同等级(A-E)的预设分值数据，
生成的数据将用于系统测试和演示。脚本根据配置文件和预设百分比，
随机生成符合各等级预期得分的问题回答。

输入:
    - config/questionnaire.yaml: 问卷配置文件，包含问题类型和结构
    - config/score_weights.yaml: 分值权重配置文件

输出:
    - config/preset_scores.yaml: 生成的预设分值文件，包含各等级的预设回答

使用方法:
    python generate_preset_scores.py
"""
import yaml
import random

# 读取问卷配置和权重配置
with open('config/questionnaire.yaml', 'r', encoding='utf-8') as f:
    questionnaire = yaml.safe_load(f)  # 加载问卷配置，包含问题结构和类型

with open('config/score_weights.yaml', 'r', encoding='utf-8') as f:
    score_weights = yaml.safe_load(f)  # 加载分值权重配置

# 章节映射（中文到英文）
# 用于将配置文件中的中文章节名称转换为系统内部使用的英文键名
section_mapping = {
    '组织环境': 'organization_context',  # 组织环境章节
    '领导作用': 'leadership',  # 领导作用章节
    '策划': 'planning',  # 策划章节
    '支持': 'support',  # 支持章节
    '运行': 'operation',  # 运行章节
    '绩效评价': 'performance_evaluation',  # 绩效评价章节
    '改进': 'improvement'  # 改进章节
}

# 预设分值配置
# 定义不同等级(A-E)对应的总得分，总分为1000分
grade_scores = {
    'A': 900,  # 优秀: 90% of 1000
    'B': 800,  # 良好: 80% of 1000
    'C': 700,  # 合格: 70% of 1000
    'D': 600,  # 基本合格: 60% of 1000
    'E': 500   # 不合格: 50% of 1000
}

def generate_preset_scores(questionnaire_data=None):
    """生成预设分值数据
    
    根据配置文件和预设百分比，为不同等级(A-E)生成符合预期得分的预设问题回答。
    支持三种问题类型：XO(是/否)、PJ(等级评分)和PW(多选)。
    
    参数:
        questionnaire_data (dict, optional): 问卷配置数据，如果不提供则从默认配置文件加载
    
    返回:
        dict: 包含不同等级预设分值的字典结构，格式如下：
            {
                'preset_scores': {  # XO和PJ类型问题的预设回答
                    'A': {
                        'organization_context': {
                            'q1': 'yes',  # XO类型问题回答
                            'q2': 4      # PJ类型问题得分（0-4）
                        }
                    },
                    # ... 其他等级
                },
                'preset_sub_scores': {  # PW类型问题的预设回答
                    'A': {
                        'organization_context': {
                            'q3': [True, False, True]  # 子问题选中状态
                        }
                    },
                    # ... 其他等级
                }
            }
    
    生成逻辑:
        - XO类型: 根据等级百分比随机选择"是"或"否"，百分比越高选择"是"的概率越大
        - PJ类型: 根据等级百分比计算平均得分，四舍五入到整数（0-4）
        - PW类型: 根据等级百分比计算需要选中的子问题数量，随机选择指定数量的子问题
    """
    preset_scores = {
        'preset_scores': {},  # XO和PJ类型的问题回答
        'preset_sub_scores': {}  # PW类型的问题子回答
    }
    
    # 如果没有提供问卷数据，则从默认配置文件加载
    current_questionnaire = questionnaire_data if questionnaire_data else questionnaire
    
    # 为每个等级(A-E)生成预设分值
    for grade, total_score in grade_scores.items():
        preset_scores['preset_scores'][grade] = {}
        preset_scores['preset_sub_scores'][grade] = {}
        
        # 计算当前等级对应的百分比 (0-1)
        percentage = total_score / 1000  # 总分为1000分
        
        # 遍历所有章节（保持questionnaire.yaml中的原始顺序）
        for section_zh in list(current_questionnaire.keys()):
            section_data = current_questionnaire[section_zh]
            section_en = section_mapping[section_zh]  # 转换为英文键名
            preset_scores['preset_scores'][grade][section_en] = {}
            preset_scores['preset_sub_scores'][grade][section_en] = {}
            
            # 遍历章节中的所有问题
            for q_id, q_data in section_data.items():
                q_type = q_data['type']
                
                if q_type == 'XO':
                    # XO类型：是/否问题
                    # 逻辑：等级百分比越高，选择"是"的概率越大
                    if random.random() < percentage:
                        preset_scores['preset_scores'][grade][section_en][q_id] = 'yes'  # 选择"是"
                    else:
                        preset_scores['preset_scores'][grade][section_en][q_id] = 'no'   # 选择"否"
                        
                elif q_type == 'PJ':
                    # PJ类型：等级评分问题（0-4分）
                    # 逻辑：根据等级百分比计算平均得分，四舍五入到最近的整数
                    avg_score = 4 * percentage  # 最高分为4分
                    preset_scores['preset_scores'][grade][section_en][q_id] = round(avg_score)
                    
                elif q_type == 'PW':
                    # PW类型：多选题
                    sub_questions = q_data.get('sub_questions', [])  # 获取子问题列表
                    num_sub = len(sub_questions)
                    
                    # 计算需要选中的子问题数量，根据等级百分比确定
                    num_selected = round(num_sub * percentage)
                    # 随机选择指定数量的子问题索引
                    selected_indices = random.sample(range(num_sub), num_selected)
                    
                    # 创建布尔值列表，表示哪些子问题被选中
                    sub_scores = [False] * num_sub  # 初始化所有子问题为未选中
                    for idx in selected_indices:
                        sub_scores[idx] = True  # 标记选中的子问题
                        
                    preset_scores['preset_sub_scores'][grade][section_en][q_id] = sub_scores
    
    return preset_scores

# 生成预设分值
preset_scores = generate_preset_scores()

# 保存到YAML文件
with open('config/preset_scores.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(preset_scores, f, 
              default_flow_style=False,  # 使用缩进格式而非流式格式
              allow_unicode=True,  # 允许保存Unicode字符
              sort_keys=False)  # 保持原始顺序

print("预设分值YAML文件已生成：config/preset_scores.yaml")
