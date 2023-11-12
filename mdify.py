#!/usr/bin/env python3

import curses
import os
import pyperclip
import time


def infer_language(filename):
    _, ext = os.path.splitext(filename)
    return ext[1:]


def format_file_content(filepath):
    language = infer_language(filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
        code_block = f"```{language}\n{content}\n```\n"
        return code_block
    except Exception as e:
        return f"Error reading {filepath}: {e}\n"


# Curses function to choose files
def select_files(screen, target_directory):
    # Initialize color pairs
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(
        1, curses.COLOR_GREEN, curses.COLOR_BLACK
    )  # Color for selected files
    curses.init_pair(
        2, curses.COLOR_WHITE, curses.COLOR_BLACK
    )  # Color for highlighted line
    curses.init_pair(
        3, curses.COLOR_YELLOW, curses.COLOR_BLACK
    )  # Color for file details

    # Fetch and sort the list of files in the directory
    items = os.listdir(target_directory)
    files = [
        (f, os.stat(os.path.join(target_directory, f)))
        for f in items
        if os.path.isfile(os.path.join(target_directory, f))
    ]
    files.sort(key=lambda x: x[1].st_mtime, reverse=True)  # Sort by modified time

    # Dictionary to keep track of selected files
    selected_flags = {file[0]: False for file in files}
    position = 0  # Current position in the file list

    # Main selection loop
    while True:
        screen.clear()
        max_y, max_x = screen.getmaxyx()

        # Display instructions at the top
        instructions = "Navigation: ↑/↓ Select: space Confirm: Enter Exit: Esc"
        screen.addstr(0, 0, instructions, curses.A_BOLD | curses.color_pair(3))

        for index, (filename, stats) in enumerate(files):
            if index == position:
                mode = (
                    curses.color_pair(2) | curses.A_BOLD
                )  # Highlight the current line
            else:
                mode = curses.A_NORMAL

            # File selection checkbox
            checkbox = "[X]" if selected_flags[filename] else "[ ]"

            # Line formatting with filename, size, and last modification date
            filesize = stats.st_size
            mod_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime)
            )
            line = f"{checkbox} {filename.ljust(30)} {str(filesize).rjust(10)} bytes  {mod_time}"

            # Change color if the file is selected
            if selected_flags[filename]:
                screen.attron(curses.color_pair(1))
            screen.addstr(index + 2, 0, line, mode)
            if selected_flags[filename]:
                screen.attroff(curses.color_pair(1))

            # Prevent overflow for long lists of files
            if index + 2 >= max_y - 1:
                break

        screen.refresh()

        # User input handling
        key = screen.getch()
        if key == curses.KEY_UP and position > 0:
            position -= 1
        elif key == curses.KEY_DOWN and position < len(files) - 1:
            position += 1
        elif key == ord(" "):
            # Toggle selection state
            filename = files[position][0]
            selected_flags[filename] = not selected_flags[filename]
        elif key == ord("\n"):
            # Confirm selections with Enter and exit
            break
        elif key == 27:
            # Exit with the Esc key
            return []

    # Return list of selected filenames
    return [file for file, selected in selected_flags.items() if selected]

def main(target_directory):
    selected_files = curses.wrapper(select_files, target_directory)
    markdown_output = ""

    for file in selected_files:
        file_path = os.path.join(target_directory, file)
        markdown_output += f"{file_path}:\n{format_file_content(file_path)}\n"

    pyperclip.copy(markdown_output)
    print("Markdown copied to clipboard.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: mdify.py <target-directory>")
    else:
        target_directory = sys.argv[1]
        if not os.path.exists(target_directory):
            print("Error: Target directory does not exist.")
        elif not os.path.isdir(target_directory):
            print("Error: The path provided is not a directory.")
        else:
            main(target_directory)
