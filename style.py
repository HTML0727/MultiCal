#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
样式模块 - 处理计算器样式和颜色
"""

import curses

class CalculatorStyle:
    def __init__(self):
        # 颜色定义
        self.colors = {
            'border': curses.COLOR_CYAN,
            'title': curses.COLOR_YELLOW,
            'expression': curses.COLOR_GREEN,
            'result': curses.COLOR_WHITE,
            'button': curses.COLOR_BLUE,
            'selected': curses.COLOR_RED,
            'history': curses.COLOR_MAGENTA,
            'error': curses.COLOR_RED
        }
        
        # 颜色对映射
        self.color_pairs = {
            'border': 1,
            'title': 2,
            'expression': 3,
            'result': 4,
            'button': 5,
            'selected': 6,
            'history': 7,
            'error': 8
        }