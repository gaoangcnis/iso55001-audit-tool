#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库操作模块单元测试

该模块用于测试ISO 55001评估工具中数据库操作功能的准确性和可靠性。
主要测试内容包括：
- 数据库连接管理
- 数据库初始化
- 评估结果保存
- 评估结果加载

测试使用临时数据库，避免影响实际数据。
"""

import sys
import os
import pytest
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

# 添加当前目录到Python路径，确保可以导入相关模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入app模块中的函数
import app
from app import init_db


# 定义测试数据库文件名
TEST_DB_NAME = 'test_assessment_data.db'


@pytest.fixture(scope='function')
def setup_test_database(monkeypatch):
    """设置测试数据库
    
    创建一个临时数据库文件用于测试，并在测试结束后清理。
    """
    print(f"=== 设置测试数据库开始 ===")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 使用绝对路径的测试数据库
    global TEST_DB_NAME
    TEST_DB_NAME = os.path.join(os.getcwd(), 'test_assessment_data.db')
    print(f"测试数据库文件绝对路径: {TEST_DB_NAME}")
    
    # 替换原有的数据库连接函数，使用测试数据库
    @contextmanager
    def mock_get_db_connection(db_name=None):
        conn = None
        try:
            # 使用测试数据库名，忽略传入的参数
            conn = sqlite3.connect(TEST_DB_NAME)
            print(f"✓ 成功连接到测试数据库: {TEST_DB_NAME}")
            yield conn
        finally:
            if conn:
                print(f"✓ 关闭数据库连接: {TEST_DB_NAME}")
                conn.close()
    
    # 使用monkeypatch替换原函数
    monkeypatch.setattr('app.get_db_connection', mock_get_db_connection)
    print(f"✓ 已替换数据库连接函数")
    
    # 初始化测试数据库
    print(f"准备初始化数据库...")
    app.init_db()
    print(f"✓ 数据库初始化完成")
    
    # 检查数据库文件是否存在
    if os.path.exists(TEST_DB_NAME):
        print(f"✓ 测试数据库文件已创建")
        print(f"文件大小: {os.path.getsize(TEST_DB_NAME)} 字节")
    else:
        print(f"✗ 测试数据库文件不存在！")
    
    # 检查数据库表是否存在
    with mock_get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assessment_results'")
        table_exists = c.fetchone()
        print(f"表 'assessment_results' 是否存在: {table_exists}")
    
    yield  # 测试执行位置
    
    # 清理测试数据库
    if os.path.exists(TEST_DB_NAME):
        print(f"=== 清理测试数据库 ===")
        os.remove(TEST_DB_NAME)
        print(f"✓ 已删除测试数据库: {TEST_DB_NAME}")
    else:
        print(f"✗ 测试数据库文件不存在，无法清理")


# 测试数据库连接管理
def test_get_db_connection(setup_test_database):
    """测试数据库连接上下文管理器
    
    测试场景：
    - 正常获取数据库连接
    - 确保连接在使用后正确关闭
    """
    # 测试数据库连接
    with app.get_db_connection() as conn:
        assert conn is not None, "数据库连接失败"
        assert isinstance(conn, sqlite3.Connection), "连接对象类型不正确"
    
    # 验证连接已关闭
    try:
        conn.execute("SELECT 1")
        assert False, "数据库连接未正确关闭"
    except sqlite3.ProgrammingError:
        # 预期的错误，连接已关闭
        pass


# 测试数据库初始化
def test_init_db(setup_test_database):
    """测试数据库初始化功能
    
    测试场景：
    - 验证数据库表是否正确创建
    """
    with app.get_db_connection() as conn:
        c = conn.cursor()
        
        # 检查assessment_results表是否存在
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assessment_results'")
        table_exists = c.fetchone()
        assert table_exists is not None, "assessment_results表创建失败"
        
        # 检查表结构
        c.execute("PRAGMA table_info(assessment_results)")
        columns = [column[1] for column in c.fetchall()]
        
        # 验证必要的列是否存在
        expected_columns = ['id', 'timestamp', 'responses', 'sub_responses']
        for column in expected_columns:
            assert column in columns, f"表中缺少必要的列: {column}"


# 测试评估结果保存
def test_save_assessment_results(setup_test_database):
    """测试保存评估结果功能
    
    测试场景：
    - 保存评估结果到数据库
    - 验证数据是否正确保存
    """
    # 准备测试数据
    test_responses = {
        'org_1': 'yes',
        'org_2': 'no',
        'lead_1': '5'
    }
    
    test_sub_responses = {
        'org_1_1': 'yes',
        'org_1_2': 'no'
    }
    
    # 保存评估结果
    print(f"准备保存的responses: {test_responses}")
    print(f"准备保存的sub_responses: {test_sub_responses}")
    
    try:
        app.save_assessment_results(test_responses, test_sub_responses)
        print("app.save_assessment_results调用成功")
    except Exception as e:
        print(f"app.save_assessment_results调用失败: {e}")
        raise
    
    # 验证数据是否正确保存
    print(f"=== 开始验证数据 ===")
    print(f"读取数据库: {TEST_DB_NAME}")
    with app.get_db_connection() as conn:
        print(f"✓ 读取数据的数据库连接成功")
        print(f"连接对象: {conn}")
        c = conn.cursor()
        
        # 检查表结构
        c.execute("PRAGMA table_info(assessment_results)")
        table_info = c.fetchall()
        print(f"表结构: {table_info}")
        
        # 检查是否有记录
        print(f"执行查询: SELECT COUNT(*) FROM assessment_results")
        c.execute("SELECT COUNT(*) FROM assessment_results")
        count = c.fetchone()[0]      
        print(f"数据库中的记录数: {count}")

        # 查看所有记录
        print(f"执行查询: SELECT * FROM assessment_results ORDER BY timestamp DESC LIMIT 1")
        c.execute("SELECT * FROM assessment_results ORDER BY timestamp DESC LIMIT 1")
        result = c.fetchone()        
        print(f"查询结果: {result}")

        assert result is not None, " 数据保存失败，未找到记录"
        
        # 验证数据内容
        saved_responses = json.loads(result[2])
        saved_sub_responses = json.loads(result[3])

        assert saved_responses == test_responses, "保存的responses数据与原始数据不符"
        assert saved_sub_responses == test_sub_responses, "保存的sub_responses数据与原始数据不符"
        
        # 验证时间戳格式
        try:
            datetime.fromisoformat(result[1])
        except ValueError:
            assert False, "时间戳格式不正确"


# 测试评估结果加载
def test_load_latest_assessment_results(setup_test_database):
    """测试加载最近评估结果功能
    
    测试场景：
    - 保存多条评估结果
    - 验证加载的是最新的结果
    """
    # 保存第一条评估结果
    first_responses = {
        'test_1': 'yes',
        'test_2': 'no'
    }
    first_sub_responses = {
        'test_1_1': 'yes'
    }
    app.save_assessment_results(first_responses, first_sub_responses)
    
    # 保存第二条评估结果
    second_responses = {
        'test_1': 'no',
        'test_2': 'yes',
        'test_3': 'yes'
    }
    second_sub_responses = {
        'test_1_1': 'no',
        'test_2_1': 'yes'
    }
    app.save_assessment_results(second_responses, second_sub_responses)
    
    # 加载最近的评估结果
    loaded_responses, loaded_sub_responses = app.load_latest_assessment_results()
    
    # 验证加载的是最新的结果
    assert loaded_responses == second_responses, "加载的不是最新的responses数据"
    assert loaded_sub_responses == second_sub_responses, "加载的不是最新的sub_responses数据"
    

# 测试空数据库情况
def test_load_latest_from_empty_db(setup_test_database):
    """测试从空数据库加载结果
    
    测试场景：
    - 数据库中没有任何记录
    - 验证返回的是空字典
    """
    # 清空数据库
    with app.get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM assessment_results")
        conn.commit()
    
    # 加载结果
    responses, sub_responses = app.load_latest_assessment_results()
    
    # 验证返回的是空字典
    assert responses == {}, "空数据库应返回空的responses字典"
    assert sub_responses == {}, "空数据库应返回空的sub_responses字典"


if __name__ == "__main__":
    # 运行所有测试
    print("开始运行数据库操作模块单元测试...")
    
    # 手动设置测试环境
    try:
        # 清理可能存在的旧测试数据库
        if os.path.exists(TEST_DB_NAME):
            os.remove(TEST_DB_NAME)
        
        # 初始化测试数据库
        init_db()
        
        # 运行测试
        test_get_db_connection(None)
        print("✓ 数据库连接管理测试通过")
        
        test_init_db(None)
        print("✓ 数据库初始化测试通过")
        
        test_save_assessment_results(None)
        print("✓ 评估结果保存测试通过")
        
        test_load_latest_assessment_results(None)
        print("✓ 评估结果加载测试通过")
        
        test_load_latest_from_empty_db(None)
        print("✓ 空数据库加载测试通过")
        
        print("\n所有数据库操作模块测试通过！")
        
    finally:
        # 清理测试数据库
        if os.path.exists(TEST_DB_NAME):
            os.remove(TEST_DB_NAME)
