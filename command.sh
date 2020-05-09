#!/bin/bash
script_path=$(find $HOME/ -type d -iname "preview-xresources")
script_exe=$(find $script_path/ -type f -iname "main.py")

if [ $# -eq 0 ]; then
    python $script_exe
    exit
fi

if [ ! -f $script_exe ]; then
    echo "The name of the script is no longer \"main.py\", please fix that!"
    exit
fi

python $script_exe $@
