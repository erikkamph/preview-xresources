import getopt
import os
import fileinput
import sys
import argparse
from subprocess import call


def clear():
    _ = call("clear" if os.name == "posix" else "cls")


def containing(search, file):
    return [line for line in file if search in line]


def save(theme_location):
    with fileinput.FileInput("/home/erik/.Xresources", inplace=True, backup=".bak") as file:
        replace = containing("#include", file)
        for line in file:
            print(line.replace(replace, "#include '" + theme_location + "'"))


def progress(curr, highest):  # Print a progress bar showing how many files there are and how many you have passed
    # rows, columns = os.popen('stty size', "r").read().split()
    percentage = (curr / highest) * 100
    start_string_len = len(" " + str(curr) + "/" + str(highest) + " [")
    end_string_len = len("] 100% ")
    total = start_string_len + end_string_len
    width = columns - total
    parts = width / highest
    string_one_parts = parts * curr
    string_two_parts = parts * (highest - curr)
    string_one = "#" * string_one_parts
    string_two = "." * string_two_parts

    print("\033[s", end="")
    print("\033[" + rows + ";1H", end="")
    print("\033[2K", end="")
    print(curr + "/" + highest + " [" + string_one + string_two + "] " + str(percentage) + "%% ", end="")
    print("\033[u", end="")


def preview(themes_location):
    print(themes_location)


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
        print("")
        print("There must be some arguments!")
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
    preview(themes_location)
    print("\033[1;" + rows + "r")  # Restores the region to the original position


if __name__ == '__main__':
    rows, columns = os.popen("stty size", "r").read().split()
    main()
    sys.exit()
