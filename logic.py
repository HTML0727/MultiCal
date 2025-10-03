#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
逻辑模块 - 处理计算器逻辑和数学计算
"""

import math
import re
import curses

class CalculatorLogic:
    def __init__(self):
        self.expression = ""
        self.result = ""
        self.history = []
        self.cursor_pos = 0
        self.mode = "标准"  # 模式: 标准, 编程, 逻辑门
        self.ui_state = {}  # UI状态存储
        
        # 定义按钮布局
        self.buttons = [
            ["7", "8", "9", "/", "sin(", "cos("],
            ["4", "5", "6", "*", "tan(", "sqrt("],
            ["1", "2", "3", "-", "log(", "exp("],
            ["0", ".", "π", "+", "(", ")"],
            ["=", "C", "Del", "Ans", "Help", "Quit"]
        ]
        
        # 逻辑门按钮布局
        self.logic_gate_buttons = [
            ["AND", "OR", "NOT", "XOR", "NAND", "NOR"],
            ["7", "8", "9", "/", "sin(", "cos("],
            ["4", "5", "6", "*", "tan(", "sqrt("],
            ["1", "2", "3", "-", "log(", "exp("],
            ["0", ".", "π", "+", "(", ")"],
            ["=", "C", "Del", "Ans", "Help", "Quit"]
        ]
    
    def handle_key(self, key, selected_row, selected_col):
        """处理按键事件"""
        if key == ord('q') or key == ord('Q'):
            return "QUIT"
        elif key == curses.KEY_UP:
            self.ui_state["selected_row"] = max(0, selected_row - 1)
            return "UPDATE_UI"
        elif key == curses.KEY_DOWN:
            self.ui_state["selected_row"] = min(len(self.buttons) - 1, selected_row + 1)
            return "UPDATE_UI"
        elif key == curses.KEY_LEFT:
            if selected_col > 0:
                self.ui_state["selected_col"] = selected_col - 1
            elif selected_row > 0:
                self.ui_state["selected_row"] = selected_row - 1
                self.ui_state["selected_col"] = len(self.buttons[selected_row - 1]) - 1
            return "UPDATE_UI"
        elif key == curses.KEY_RIGHT:
            if selected_col < len(self.buttons[selected_row]) - 1:
                self.ui_state["selected_col"] = selected_col + 1
            elif selected_row < len(self.buttons) - 1:
                self.ui_state["selected_row"] = selected_row + 1
                self.ui_state["selected_col"] = 0
            return "UPDATE_UI"
        elif key == curses.KEY_BACKSPACE or key == 127:
            if self.expression and self.cursor_pos > 0:
                self.expression = self.expression[:self.cursor_pos-1] + self.expression[self.cursor_pos:]
                self.cursor_pos -= 1
        elif key == curses.KEY_HOME:
            self.cursor_pos = 0
        elif key == curses.KEY_END:
            self.cursor_pos = len(self.expression)
        elif key == curses.KEY_LEFT and self.cursor_pos > 0:
            self.cursor_pos -= 1
        elif key == curses.KEY_RIGHT and self.cursor_pos < len(self.expression):
            self.cursor_pos += 1
        elif key == ord('\n') or key == ord(' '):
            buttons = self.logic_gate_buttons if self.mode == "逻辑门" else self.buttons
            button = buttons[selected_row][selected_col]
            return self.handle_button_click(button)
        elif key == ord('h') or key == ord('H'):
            return "SHOW_HELP"
        elif key == ord('j') or key == ord('J'):
            self.switch_mode()
        elif key == ord('c') or key == ord('C'):
            self.expression = ""
            self.cursor_pos = 0
            self.result = ""
        elif key >= ord(' ') and key <= ord('~'):
            char = chr(key)
            self.insert_text(char)
        
        return None
    
    def switch_mode(self):
        """切换计算模式"""
        modes = ["标准", "编程", "逻辑门"]
        current_index = modes.index(self.mode)
        self.mode = modes[(current_index + 1) % len(modes)]
    
    def insert_text(self, text):
        """在光标位置插入文本"""
        if self.cursor_pos == len(self.expression):
            self.expression += text
        else:
            self.expression = self.expression[:self.cursor_pos] + text + self.expression[self.cursor_pos:]
        self.cursor_pos += len(text)
    
    def handle_button_click(self, button):
        """处理按钮点击"""
        if button in "0123456789.+-*/π()":
            self.insert_text(button)
        elif button == "sin(":
            self.insert_text("sin()")
            self.cursor_pos -= 1  # 将光标移动到括号内
        elif button == "cos(":
            self.insert_text("cos()")
            self.cursor_pos -= 1
        elif button == "tan(":
            self.insert_text("tan()")
            self.cursor_pos -= 1
        elif button == "sqrt(":
            self.insert_text("sqrt()")
            self.cursor_pos -= 1
        elif button == "log(":
            self.insert_text("log()")
            self.cursor_pos -= 1
        elif button == "exp(":
            self.insert_text("exp()")
            self.cursor_pos -= 1
        elif button == "=":
            if self.expression.startswith("plot "):
                func_str = self.expression[5:]
                # 这里需要实现绘图功能
                pass
            else:
                self.result = self.evaluate_expression(self.expression)
        elif button == "C":
            self.expression = ""
            self.cursor_pos = 0
            self.result = ""
        elif button == "Del":
            if self.expression and self.cursor_pos > 0:
                self.expression = self.expression[:self.cursor_pos-1] + self.expression[self.cursor_pos:]
                self.cursor_pos -= 1
        elif button == "Ans":
            if self.result and not self.result.startswith("错误"):
                self.insert_text(self.result)
        elif button == "Help":
            return "SHOW_HELP"
        elif button == "Quit":
            return "QUIT"
        elif button in ["AND", "OR", "NOT", "XOR", "NAND", "NOR"]:
            self.handle_logic_gate(button)
        
        return None
    
    def handle_logic_gate(self, gate):
        """处理逻辑门操作"""
        # 这里实现逻辑门计算
        if gate == "NOT":
            self.insert_text("NOT(")
            self.cursor_pos -= 1
        else:
            self.insert_text(f"{gate}(")
            self.cursor_pos -= 1
    
    def safe_eval(self, expr, variables={}):
        """安全地评估数学表达式"""
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update(variables)
        allowed_names['π'] = math.pi
        allowed_names['pi'] = math.pi
        allowed_names['e'] = math.e
        allowed_names['E'] = math.e
        allowed_names['ans'] = self.result if self.result and self.result.replace('.', '').replace('-', '').isdigit() else 0

        # 替换函数为math等效函数
        expr = re.sub(r'sin\(', 'math.sin(', expr)
        expr = re.sub(r'cos\(', 'math.cos(', expr)
        expr = re.sub(r'tan\(', 'math.tan(', expr)
        expr = re.sub(r'sqrt\(', 'math.sqrt(', expr)
        expr = re.sub(r'log\(', 'math.log10(', expr)
        expr = re.sub(r'ln\(', 'math.log(', expr)
        expr = re.sub(r'exp\(', 'math.exp(', expr)

        try:
            code = compile(expr, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    raise NameError(f"使用 '{name}' 不被允许")
            return eval(code, {"__builtins__": {}}, allowed_names)
        except Exception as e:
            raise ValueError(f"评估表达式错误: {e}")
    
    def evaluate_expression(self, expr):
        """评估数学表达式"""
        try:
            # 移除任何多余的字符
            expr = expr.replace(' ', '')
            result = self.safe_eval(expr)
            # 将结果添加到历史记录
            self.history.append(f"{expr} = {result}")
            # 限制历史记录长度
            if len(self.history) > 10:
                self.history.pop(0)
            return str(result)
        except Exception as e:
            return "错误: " + str(e)