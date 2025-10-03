#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TUICalculator - 增强版终端计算器
具有现代化UI设计和丰富功能
"""

import curses
from calculator import TUICalculator

def main(stdscr):
    """主函数"""
    calculator = TUICalculator(stdscr)
    calculator.run()

if __name__ == "__main__":
    curses.wrapper(main)