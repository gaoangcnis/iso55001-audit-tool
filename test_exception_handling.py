import unittest
import logging
import io
import sys
from app import (
    AppError, DatabaseError, ConfigError, FileError, BusinessLogicError, ExportError,
    handle_errors, get_db_connection, init_session_state, create_pdf_report,
    get_translated_text, get_section_title, get_display_section_title, load_questionnaire, calculate_compliance_score
)

# 配置日志以捕获输出
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class TestExceptionHandling(unittest.TestCase):
    """测试统一异常处理机制"""
    
    def test_handle_errors_decorator(self):
        """测试handle_errors装饰器的基本功能"""
        
        @handle_errors(default_return_value="error_occurred", error_type=BusinessLogicError)
        def raise_error():
            raise ValueError("Test error")
        
        result = raise_error()
        self.assertEqual(result, "error_occurred")
    
    def test_handle_errors_decorator_raise_exception(self):
        """测试handle_errors装饰器是否能正确抛出指定类型的异常"""
        
        @handle_errors(error_type=DatabaseError)
        def raise_error():
            raise ValueError("Test error")
        
        with self.assertRaises(DatabaseError):
            raise_error()
    
    def test_get_translated_text_with_invalid_input(self):
        """测试get_translated_text函数在无效输入下的异常处理"""
        result = get_translated_text(None)
        self.assertEqual(result, '')
        
        result = get_translated_text(123)
        self.assertEqual(result, '')
    
    def test_get_display_section_title_with_invalid_input(self):
        """测试get_display_section_title函数在无效输入下的异常处理"""
        result = get_display_section_title(None)
        self.assertEqual(result, '**未知章节**')
        
        result = get_display_section_title({})
        self.assertEqual(result, '**未知章节**')
    
    def test_calculate_compliance_score_with_invalid_input(self):
        """测试calculate_compliance_score函数在无效输入下的异常处理"""
        # 无效的问题类型
        result = calculate_compliance_score(0, "INVALID_TYPE")
        self.assertEqual(result, 0)
        
        # None作为回答
        result = calculate_compliance_score(None, "XO")
        self.assertEqual(result, 0)

if __name__ == "__main__":
    unittest.main()
