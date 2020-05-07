#!/bin/bash
script_path=$(find $HOME/ -type d -iname "preview-xresources")
script_exe=$(find $script_path/ -type f -iname "main.py")
python $script_exe
