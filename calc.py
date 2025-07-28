#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TUICalculator - A Simple Terminal Calculator
"""

import curses
import math
import re


def evaluate_expression(expr):
    """Evaluate mathematical expression with support for advanced functions."""
    # Replace constants
    expr = expr.replace('E', str(math.e))
    
    # Replace functions
    expr = re.sub(r'sin\(([^)]+)\)', r'math.sin(\1)', expr)
    expr = re.sub(r'cos\(([^)]+)\)', r'math.cos(\1)', expr)
    expr = re.sub(r'tan\(([^)]+)\)', r'math.tan(\1)', expr)
    expr = re.sub(r'sqrt\(([^)]+)\)', r'math.sqrt(\1)', expr)
    expr = re.sub(r'log\(([^)]+)\)', r'math.log10(\1)', expr)
    expr = re.sub(r'ln\(([^)]+)\)', r'math.log(\1)', expr)
    expr = re.sub(r'exp\(([^)]+)\)', r'math.exp(\1)', expr)
    
    # Evaluate expression
    try:
        result = eval(expr)
        return str(result)
    except Exception as e:
        return "Error: " + str(e)


def plot_function(stdscr, func_str):
    """Plot a function in text mode."""
    try:
        # Clear screen
        stdscr.clear()
        
        # Get screen dimensions
        height, width = stdscr.getmaxyx()
        
        # Draw title
        title = "Function Plot: " + func_str
        stdscr.addstr(1, (width - len(title)) // 2, title)
        
        # Draw axes
        # X-axis
        for x in range(2, width - 2):
            stdscr.addstr(height // 2, x, "-")
        # Y-axis
        for y in range(2, height - 2):
            stdscr.addstr(y, width // 2, "|")
        
        # Draw function
        for x in range(2, width - 2):
            # Convert screen coordinates to mathematical coordinates
            math_x = (x - width // 2) / 2.0
            
            # Evaluate function
            try:
                # Replace 'x' with the mathematical x value
                expr = func_str.replace('x', str(math_x))
                math_y = eval(expr)
                
                # Convert mathematical coordinates to screen coordinates
                screen_y = int(height // 2 - math_y * 2)
                
                # Draw point if it's within screen bounds
                if 2 <= screen_y < height - 2:
                    stdscr.addstr(screen_y, x, "*")
            except:
                pass  # Skip points that cause errors
        
        # Refresh screen
        stdscr.refresh()
        
        # Wait for key press
        stdscr.getch()
    except Exception as e:
        # Show error message
        stdscr.clear()
        stdscr.addstr(1, 1, "Error plotting function: " + str(e))
        stdscr.refresh()
        stdscr.getch()


def draw_calculator(stdscr, expression, result, selected_row=0, selected_col=0):
    """Draw the calculator interface."""
    # Clear screen
    stdscr.clear()
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Draw title
    title = "Terminal Calculator"
    stdscr.addstr(1, (width - len(title)) // 2, title)
    
    # Draw expression and result
    stdscr.addstr(3, 2, "Expression: " + expression)
    stdscr.addstr(4, 2, "Result: " + result)
    
    # Draw buttons
    buttons = [
        ["7", "8", "9", "/", "sin", "cos"],
        ["4", "5", "6", "*", "tan", "sqrt"],
        ["1", "2", "3", "-", "log", "exp"],
        ["0", ".", "E", "+", "=", "C"],
        ["Del", "Quit"]
    ]
    
    start_y = 6
    for i, row in enumerate(buttons):
        start_x = (width - (len(row) * 4 - 1)) // 2
        for j, button in enumerate(row):
            if i == selected_row and j == selected_col:
                stdscr.addstr(start_y + i, start_x + j * 4, "[" + button + "]", curses.A_REVERSE)
            else:
                stdscr.addstr(start_y + i, start_x + j * 4, " " + button + " ")
    
    # Refresh screen
    stdscr.refresh()


def main(stdscr):
    """Main function."""
    # Initialize
    curses.curs_set(0)
    expression = ""
    result = ""
    selected_row = 0
    selected_col = 0
    
    # Draw initial interface
    draw_calculator(stdscr, expression, result, selected_row, selected_col)
    
    # Main loop
    while True:
        key = stdscr.getch()
        
        # Handle key presses
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('c') or key == ord('C'):
            expression = ""
            result = ""
        elif key == ord('='):
            # Check if it's a plot command
            if expression.startswith("plot "):
                func_str = expression[5:]  # Remove "plot " prefix
                plot_function(stdscr, func_str)
                # Redraw calculator after plotting
                draw_calculator(stdscr, expression, result, selected_row, selected_col)
            else:
                result = evaluate_expression(expression)
        elif key == curses.KEY_BACKSPACE or key == 127:
            expression = expression[:-1]
        elif key == curses.KEY_UP:
            selected_row = max(0, selected_row - 1)
        elif key == curses.KEY_DOWN:
            selected_row = min(4, selected_row + 1)
        elif key == curses.KEY_LEFT:
            selected_col = max(0, selected_col - 1)
        elif key == curses.KEY_RIGHT:
            # Adjust max column based on current row
            # Define buttons layout for navigation
            buttons = [
                ["7", "8", "9", "/", "sin", "cos"],
                ["4", "5", "6", "*", "tan", "sqrt"],
                ["1", "2", "3", "-", "log", "exp"],
                ["0", ".", "E", "+", "=", "C"],
                ["Del", "Quit"]
            ]
            max_col = len(buttons[selected_row]) - 1
            selected_col = min(max_col, selected_col + 1)
        elif key == ord('\n') or key == ord(' '):  # Enter or Space key
            # Get the button text
            buttons = [
                ["7", "8", "9", "/", "sin", "cos"],
                ["4", "5", "6", "*", "tan", "sqrt"],
                ["1", "2", "3", "-", "log", "exp"],
                ["0", ".", "E", "+", "=", "C"],
                ["Del", "Quit"]
            ]
            
            # Handle button press
            if selected_row < 4:
                button = buttons[selected_row][selected_col]
                if button in "0123456789.+-*/E":
                    expression += button
                elif button in ["sin", "cos", "tan", "sqrt", "log", "exp"]:
                    expression += button + "("
                elif button == "=":
                    # Check if it's a plot command
                    if expression.startswith("plot "):
                        func_str = expression[5:]  # Remove "plot " prefix
                        plot_function(stdscr, func_str)
                        # Redraw calculator after plotting
                        draw_calculator(stdscr, expression, result, selected_row, selected_col)
                    else:
                        result = evaluate_expression(expression)
                elif button == "C":
                    expression = ""
                    result = ""
            elif selected_row == 4:  # Last row with Del and Quit buttons
                if selected_col == 0:  # Del button
                    if len(expression) > 0:
                        expression = expression[:-1]
                elif selected_col == 1:  # Quit button
                    break
        elif key >= ord(' ') and key <= ord('~'):
            expression += chr(key)
        
        # Draw updated interface
        draw_calculator(stdscr, expression, result, selected_row, selected_col)


if __name__ == "__main__":
    curses.wrapper(main)