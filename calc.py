#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TUICalculator - 增强版终端计算器
具有现代化UI设计和丰富功能
"""

import curses
import math
import re
from datetime import datetime

class TUICalculator:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.expression = ""
        self.result = ""
        self.history = []
        self.selected_row = 0
        self.selected_col = 0
        self.cursor_pos = 0
        self.show_help = False
        self.theme = {
            'border': curses.COLOR_CYAN,
            'title': curses.COLOR_YELLOW,
            'expression': curses.COLOR_GREEN,
            'result': curses.COLOR_WHITE,
            'button': curses.COLOR_BLUE,
            'selected': curses.COLOR_RED,
            'history': curses.COLOR_MAGENTA,
            'error': curses.COLOR_RED
        }
        
        # 初始化颜色
        curses.start_color()
        curses.use_default_colors()
        for i, color in enumerate(self.theme.values(), 1):
            curses.init_pair(i, color, -1)
        
        self.buttons = [
            ["7", "8", "9", "/", "sin(", "cos("],
            ["4", "5", "6", "*", "tan(", "sqrt("],
            ["1", "2", "3", "-", "log(", "exp("],
            ["0", ".", "π", "+", "(", ")"],
            ["=", "C", "Del", "Ans", "Help", "Quit"]
        ]
        
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
        allowed_names['ans'] = self.result if self.result and self.result.replace('.', '').isdigit() else 0

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

    def draw_border(self):
        """绘制边框"""
        height, width = self.stdscr.getmaxyx()
        
        # 绘制外边框
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.border(0)
        self.stdscr.attroff(curses.color_pair(1))
        
        # 绘制标题栏
        title = " TUICalculator - 增强版终端计算器 "
        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(0, (width - len(title)) // 2, title)
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        
        # 绘制底部状态栏
        status = " 按 'h' 显示帮助 | 按 'q' 退出 "
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(height-1, (width - len(status)) // 2, status)
        self.stdscr.attroff(curses.color_pair(1))

    def draw_display(self):
        """绘制显示区域"""
        height, width = self.stdscr.getmaxyx()
        
        # 绘制显示区域边框
        display_height = 4
        display_width = width - 6
        
        # 上边框
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addch(2, 2, curses.ACS_ULCORNER)
        self.stdscr.addch(2, width-3, curses.ACS_URCORNER)
        for x in range(3, width-3):
            self.stdscr.addch(2, x, curses.ACS_HLINE)
        
        # 下边框
        self.stdscr.addch(2+display_height, 2, curses.ACS_LLCORNER)
        self.stdscr.addch(2+display_height, width-3, curses.ACS_LRCORNER)
        for x in range(3, width-3):
            self.stdscr.addch(2+display_height, x, curses.ACS_HLINE)
        
        # 侧边框
        for y in range(3, 2+display_height):
            self.stdscr.addch(y, 2, curses.ACS_VLINE)
            self.stdscr.addch(y, width-3, curses.ACS_VLINE)
        
        # 表达式显示
        expr_display = self.expression[:display_width-2]
        self.stdscr.attron(curses.color_pair(3))
        self.stdscr.addstr(3, 3, "表达式: " + expr_display)
        
        # 光标位置
        if self.cursor_pos < len(expr_display):
            cursor_x = 3 + 8 + self.cursor_pos
            if cursor_x < width - 4:
                self.stdscr.move(3, cursor_x)
        
        # 结果显示
        result_display = self.result[:display_width-2]
        self.stdscr.attron(curses.color_pair(4))
        self.stdscr.addstr(4, 3, "结果:   " + result_display)
        self.stdscr.attroff(curses.color_pair(4))

    def draw_buttons(self):
        """绘制按钮"""
        height, width = self.stdscr.getmaxyx()
        start_y = 8
        
        for i, row in enumerate(self.buttons):
            start_x = (width - (len(row) * 8 - 1)) // 2
            for j, button in enumerate(row):
                # 绘制按钮边框
                btn_x = start_x + j * 8
                btn_text = f" {button} "
                
                if i == self.selected_row and j == self.selected_col:
                    # 选中的按钮
                    self.stdscr.attron(curses.color_pair(5) | curses.A_REVERSE)
                    self.stdscr.addstr(start_y + i*2, btn_x, "╭" + "─"*(len(btn_text)) + "╮")
                    self.stdscr.addstr(start_y + i*2 + 1, btn_x, "│" + btn_text + "│")
                    self.stdscr.addstr(start_y + i*2 + 2, btn_x, "╰" + "─"*(len(btn_text)) + "╯")
                    self.stdscr.attroff(curses.color_pair(5) | curses.A_REVERSE)
                else:
                    # 未选中的按钮
                    self.stdscr.attron(curses.color_pair(6))
                    self.stdscr.addstr(start_y + i*2, btn_x, "╭" + "─"*(len(btn_text)) + "╮")
                    self.stdscr.addstr(start_y + i*2 + 1, btn_x, "│" + btn_text + "│")
                    self.stdscr.addstr(start_y + i*2 + 2, btn_x, "╰" + "─"*(len(btn_text)) + "╯")
                    self.stdscr.attroff(curses.color_pair(6))

    def draw_history(self):
        """绘制历史记录"""
        height, width = self.stdscr.getmaxyx()
        
        # 绘制历史记录区域
        history_start_y = 8 + len(self.buttons) * 2 + 2
        history_height = height - history_start_y - 2
        
        if history_height < 3:
            return  # 没有足够的空间显示历史记录
        
        # 历史记录标题
        title = "历史记录"
        self.stdscr.attron(curses.color_pair(7) | curses.A_BOLD)
        self.stdscr.addstr(history_start_y, 4, title)
        self.stdscr.attroff(curses.color_pair(7) | curses.A_BOLD)
        
        # 历史记录内容
        for i, item in enumerate(self.history[-history_height+1:]):
            if i < history_height - 1:
                self.stdscr.addstr(history_start_y + i + 1, 4, item)

    def draw_help(self):
        """绘制帮助信息"""
        height, width = self.stdscr.getmaxyx()
        
        # 创建帮助窗口
        help_height, help_width = 16, 60
        help_y = (height - help_height) // 2
        help_x = (width - help_width) // 2
        
        # 绘制帮助窗口边框
        self.stdscr.attron(curses.color_pair(1))
        for y in range(help_y, help_y + help_height):
            for x in range(help_x, help_x + help_width):
                if y == help_y or y == help_y + help_height - 1:
                    self.stdscr.addch(y, x, curses.ACS_HLINE)
                elif x == help_x or x == help_x + help_width - 1:
                    self.stdscr.addch(y, x, curses.ACS_VLINE)
        
        # 绘制窗口角落
        self.stdscr.addch(help_y, help_x, curses.ACS_ULCORNER)
        self.stdscr.addch(help_y, help_x + help_width - 1, curses.ACS_URCORNER)
        self.stdscr.addch(help_y + help_height - 1, help_x, curses.ACS_LLCORNER)
        self.stdscr.addch(help_y + help_height - 1, help_x + help_width - 1, curses.ACS_LRCORNER)
        
        # 帮助标题
        title = "帮助信息"
        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(help_y, help_x + (help_width - len(title)) // 2, title)
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        
        # 帮助内容
        help_texts = [
            "方向键: 导航按钮",
            "回车/空格: 选择按钮",
            "数字键: 直接输入数字",
            "运算符: 直接输入 + - * /",
            "退格键: 删除上一个字符",
            "Esc: 清除表达式",
            "h: 显示/隐藏帮助",
            "q: 退出计算器"
        ]
        
        for i, text in enumerate(help_texts):
            self.stdscr.addstr(help_y + 2 + i, help_x + 2, text)
        
        # 关闭帮助提示
        close_help = "按任意键关闭帮助"
        self.stdscr.addstr(help_y + help_height - 2, help_x + (help_width - len(close_help)) // 2, close_help)

    def draw(self):
        """绘制整个界面"""
        self.stdscr.clear()
        self.draw_border()
        
        if self.show_help:
            self.draw_help()
        else:
            self.draw_display()
            self.draw_buttons()
            self.draw_history()
        
        self.stdscr.refresh()

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
                self.plot_function(func_str)
            else:
                self.result = self.evaluate_expression(self.expression)
        elif button == "C":
            self.expression = ""
            self.cursor_pos = 0
        elif button == "Del":
            if self.expression and self.cursor_pos > 0:
                self.expression = self.expression[:self.cursor_pos-1] + self.expression[self.cursor_pos:]
                self.cursor_pos -= 1
        elif button == "Ans":
            if self.result and not self.result.startswith("错误"):
                self.insert_text(self.result)
        elif button == "Help":
            self.show_help = not self.show_help
        elif button == "Quit":
            return False
        
        return True

    def plot_function(self, func_str):
        """绘制函数图像"""
        try:
            self.stdscr.clear()
            height, width = self.stdscr.getmaxyx()

            title = "函数图像: " + func_str
            self.stdscr.addstr(1, (width - len(title)) // 2, title)

            # 坐标轴
            for x in range(2, width - 2):
                self.stdscr.addstr(height // 2, x, "─")
            for y in range(2, height - 2):
                self.stdscr.addstr(y, width // 2, "│")

            # 原点标记
            self.stdscr.addstr(height // 2, width // 2, "┼")

            # 绘制函数图像
            for x in range(2, width - 2):
                math_x = (x - width // 2) / 5.0
                try:
                    y_val = self.safe_eval(func_str, {'x': math_x})
                    screen_y = int(height // 2 - y_val * 5)
                    if 2 <= screen_y < height - 2:
                        self.stdscr.addstr(screen_y, x, "•")
                except:
                    pass

            self.stdscr.refresh()
            self.stdscr.getch()
        except Exception as e:
            self.stdscr.clear()
            self.stdscr.addstr(1, 1, "绘制函数图像错误: " + str(e))
            self.stdscr.refresh()
            self.stdscr.getch()

    def run(self):
        """运行计算器主循环"""
        curses.curs_set(1)  # 显示光标
        self.draw()

        while True:
            key = self.stdscr.getch()

            if self.show_help:
                self.show_help = False
                self.draw()
                continue

            if key == ord('q') or key == ord('Q'):
                break
            elif key == curses.KEY_UP:
                self.selected_row = max(0, self.selected_row - 1)
            elif key == curses.KEY_DOWN:
                self.selected_row = min(len(self.buttons) - 1, self.selected_row + 1)
            elif key == curses.KEY_LEFT:
                if self.selected_col > 0:
                    self.selected_col -= 1
                elif self.selected_row > 0:
                    self.selected_row -= 1
                    self.selected_col = len(self.buttons[self.selected_row]) - 1
            elif key == curses.KEY_RIGHT:
                if self.selected_col < len(self.buttons[self.selected_row]) - 1:
                    self.selected_col += 1
                elif self.selected_row < len(self.buttons) - 1:
                    self.selected_row += 1
                    self.selected_col = 0
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
                button = self.buttons[self.selected_row][self.selected_col]
                if not self.handle_button_click(button):
                    break
            elif key == ord('h') or key == ord('H'):
                self.show_help = True
            elif key == ord('c') or key == ord('C'):
                self.expression = ""
                self.cursor_pos = 0
            elif key >= ord(' ') and key <= ord('~'):
                char = chr(key)
                self.insert_text(char)

            self.draw()

def main(stdscr):
    """主函数"""
    calculator = TUICalculator(stdscr)
    calculator.run()

if __name__ == "__main__":
    curses.wrapper(main)