#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权重配置生成工具

当用户更新questionnaire.yaml和questionnaire_en.yaml后，手动运行此脚本，
根据score_weights.yaml中的章节权重自动分配默认问题权重。
"""

import yaml
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 全局章节名称映射
SECTION_MAPPING = {
    'organization_context': '组织环境',
    'leadership': '领导作用',
    'planning': '策划',
    'support': '支持',
    'operation': '运行',
    'performance_evaluation': '绩效评价',
    'improvement': '改进'
}

# 反向章节映射（用于从中文映射到英文ID）
REVERSE_SECTION_MAPPING = {v: k for k, v in SECTION_MAPPING.items()}

def load_config_files():
    """加载所有配置文件"""
    config_dir = 'config'
    
    # 加载中文问卷
    with open(os.path.join(config_dir, 'questionnaire.yaml'), 'r', encoding='utf-8') as f:
        questions_zh = yaml.safe_load(f)
    logging.info("成功加载中文问卷配置")
    
    # 加载英文问卷
    with open(os.path.join(config_dir, 'questionnaire_en.yaml'), 'r', encoding='utf-8') as f:
        questions_en = yaml.safe_load(f)
    logging.info("成功加载英文问卷配置")
    
    # 加载现有权重配置
    with open(os.path.join(config_dir, 'score_weights.yaml'), 'r', encoding='utf-8') as f:
        score_weights = yaml.safe_load(f)
    logging.info("成功加载现有权重配置")
    
    return questions_zh, questions_en, score_weights

def validate_questionnaires(questions_zh, questions_en):
    """验证中英文问卷的一致性"""
    # 检查章节一致性
    zh_sections = set(questions_zh.keys())
    en_sections = set(questions_en.keys())
    
    # 转换中文章节名称为英文ID
    zh_sections_en_ids = {REVERSE_SECTION_MAPPING.get(section, section) for section in zh_sections}
    
    if zh_sections_en_ids != en_sections:
        logging.warning("中英文问卷章节不一致！")
        logging.warning(f"中文问卷章节（英文ID）: {zh_sections_en_ids}")
        logging.warning(f"英文问卷章节: {en_sections}")
        return False
    
    # 检查每个章节的问题数量一致性
    for en_section in en_sections:
        zh_section = SECTION_MAPPING.get(en_section, en_section)
        
        if zh_section in questions_zh:
            zh_questions = questions_zh[zh_section].keys()
            en_questions = questions_en[en_section].keys()
            
            if set(zh_questions) != set(en_questions):
                logging.warning(f"章节 '{en_section}' 中英文问题不一致！")
                logging.warning(f"中文问题: {sorted(zh_questions)}")
                logging.warning(f"英文问题: {sorted(en_questions)}")
                return False
    
    logging.info("中英文问卷验证通过")
    return True

def generate_question_weights(questions_en, section_weights):
    """根据章节权重自动分配问题权重"""
    question_weights = {}
    
    for section, weight in section_weights.items():
        if section not in questions_en:
            logging.warning(f"章节 '{section}' 在问卷中不存在，跳过权重分配")
            continue
        
        questions = questions_en[section]
        question_count = len(questions)
        
        if question_count == 0:
            logging.warning(f"章节 '{section}' 没有问题，跳过权重分配")
            question_weights[section] = {}
            continue
        
        # 平均分配权重（确保整数）
        base_weight = weight // question_count  # 整数除法
        remainder = weight % question_count    # 余数
        
        # 分配权重（确保总和等于章节权重）
        section_question_weights = {}
        
        # 按数字顺序排序问题ID
        sorted_q_ids = sorted(questions.keys(), key=lambda x: int(x[1:]))
        
        for i, q_id in enumerate(sorted_q_ids):
            if i < remainder:
                # 前remainder个问题每个加1，分配余数
                question_weight = base_weight + 1
            else:
                question_weight = base_weight
            
            section_question_weights[q_id] = question_weight
        
        # 验证总和是否准确
        actual_total = sum(section_question_weights.values())
        if actual_total != weight:
            logging.error(f"章节 '{section}' 权重总和不准确！预期: {weight}, 实际: {actual_total}")
        else:
            logging.debug(f"章节 '{section}' 权重总和准确: {actual_total}")
        

        
        question_weights[section] = section_question_weights
        logging.info(f"为章节 '{section}' 生成权重配置（{question_count}个问题，总权重 {weight}）")
    
    return question_weights

def save_updated_weights(score_weights, question_weights):
    """保存更新后的权重配置"""
    # 更新问题权重
    score_weights['question_weights'] = question_weights
    
    # 保存到文件
    config_dir = 'config'
    with open(os.path.join(config_dir, 'score_weights.yaml'), 'w', encoding='utf-8') as f:
        yaml.dump(score_weights, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    logging.info("权重配置已成功更新到 score_weights.yaml")

def main():
    """主函数"""
    logging.info("开始生成权重配置...")
    
    try:
        # 加载配置文件
        questions_zh, questions_en, score_weights = load_config_files()
        
        # 验证问卷一致性
        if not validate_questionnaires(questions_zh, questions_en):
            logging.error("问卷验证失败，请检查中英文问卷配置的一致性")
            return 1
        
        # 获取章节权重配置
        section_weights = score_weights.get('section_weights', {})
        if not section_weights:
            logging.error("未找到章节权重配置，请检查 score_weights.yaml 文件")
            return 1
        
        # 生成问题权重
        question_weights = generate_question_weights(questions_en, section_weights)
        
        # 保存更新后的权重配置
        save_updated_weights(score_weights, question_weights)
        
        logging.info("权重配置生成完成！")
        return 0
        
    except Exception as e:
        logging.error(f"生成权重配置时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())