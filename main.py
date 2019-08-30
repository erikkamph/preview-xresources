# A Theme previewer program for Xresources and base16
# Copyright 2019 © Erik Kamph

import getopt
import os
import fileinput
import subprocess
import sys
import argparse
import textwrap
from subprocess import call
import re
import shlex


# Clears the screen
def clear():
    _ = call("clear" if os.name == "posix" else "cls")


# Searches in file, never used
def containing(search, file):
    return [line for line in file if search in line]


# Opens the current Xresources writes the new line and saves the old one as backup in case something wen wrong
def save(theme_location):
    with open(home + "/.Xresources.backup", "a") as new:
        with open(home + "/.Xresources", "r") as old:
            for line in old.readlines():
                if "#include" not in line:
                    new.write(line)
                else:
                    new.write("#include \"" + theme_location + "\"\n")
    os.rename(home + "/.Xresources", home + "/.Xresources.bak")
    os.rename(home + "/.Xresources.backup", home + "/.Xresources")


# Print a progress bar showing how many files there are and how many you have passed
def progress(curr, highest, dir):
    # rows, columns = os.popen('stty size', "r").read().split()
    percentage = (curr / highest) * 100
    start_string_len = len(" " + str(curr) + "/" + str(highest) + " [")
    end_string_len = len("] 100% ")
    total = start_string_len + end_string_len
    width = int(columns) - total
    parts = width / highest
    string_one_parts = parts * curr
    string_two_parts = parts * (highest - curr)
    string_one = "#" * int(string_one_parts)
    string_two = "." * int(string_two_parts)
    rowsminusone = int(rows) - 1
    cmd = ""
    if dir != "":
        cmd = "ls --color=always " + str(dir)
    else:
        cmd = "ls --color=always"
    args = shlex.split(cmd)
    output, err = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    printable = str(output).strip("\'b").replace("\\x1b", "\033").replace("\\n", " ")

    print("\033[s", end="")
    print("\033[" + str(rowsminusone) + ";1H", end="")
    print("\033[2K", end="")
    print(printable, end="")
    print("\033[" + rows + ";1H", end="")
    print("\033[2K", end="")
    print(str(curr) + "/" + str(highest) + " [" + string_one + string_two + "] " + str(int(percentage)) + "% ", end="")
    print("\033[u", end="")


# Read all filenames and ignore everything that has to do with git
# or something else that isn't Xresources or base16 files.
def get_files(themes_location):
    files = []
    for r, d, f in os.walk(themes_location):
        for file in f:
            if file not in (".", "..", "README.md", "LICENSE", "exclude", "HEAD", "master",
                            "config", "packed-refs", "index", "description"):
                if not re.search(".*.idx", file) \
                    and not re.search(".*.pack", file) \
                        and not re.search(".*.sample", file):
                    files.append(os.path.join(r, file))
    return files


# Print the usage when something went wrong or -h is supplied
def usage():
    parser = argparse.ArgumentParser(description=textwrap.dedent('''
         description:
         A program for previewing Xresource- and base16
         theme files before applying the theme to the terminal.
         After applying the theme by pressing s do one of following:
            - xrdb --merge
            - Restart computer
         
         You could also send commands through the script using
         command:<command>, where <command> can for instance be:
            - ls --color=none
            - pwd
         NOTE: Using pipes is experimental right now, it doesn't
         always work and the output is sometimes the command which
         was sent into the "command:".
         
         Quitting the program is also easy, just press q and
         then hit ENTER to exit the program without doing
         CTRL+C.
         '''), formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o, --output", help="used to enable/disable printable output. like which file we are "
                                             "looking at or which folder you wrote for input.", action='store_true')
    parser.add_argument("-v, --version", action="version", version="%(prog)s 1.5")
    parser.add_argument("folder", help="the location of the folder containing any number of xresource files greater "
                                       "than 0")
    parser.add_argument("-s, --start", default="0", metavar="number", help="a number that tells which of the n number "
                                                                           "of files to start from.")
    parser.add_argument("-d, --ls", metavar="folder", help="A folder to display contents of while running the program"
                                                           " just to see more colors, if not specified current dir will"
                                                           " be used as output instead!")
    parser.add_argument("-b, --blocks", metavar="colors", default="2", help="a number used for displaying color blocks"
                                                                            " on the right side of the screen, if this"
                                                                            " option is left out it will default to 2.")
    parser.print_help()


# For each line in the file there will be for example *.foreground: #123455, based on the *.foreground we have build an
# return a code which we want to use later in when printing it in the terminal.
def getcode(line):
    code = ""
    if re.search(".*foreground:.*", line):
        code = "10;"
    elif re.search(".*background:.*", line):
        code = "11;"
    elif re.search(".*cursorColor:.*", line):
        code = "12;"
    elif re.search(".*color0:.*", line):
        code = "4;0;"
    elif re.search(".*color1:.*", line):
        code = "4;1;"
    elif re.search(".*color2:.*", line):
        code = "4;2;"
    elif re.search(".*color3:.*", line):
        code = "4;3;"
    elif re.search(".*color4:.*", line):
        code = "4;4;"
    elif re.search(".*color5:.*", line):
        code = "4;5;"
    elif re.search(".*color6:.*", line):
        code = "4;6;"
    elif re.search(".*color7:.*", line):
        code = "4;7;"
    elif re.search(".*color8:.*", line):
        code = "4;8;"
    elif re.search(".*color9:.*", line):
        code = "4;9;"
    elif re.search(".*color10:.*", line):
        code = "4;10;"
    elif re.search(".*color11:.*", line):
        code = "4;11;"
    elif re.search(".*color12:.*", line):
        code = "4;12;"
    elif re.search(".*color13:.*", line):
        code = "4;13;"
    elif re.search(".*color14:.*", line):
        code = "4;14;"
    elif re.search(".*color15:.*", line):
        code = "4;15;"
    return code


