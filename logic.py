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
        self.mode = "标准"  # 模式: 标准, 编程, 逻辑门, 正则表达式, 进制换算
        self.ui_state = {}  # UI状态存储
        
        # 定义按钮布局
        self.buttons = [
            ["7", "8", "9", "/", "sin(", "cos(", "∫"],
            ["4", "5", "6", "*", "tan(", "sqrt(", "∂"],
            ["1", "2", "3", "-", "log(", "exp(", "dx"],
            ["0", ".", "π", "+", "(", ")", "dy"],
            ["=", "C", "Del", "Ans", "Help", "Quit"]
        ]
        
        # 编程按钮布局
        self.codingbuttons = [
            ["0", "1"],
            ["/", " * "],
            ["-", "+"],
            ["=",]
        ]

        # 逻辑门按钮布局
        self.logic_gate_buttons = [
            ["AND", "OR", "NOT", "XOR", "NAND", "NOR"],
            ["Truth", "Table", "Show", "0", "1", "Calc"],
            ["7", "8", "9", "/", "sin(", "cos("],
            ["4", "5", "6", "*", "tan(", "sqrt("],
            ["1", "2", "3", "-", "log(", "exp("],
            ["0", ".", "π", "+", "(", ")"],
            ["=", "C", "Del", "Ans", "Help", "Quit"]
        ]

        # 进制换算按钮布局
        self.base_conversion_buttons = [
            ["BIN", "OCT", "DEC", "HEX", "CONV", "SWAP"],
            ["7", "8", "9", "A", "B", "C"],
            ["4", "5", "6", "D", "E", "F"],
            ["1", "2", "3", "CLR", "Help", "Quit"],
            ["0", ".", "=", "Ans", "Mode", "Back"]
        ]

        # 正则表达式按钮布局
        self.regex_buttons = [
            ["match", "search", "findall", "sub", "split", "compile"],
            ["^", "$", "*", "+", "?", "."],
            ["[", "]", "(", ")", "{", "}"],
            ["|", "\\", "w", "d", "s", "b"],
            ["CLR", "Test", "=", "Ans", "Help", "Quit"]
        ]
    
    def handle_key(self, key, selected_row, selected_col):
        """处理按键事件"""
        if key == ord('q') or key == ord('Q'):
            return "QUIT"
        elif key == curses.KEY_UP:
            self.ui_state["selected_row"] = max(0, selected_row - 1)
            return "UPDATE_UI"
        elif key == curses.KEY_DOWN:
            # 根据模式选择正确的按钮布局长度
            if self.mode == "编程":
                max_row = len(self.codingbuttons) - 1
            elif self.mode == "逻辑门":
                max_row = len(self.logic_gate_buttons) - 1
            elif self.mode == "进制换算":
                max_row = len(self.base_conversion_buttons) - 1
            elif self.mode == "正则表达式":
                max_row = len(self.regex_buttons) - 1
            else:
                max_row = len(self.buttons) - 1
            self.ui_state["selected_row"] = min(max_row, selected_row + 1)
            return "UPDATE_UI"
        elif key == curses.KEY_LEFT:
            # 根据模式选择正确的按钮布局
            if self.mode == "编程":
                buttons = self.codingbuttons
            elif self.mode == "逻辑门":
                buttons = self.logic_gate_buttons
            elif self.mode == "进制换算":
                buttons = self.base_conversion_buttons
            elif self.mode == "正则表达式":
                buttons = self.regex_buttons
            else:
                buttons = self.buttons

            if selected_col > 0:
                self.ui_state["selected_col"] = selected_col - 1
            elif selected_row > 0:
                self.ui_state["selected_row"] = selected_row - 1
                self.ui_state["selected_col"] = len(buttons[selected_row - 1]) - 1
            return "UPDATE_UI"
        elif key == curses.KEY_RIGHT:
            # 根据模式选择正确的按钮布局
            if self.mode == "编程":
                buttons = self.codingbuttons
            elif self.mode == "逻辑门":
                buttons = self.logic_gate_buttons
            elif self.mode == "进制换算":
                buttons = self.base_conversion_buttons
            elif self.mode == "正则表达式":
                buttons = self.regex_buttons
            else:
                buttons = self.buttons

            if selected_col < len(buttons[selected_row]) - 1:
                self.ui_state["selected_col"] = selected_col + 1
            elif selected_row < len(buttons) - 1:
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
            if self.mode == "逻辑门":
                buttons = self.logic_gate_buttons
            elif self.mode == "进制换算":
                buttons = self.base_conversion_buttons
            elif self.mode == "正则表达式":
                buttons = self.regex_buttons
            else:
                buttons = self.buttons
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
        modes = ["标准", "编程", "逻辑门", "正则表达式", "进制换算"]
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
        elif button == "∫":
            self.insert_text("∫")
        elif button == "∂":
            self.insert_text("∂")
        elif button == "dx":
            self.insert_text("dx")
        elif button == "dy":
            self.insert_text("dy")
        elif button == "=":
            if self.expression.startswith("plot "):
                func_str = self.expression[5:]
                # 这里需要实现绘图功能
                pass
            elif self.mode == "逻辑门":
                self.result = self.evaluate_logic_gate(self.expression)
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
        elif button == "Truth":
            self.show_truth_table()
        elif button == "Table":
            self.show_truth_table()
        elif button == "Show":
            self.show_truth_table()
        elif button in ["BIN", "OCT", "DEC", "HEX"]:
            self.handle_base_conversion(button)
        elif button == "CONV":
            self.convert_base()
        elif button == "SWAP":
            self.swap_bases()
        elif button in ["match", "search", "findall", "sub", "split", "compile"]:
            self.handle_regex_function(button)
        elif button in ["^", "$", "*", "+", "?", ".", "[", "]", "(", ")", "{", "}", "|", "\\"]:
            self.insert_text(f"\\{button}" if button in ".^$*+?{}[]()|" else button)
        elif button in ["w", "d", "s", "b"]:
            self.insert_text(f"\\{button}")
        elif button == "Test":
            self.test_regex()
        
        return None
    
    def handle_logic_gate(self, gate):
        """处理逻辑门操作"""
        if gate == "NOT":
            self.insert_text("NOT(")
            self.cursor_pos -= 1
        else:
            self.insert_text(f"{gate}(")
            self.cursor_pos -= 1

    def evaluate_logic_gate(self, expression):
        """评估逻辑门表达式"""
        try:
            # 解析逻辑表达式，支持AND, OR, NOT, XOR, NAND, NOR
            # 简单的实现：将二进制数字转换为逻辑运算

            # 提取数字参数
            import re
            numbers = re.findall(r'\d+', expression)

            if not numbers:
                return "错误: 请输入二进制数字"

            # 转换为整数
            nums = [int(x, 2) for x in numbers]

            if "NOT" in expression and len(nums) >= 1:
                result = ~nums[0] & 1  # 按位取反并只取最低位
                return f"NOT({numbers[0]}) = {bin(result)[2:]}"
            elif "NAND" in expression and len(nums) >= 2:
                result = 1 - (nums[0] & nums[1])  # NAND逻辑
                return f"{numbers[0]} NAND {numbers[1]} = {bin(result)[2:]}"
            elif "NOR" in expression and len(nums) >= 2:
                result = 1 - (nums[0] | nums[1])  # NOR逻辑
                return f"{numbers[0]} NOR {numbers[1]} = {bin(result)[2:]}"
            elif "XOR" in expression and len(nums) >= 2:
                result = nums[0] ^ nums[1]
                return f"{numbers[0]} XOR {numbers[1]} = {bin(result)[2:]}"
            elif "AND" in expression and len(nums) >= 2:
                result = nums[0] & nums[1]
                return f"{numbers[0]} AND {numbers[1]} = {bin(result)[2:]}"
            elif "OR" in expression and len(nums) >= 2:
                result = nums[0] | nums[1]
                return f"{numbers[0]} OR {numbers[1]} = {bin(result)[2:]}"

            return "错误: 不支持的逻辑门操作"
        except Exception as e:
            return f"逻辑门计算错误: {str(e)}"

    def show_truth_table(self):
        """显示逻辑门真值表"""
        table = "逻辑门真值表:\nA B | AND OR XOR NAND NOR\n0 0 |  0   0   0    1    1\n0 1 |  0   1   1    1    0\n1 0 |  0   1   1    1    0\n1 1 |  1   1   0    0    0\n\nNOT: 0->1, 1->0"
        self.result = table
        self.history.append(f"真值表 = {table}")

    def handle_base_conversion(self, base):
        """处理进制选择"""
        base_map = {"BIN": 2, "OCT": 8, "DEC": 10, "HEX": 16}
        self.current_base = base_map[base]
        self.insert_text(f"{base}:")

    def convert_base(self):
        """执行进制转换"""
        try:
            # 解析表达式中的进制信息
            parts = self.expression.split(":")
            if len(parts) == 2:
                base_part, num_part = parts
                base = int(base_part) if base_part.isdigit() else self.current_base
                number = num_part.strip()

                # 转换为十进制
                if base == 16:
                    decimal = int(number, 16)
                elif base == 8:
                    decimal = int(number, 8)
                elif base == 2:
                    decimal = int(number, 2)
                else:
                    decimal = int(number, 10)

                # 显示所有进制
                result = f"DEC: {decimal}, HEX: {hex(decimal)[2:].upper()}, OCT: {oct(decimal)[2:]}, BIN: {bin(decimal)[2:]}"
                self.result = result
                self.history.append(f"{self.expression} = {result}")
            else:
                self.result = "错误: 请输入正确的进制格式，如 '16:FF'"
        except Exception as e:
            self.result = f"错误: {str(e)}"

    def swap_bases(self):
        """交换进制位置"""
        if ":" in self.expression:
            parts = self.expression.split(":")
            if len(parts) == 2:
                self.expression = f"{parts[1]}:{parts[0]}"

    def handle_regex_function(self, func):
        """处理正则表达式函数"""
        if func == "compile":
            self.insert_text("re.compile()")
            self.cursor_pos -= 1
        else:
            self.insert_text(f"re.{func}()")
            self.cursor_pos -= 1

    def test_regex(self):
        """测试正则表达式"""
        try:
            # 解析表达式，期望格式如: pattern,text
            if "," in self.expression:
                pattern, text = self.expression.split(",", 1)
                pattern = pattern.strip()
                text = text.strip()

                # 编译正则表达式
                regex = re.compile(pattern)
                matches = regex.findall(text)

                if matches:
                    result = f"找到 {len(matches)} 个匹配: {matches[:5]}"  # 只显示前5个
                    if len(matches) > 5:
                        result += f" ... (还有 {len(matches) - 5} 个)"
                else:
                    result = "未找到匹配"

                self.result = result
                self.history.append(f"regex: {self.expression} = {result}")
            else:
                self.result = "错误: 请使用格式 'pattern,text'"
        except Exception as e:
            self.result = f"正则表达式错误: {str(e)}"
    
    def safe_eval(self, expr, variables={}):
        """安全地评估数学表达式"""
        import math
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

        # 处理幂运算
        expr = re.sub(r'\^', '**', expr)

        try:
            code = compile(expr, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names and name != 'math':
                    raise NameError(f"使用 '{name}' 不被允许")
            return eval(code, {"__builtins__": {}, "math": math}, allowed_names)
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
