#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UI模块 - 处理计算器界面绘制
"""

import curses
from style import CalculatorStyle

class CalculatorUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.style = CalculatorStyle()
        self.selected_row = 0
        self.selected_col = 0
        
        # 初始化颜色
        curses.start_color()
        curses.use_default_colors()
        for i, color in enumerate(self.style.colors.values(), 1):
            curses.init_pair(i, color, -1)
        
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
            ["7", "8", "9", " / ", "sin(", "cos("],
            ["4", "5", "6", " * ", "tan(", "sqrt("],
            ["1", "2", "3", " - ", "log(", "exp("],
            ["0", ".", "π", " + ", "(", ")"],
            ["=", "C", "Del", "Ans", "Help", "Quit"]
        ]
        
    def draw(self, expression, result, history, selected_row, selected_col, cursor_pos, show_help, mode):
        """绘制整个界面"""
        self.stdscr.clear()
        self.selected_row = selected_row
        self.selected_col = selected_col
        
        if not self.draw_border():
            return
            
        if show_help:
            self.draw_help()
        else:
            self.draw_display(expression, result, cursor_pos, mode)
            self.draw_buttons(mode)
            self.draw_history(history)
        
        self.stdscr.refresh()
    
    def draw_border(self):
        """绘制边框"""
        height, width = self.stdscr.getmaxyx()
        
        # 检查窗口大小是否足够
        if height < 20 or width < 60:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, "窗口太小，请调整终端大小")
            self.stdscr.refresh()
            return False
            
        # 绘制外边框
        self.stdscr.attron(curses.color_pair(self.style.color_pairs['border']))
        self.stdscr.border(0)
        self.stdscr.attroff(curses.color_pair(self.style.color_pairs['border']))
        
        # 绘制标题栏
        title = " TUICalculator - 增强版终端计算器 "
        title_x = max(1, (width - len(title)) // 2)
        self.stdscr.attron(curses.color_pair(self.style.color_pairs['title']) | curses.A_BOLD)
        self.stdscr.addstr(0, title_x, title)
        self.stdscr.attroff(curses.color_pair(self.style.color_pairs['title']) | curses.A_BOLD)
        
        # 绘制底部状态栏
        status = "| 按 'h' 显示帮助 | 按 'q' 退出 | 按 'j' 切换模式 | "
        status_x = max(1, (width - len(status)) // 2)
        self.stdscr.attron(curses.color_pair(self.style.color_pairs['border']))
        self.stdscr.addstr(height-1, status_x, status)
        self.stdscr.attroff(curses.color_pair(self.style.color_pairs['border']))
        
        return True
    
    def draw_display(self, expression, result, cursor_pos, mode):
        """绘制显示区域"""
        height, width = self.stdscr.getmaxyx()
        
        # 检查窗口大小是否足够
        if height < 20 or width < 60:
            return
            
        # 绘制模式指示器
        mode_text = f"模式: {mode}"
        self.stdscr.attron(curses.color_pair(self.style.color_pairs['title']))
        self.stdscr.addstr(1, 2, mode_text)
        self.stdscr.attroff(curses.color_pair(self.style.color_pairs['title']))
        
        # 绘制显示区域边框
        display_height = 4
        display_width = width - 6
        
        # 上边框
        self.stdscr.attron(curses.color_pair(self.style.color_pairs['border']))
        self.stdscr.addch(2, 2, curses.ACS_ULCORNER)
        self.stdscr.addch(2, min(width-3, width-1), curses.ACS_URCORNER)
        for x in range(3, min(width-3, width)):
            self.stdscr.addch(2, x, curses.ACS_HLINE)
        
        # 下边框
        self.stdscr.addch(2+display_height, 2, curses.ACS_LLCORNER)
        self.stdscr.addch(2+display_height, min(width-3, width-1), curses.ACS_LRCORNER)
        for x in range(3, min(width-3, width)):
            self.stdscr.addch(2+display_height, x, curses.ACS_HLINE)
        
        # 侧边框
        for y in range(3, min(2+display_height, height)):
            self.stdscr.addch(y, 2, curses.ACS_VLINE)
            self.stdscr.addch(y, min(width-3, width-1), curses.ACS_VLINE)
        
        # 表达式显示
        expr_display = expression[:display_width-10]  # 保留一些空间给"表达式: "前缀
        self.stdscr.attron(curses.color_pair(self.style.color_pairs['expression']))
        self.stdscr.addstr(3, 3, "表达式: " + expr_display)
        
        # 光标位置
        if cursor_pos < len(expr_display):
            cursor_x = 3 + 8 + min(cursor_pos, width-12)
            if cursor_x < width - 4:
                try:
                    self.stdscr.move(3, cursor_x)
                except:
                    pass
        
        # 结果显示
        result_display = result[:display_width-8]  # 保留一些空间给"结果: "前缀
        self.stdscr.attron(curses.color_pair(self.style.color_pairs['result']))
        self.stdscr.addstr(4, 3, "结果:   " + result_display)
        self.stdscr.attroff(curses.color_pair(self.style.color_pairs['result']))
    
    def draw_buttons(self, mode):
        """绘制按钮"""
        height, width = self.stdscr.getmaxyx()
        
        # 检查窗口大小是否足够
        if height < 20 or width < 60:
            return
            
        # 根据模式选择按钮布局
        buttons = self.logic_gate_buttons if mode == "逻辑门" else self.buttons
        start_y = 8
        
        for i, row in enumerate(buttons):
            start_x = max(2, (width - (len(row) * 8 - 1)) // 2)
            for j, button in enumerate(row):
                # 绘制按钮边框
                btn_x = start_x + j * 8
                btn_text = f" {button} "
                
                # 检查按钮是否在屏幕内
                if btn_x + len(btn_text) + 2 >= width or start_y + i*2 + 2 >= height:
                    continue
                
                if i == self.selected_row and j == self.selected_col:
                    # 选中的按钮
                    self.stdscr.attron(curses.color_pair(self.style.color_pairs['selected']) | curses.A_REVERSE)
                    try:
                        self.stdscr.addstr(start_y + i*2, btn_x, "╭" + "─"*(len(btn_text)) + "╮")
                        self.stdscr.addstr(start_y + i*2 + 1, btn_x, "│" + btn_text + "│")
                        self.stdscr.addstr(start_y + i*2 + 2, btn_x, "╰" + "─"*(len(btn_text)) + "╯")
                    except:
                        pass
                    self.stdscr.attroff(curses.color_pair(self.style.color_pairs['selected']) | curses.A_REVERSE)
                else:
                    # 未选中的按钮
                    self.stdscr.attron(curses.color_pair(self.style.color_pairs['button']))
                    try:
                        self.stdscr.addstr(start_y + i*2, btn_x, "╭" + "─"*(len(btn_text)) + "╮")
                        self.stdscr.addstr(start_y + i*2 + 1, btn_x, "│" + btn_text + "│")
                        self.stdscr.addstr(start_y + i*2 + 2, btn_x, "╰" + "─"*(len(btn_text)) + "╯")
                    except:
                        pass
                    self.stdscr.attroff(curses.color_pair(self.style.color_pairs['button']))
    
    def draw_history(self, history):
        """绘制历史记录"""
        height, width = self.stdscr.getmaxyx()
        
        # 检查窗口大小是否足够
        if height < 25 or width < 60:
            return
            
        # 绘制历史记录区域
        history_start_y = 8 + len(self.buttons) * 2 + 2
        history_height = height - history_start_y - 2
        
        if history_height < 3:
            return  # 没有足够的空间显示历史记录
        
        # 历史记录标题
        title = "历史记录"
        self.stdscr.attron(curses.color_pair(self.style.color_pairs['history']) | curses.A_BOLD)
        try:
            self.stdscr.addstr(history_start_y, 4, title)
        except:
            pass
        self.stdscr.attroff(curses.color_pair(self.style.color_pairs['history']) | curses.A_BOLD)
        
        # 历史记录内容
        for i, item in enumerate(history[-history_height+1:]):
            if i < history_height - 1:
                try:
                    self.stdscr.addstr(history_start_y + i + 1, 4, item[:width-8])
                except:
                    pass
    
    def draw_help(self):
        """绘制帮助信息"""
        height, width = self.stdscr.getmaxyx()
        
        # 检查窗口大小是否足够
        if height < 20 or width < 60:
            return
            
        # 创建帮助窗口
        help_height, help_width = min(16, height-4), min(60, width-4)
        help_y = (height - help_height) // 2
        help_x = (width - help_width) // 2
        
        # 绘制帮助窗口边框
        self.stdscr.attron(curses.color_pair(self.style.color_pairs['border']))
        for y in range(help_y, help_y + help_height):
            for x in range(help_x, help_x + help_width):
                if y == help_y or y == help_y + help_height - 1:
                    try:
                        self.stdscr.addch(y, x, curses.ACS_HLINE)
                    except:
                        pass
                elif x == help_x or x == help_x + help_width - 1:
                    try:
                        self.stdscr.addch(y, x, curses.ACS_VLINE)
                    except:
                        pass
        
        # 绘制窗口角落
        try:
            self.stdscr.addch(help_y, help_x, curses.ACS_ULCORNER)
            self.stdscr.addch(help_y, help_x + help_width - 1, curses.ACS_URCORNER)
            self.stdscr.addch(help_y + help_height - 1, help_x, curses.ACS_LLCORNER)
            self.stdscr.addch(help_y + help_height - 1, help_x + help_width - 1, curses.ACS_LRCORNER)
        except:
            pass
        
        # 帮助标题
        title = "帮助信息"
        self.stdscr.attron(curses.color_pair(self.style.color_pairs['title']) | curses.A_BOLD)
        try:
            self.stdscr.addstr(help_y, help_x + (help_width - len(title)) // 2, title)
        except:
            pass
        self.stdscr.attroff(curses.color_pair(self.style.color_pairs['title']) | curses.A_BOLD)
        
        # 帮助内容
        help_texts = [
            "方向键: 导航按钮",
            "回车/空格: 选择按钮",
            "数字键: 直接输入数字",
            "运算符: 直接输入 + - * /",
            "退格键: 删除上一个字符",
            "Esc: 清除表达式",
            "h: 显示/隐藏帮助",
            "j: 切换计算模式",
            "q: 退出计算器",
            "--------------------------------",
            "Nekosparry浪费了114514秒打造"
        ]
        
        for i, text in enumerate(help_texts):
            if help_y + 2 + i < height - 1:
                try:
                    self.stdscr.addstr(help_y + 2 + i, help_x + 2, text[:help_width-4])
                except:
                    pass
        
        # 关闭帮助提示
        close_help = "按任意键关闭帮助"
        try:
            self.stdscr.addstr(help_y + help_height - 2, help_x + (help_width - len(close_help)) // 2, close_help)
        except:
            pass