# If the file is base16, load all #define's as key value pairs
# and read each line after that and print the correct escape
# sequence in the terminal
def base16previewer(file):
    valuedict = {}
    with open(file, "r") as f:
        for line in f:
            if re.search("#define.*", line):
                key = line.split(" ")[1]
                value = line.split(" ")[2].strip("\r").strip("\n")
                valuedict[key] = value
    # print(valuedict)
    with open(file, "r") as f:
        for line in f:
            code = getcode(line)
            value = ""
            if re.search("base[0-9]+.$", line):
                x = len(line) - 7
                key = line[x:].strip("\r").strip("\n")
                value = valuedict[key]
            if value != "" and code != "":
                print("\033]" + code + value + "\007", end="")


# If the theme is not base16 then just read it because the values will not be on any other place.
def preview_theme(path):
    if path.__contains__("base16"):
        base16previewer(path)
    else:
        with open(path, "r") as file:
            for line in file.readlines():
                code = getcode(line)
                value = ""
                if line.__contains__("#"):
                    value = "#" + line.split("#")[1].strip("\r").strip("\n")
                if value != "" and code != "":
                    print("\033]" + code + value + "\007", end="")


# Prints blocks of colors in the top right corner of the screen,
# if -b 0 is supplied none will be printed, otherwise the highest number recommended
# is 7 for -b or --blocks.
def print_colors(blocks):
    print("\033[s", end="")
    from_right = int(columns) - 55
    x = 1
    for i in range(blocks):
        for j in range(30, 38):
            print("\033[" + str(x) + ";" + str(from_right) + "H", end="")
            for k in range(40, 48):
                print("\033[%d;%d;%dm%d;%d;%d\033[m\007" % (i, j, k, i, j, k), end="")
            print()
            x += 1
    print("\033[u", end="")


# Prints location and where in the array we start, previews the theme and asks for a choice,
# the choice can either be s to save, q to quit or command: followed by a bash-command.
def preview(files, output, start, themes_location, blocks, dir):
    if output:
        print("Location: " + themes_location)
        print("Start: " + str(start))
        print("Keys: Enter to continue, s to save, q to quit")
    x = start
    maximum = len(files) - 1
    while True:
        print(files[x], end="")
        preview_theme(files[x])
        if output:
            if blocks > 0:
                print_colors(blocks)
        progress(x, maximum, dir)
        # print("\033[s", end="")
        choice = str(input())
        if choice == "s":
            save(files[x])
            break
        elif choice == "q":
            break
        elif re.search("command:.*", choice):
            command = choice.split(":")[1]
            args = shlex.split(command)
            output, error = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            printable = str(output)[2:].replace("'", "").replace("\\n", " ").replace("\\x1b", "\x1b")
            print(printable)
        # print("\033[u\033[2K", end="")
        x += 1
        if x > maximum:
            break


# Parses the arguments and goes to the function above.
def main():
    try:
        opts, argv = getopt.getopt(sys.argv[1:], "hovs:d:b:", ["help", "output", "version", "start=", "ls=", "blocks="])
    except getopt.GetoptError as error:
        print(error.__str__())
        usage()
        sys.exit(2)

    output = None
    start = 0
    blocks = 2
    dir = ""

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--output"):
            output = 1
        elif o in ("-v", "--version"):
            print("ThemePreviewer 1.0")
            sys.exit()
        elif o in ("-s", "--start"):
            start = int(a)
        elif o in ("-d", "--ls"):
            dir = str(a)
        elif o in ("-b", "--blocks"):
            blocks = int(a)
            if blocks < 0:
                usage()
                sys.exit()
        else:
            usage()
            assert False, "There is no option like that."

    if not argv:
        usage()
        sys.exit()

    themes_location = argv[0]

    if not themes_location:
        usage()
        print("You must specify a folder where all the Xresources themes are located at.")
        exit()

    clear()
    if not output:
        print("------------- Warning -------------")
        print("1. You have been warned about this ")
        print("2. There is no going back now!     ")
        print("3. There will be complete silence! ")

    print("\033[1;" + str(int(rows) - 3) + "r", end="")  # Change region temporarily by 2 rows while running the program
    files = get_files(themes_location)
    preview(files=files, output=output, start=start, themes_location=themes_location, blocks=blocks, dir=dir)
    # print("\033[0m", end="")
    print("\033[1;" + rows + "r", end="")  # Restores the region to the original position


if __name__ == '__main__':
    rows, columns = os.popen("stty size", "r").read().split()
    home = os.path.expanduser("~")
    main()
    sys.exit()
