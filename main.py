import getopt
import os
import fileinput
import sys
import argparse
from subprocess import call
import keyboard


def clear():
    _ = call("clear" if os.name == "posix" else "cls")


def containing(search, file):
    return [line for line in file if search in line]


def save(theme_location):
    with open("/home/erik/.Xresources.backup", "a") as new:
        with open("/home/erik/.Xresources", "r") as old:
            for line in old.readlines():
                if "#include" not in line:
                    new.write(line)
                else:
                    new.write("#include \"" + theme_location + "\"\n")
    home = os.path.expanduser("~")
    os.rename(home + "/.Xresources", home + "/.Xresources.bak")
    os.rename(home + "/.Xresources.backup", home + "/.Xresources")


def progress(curr, highest):  # Print a progress bar showing how many files there are and how many you have passed
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

    print("\033[s", end="")
    print("\033[" + rows + ";1H", end="")
    print("\033[2K", end="")
    print(str(curr) + "/" + str(highest) + " [" + string_one + string_two + "] " + str(int(percentage)) + "% ", end="")
    print("\033[u", end="")


def get_files(themes_location):
    files = []
    for r, d, f in os.walk(themes_location):
        for file in f:
            if file != "." or file != "..":
                files.append(os.path.join(r, file))
    return files


def usage():
    parser = argparse.ArgumentParser(description="preview Xresource theme files before choosing theme for your "
                                                 "urxvt-sensible-terminal")
    parser.add_argument("-o, --output", help="used to enable/disable printable output. like which file we are "
                                             "looking at or which folder you wrote for input.", action='store_true')
    parser.add_argument("-v, --version", action="version", version="%(prog)s 2.0")
    parser.add_argument("folder", help="the location of the folder containing any number of xresource files greater "
                                       "than 0")
    parser.add_argument("-s, --start", default="0", metavar="number", help="a number that tells which of the n number "
                                                                           "of files to start from.")
    parser.print_help()


def preview_theme(path):
    with open(path, "r") as file:
        for line in file.readlines():
            if "*.foreground" in line:
                if "#" in line:
                    value = "#" + line.split("#")[1] + "\007"
                    print("\033]10;" + value, end="")
            if "*.background" in line:
                if "#" in line:
                    value = "#" + line.split("#")[1] + "\007"
                    print("\033]11;" + value, end="")


def preview(files, output):
    x = 1
    maximum = len(files)
    for f in files:
        if output:
            print(f)
        progress(x, maximum)
        x += 1
        preview_theme(f)
        print("\033[s", end="")
        print("Options enter to continue, s to save, q to quit: ", end="")
        choice = str(input())
        if choice == "s":
            save(f)
            exit(0)
        elif choice == "q":
            exit(0)
        print("\033[u\033[2K", end="")


def main():
    try:
        opts, argv = getopt.getopt(sys.argv[1:], "hovs:", ["help", "output", "version", "start="])
    except getopt.GetoptError as error:
        print(error.__str__())
        usage()
        sys.exit(2)

    output = None
    themes_location = None
    start = 0

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

    if output:
        print("Location: " + themes_location)
        print("Start at: " + str(start))

    print("\033[1;" + str(int(rows) - 2) + "r")  # Change region temporarily by 2 rows while running the program
    files = get_files(themes_location)
    preview(files, output)
    print("\033[1;" + rows + "r")  # Restores the region to the original position


if __name__ == '__main__':
    rows, columns = os.popen("stty size", "r").read().split()
    main()
    sys.exit()
