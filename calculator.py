#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TUICalculator - 计算器主类
"""
import math
import curses
from ui import CalculatorUI
from logic import CalculatorLogic

class TUICalculator:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.ui = CalculatorUI(stdscr)
        self.logic = CalculatorLogic()
        self.show_help = False
        
    def run(self):
        """运行计算器主循环"""
        curses.curs_set(1)  # 显示光标
        self.ui.draw(self.logic.expression, self.logic.result, 
                    self.logic.history, self.ui.selected_row, 
                    self.ui.selected_col, self.logic.cursor_pos, 
                    self.show_help, self.logic.mode)

        while True:
            try:
                key = self.stdscr.getch()
            except:
                continue

            if self.show_help:
                self.show_help = False
                self.ui.draw(self.logic.expression, self.logic.result, 
                            self.logic.history, self.ui.selected_row, 
                            self.ui.selected_col, self.logic.cursor_pos, 
                            self.show_help, self.logic.mode)
                continue

            # 处理按键
            result = self.logic.handle_key(key, self.ui.selected_row, self.ui.selected_col)
            
            if result == "SHOW_HELP":
                self.show_help = True
            elif result == "QUIT":
                break
            elif result == "UPDATE_UI":
                # 更新UI选择状态
                if "selected_row" in self.logic.ui_state:
                    self.ui.selected_row = self.logic.ui_state["selected_row"]
                if "selected_col" in self.logic.ui_state:
                    self.ui.selected_col = self.logic.ui_state["selected_col"]
            
            # 绘制UI
            self.ui.draw(self.logic.expression, self.logic.result, 
                        self.logic.history, self.ui.selected_row, 
                        self.ui.selected_col, self.logic.cursor_pos, 
                        self.show_help, self.logic.mode)