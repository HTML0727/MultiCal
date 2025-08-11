#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TUICalculator - A Simple Terminal Calculator
"""

import curses
import math
import re


def safe_eval(expr, variables={}):
    """Safely evaluate a mathematical expression with optional variables."""
    allowed_names = {
        k: v for k, v in math.__dict__.items() if not k.startswith("__")
    }
    allowed_names.update(variables)
    allowed_names['E'] = math.e

    # Replace functions with math equivalents
    expr = re.sub(r'sin\(', 'math.sin(', expr)
    expr = re.sub(r'cos\(', 'math.cos(', expr)
    expr = re.sub(r'tan\(', 'math.tan(', expr)
    expr = re.sub(r'sqrt\(', 'math.sqrt(', expr)
    expr = re.sub(r'log\(', 'math.log10(', expr)
    expr = re.sub(r'ln\(', 'math.log(', expr)
    expr = re.sub(r'exp\(', 'math.exp(', expr)

    try:
        # 使用 compile 和限制的命名空间进行 eval
        code = compile(expr, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"Use of '{name}' not allowed")
        return eval(code, {"__builtins__": {}}, allowed_names)
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}")


def evaluate_expression(expr):
    """Evaluate mathematical expression with support for advanced functions."""
    try:
        result = safe_eval(expr)
        return str(result)
    except Exception as e:
        return "Error: " + str(e)


def plot_function(stdscr, func_str):
    """Plot a function in text mode."""
    try:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = "Function Plot: " + func_str
        stdscr.addstr(1, (width - len(title)) // 2, title)

        # Axes
        for x in range(2, width - 2):
            stdscr.addstr(height // 2, x, "-")
        for y in range(2, height - 2):
            stdscr.addstr(y, width // 2, "|")

        # Plot points
        for x in range(2, width - 2):
            math_x = (x - width // 2) / 2.0
            try:
                y_val = safe_eval(func_str, {'x': math_x})
                screen_y = int(height // 2 - y_val * 2)
                if 2 <= screen_y < height - 2:
                    stdscr.addstr(screen_y, x, "*")
            except:
                pass

        stdscr.refresh()
        stdscr.getch()
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(1, 1, "Error plotting function: " + str(e))
        stdscr.refresh()
        stdscr.getch()


def draw_calculator(stdscr, expression, result, selected_row=0, selected_col=0):
    """Draw the calculator interface."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    title = "Terminal Calculator"
    stdscr.addstr(1, (width - len(title)) // 2, title)

    stdscr.addstr(3, 2, "Expression: " + expression)
    stdscr.addstr(4, 2, "Result: " + result)

    buttons = [
        ["7", "8", "9", "/", "sin", "cos"],
        ["4", "5", "6", "*", "tan", "sqrt"],
        ["1", "2", "3", "-", "log", "exp"],
        ["0", ".", "E", "+", "=", "C"],
        ["plot", "Del", "Quit"]
    ]

    start_y = 6
    for i, row in enumerate(buttons):
        start_x = (width - (len(row) * 5 - 1)) // 2
        for j, button in enumerate(row):
            if i == selected_row and j == selected_col:
                stdscr.addstr(start_y + i, start_x + j * 5, "[" + button + "]", curses.A_REVERSE)
            else:
                stdscr.addstr(start_y + i, start_x + j * 5, " " + button + " ")

    stdscr.refresh()


def main(stdscr):
    """Main function."""
    curses.curs_set(0)
    expression = ""
    result = ""
    selected_row = 0
    selected_col = 0

    buttons = [
        ["7", "8", "9", "/", "sin", "cos"],
        ["4", "5", "6", "*", "tan", "sqrt"],
        ["1", "2", "3", "-", "log", "exp"],
        ["0", ".", "E", "+", "=", "C"],
        ["plot", "Del", "Quit"]
    ]

    draw_calculator(stdscr, expression, result, selected_row, selected_col)

    while True:
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('c') or key == ord('C'):
            expression = ""
            result = ""
        elif key == ord('='):
            if expression.startswith("plot "):
                func_str = expression[5:]
                plot_function(stdscr, func_str)
                draw_calculator(stdscr, expression, result, selected_row, selected_col)
            else:
                result = evaluate_expression(expression)
        elif key == curses.KEY_BACKSPACE or key == 127:
            expression = expression[:-1]
        elif key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(len(buttons) - 1, selected_row + 1)
        elif key == curses.KEY_LEFT:
            selected_col = max(0, selected_col - 1)
        elif key == curses.KEY_RIGHT:
            max_col = len(buttons[selected_row]) - 1
            selected_col = min(max_col, selected_col + 1)
        elif key == ord('\n') or key == ord(' '):
            if selected_row < len(buttons) - 1:
                button = buttons[selected_row][selected_col]
                if button in "0123456789.+-*/E":
                    expression += button
                elif button in ["sin", "cos", "tan", "sqrt", "log", "exp"]:
                    expression += button + "("
                elif button == "=":
                    if expression.startswith("plot "):
                        func_str = expression[5:]
                        plot_function(stdscr, func_str)
                        draw_calculator(stdscr, expression, result, selected_row, selected_col)
                    else:
                        result = evaluate_expression(expression)
                elif button == "C":
                    expression = ""
                    result = ""
                elif button == "plot":
                    expression = "plot "
            elif selected_row == len(buttons) - 1:
                if selected_col == 0:  # plot
                    expression = "plot "
                elif selected_col == 1:  # Del
                    expression = expression[:-1]
                elif selected_col == 2:  # Quit
                    break
        elif key >= ord(' ') and key <= ord('~'):
            expression += chr(key)

        draw_calculator(stdscr, expression, result, selected_row, selected_col)


if __name__ == "__main__":
    curses.wrapper(main)