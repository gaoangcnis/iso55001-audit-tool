#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较中英文语言文件的键，识别缺失的键
"""

import yaml
import os

def compare_lang_files():
    """比较中英文语言文件的键"""
    # 读取语言文件
    with open('config/lang_zh.yaml', 'r', encoding='utf-8') as f:
        lang_zh = yaml.safe_load(f)
    
    with open('config/lang_en.yaml', 'r', encoding='utf-8') as f:
        lang_en = yaml.safe_load(f)
    
    # 获取所有键
    keys_zh = set(lang_zh.keys())
    keys_en = set(lang_en.keys())
    
    # 找出缺失的键
    missing_in_en = keys_zh - keys_en
    missing_in_zh = keys_en - keys_zh
    
    # 输出结果
    print("中英文语言文件比较结果：")
    print(f"中文文件键数量：{len(keys_zh)}")
    print(f"英文文件键数量：{len(keys_en)}")
    print()
    
    if missing_in_en:
        print(f"中文文件中有，但英文文件中缺失的键：{missing_in_en}")
    else:
        print("英文文件包含中文文件的所有键")
    
    print()
    
    if missing_in_zh:
        print(f"英文文件中有，但中文文件中缺失的键：{missing_in_zh}")
    else:
        print("中文文件包含英文文件的所有键")
    
    print()
    
    if not missing_in_en and not missing_in_zh:
        print("✅ 中英文语言文件的键完全一致！")
    else:
        print("❌ 中英文语言文件的键存在差异！")

if __name__ == "__main__":
    compare_lang_files()