#!/bin/bash

function uninstall {
    if [ ! -f "$HOME/bin/preview-xresources" ]; then
        echo "The program was either removed or never installed!"
        echo "Aborting..."
        exit
    fi
    rm "$HOME/bin/preview-xresources"
}

function install {
    filea=$(find ./ -type f -iname "command*")
    if [ ! -d "$HOME/bin" ]; then
        echo "Need to have path $HOME/bin."
        echo "Aborting..."
        exit
    fi
    cp $filea $HOME/bin/preview-xresources
}

while getopts "ui" arg; do
    case $arg in
        u)
            echo "Uninstalling..."
            uninstall
            ;;
        i)
            echo "Installing..."
            install
            ;;
    esac
done

