#!/bin/sh

MOVIE=`zenity --file-selection --title "Select the movie file" --file-filter "Movie (*.avi) | *.avi"`
case $? in
    1) zenity --warning --text "No file selected.\nProgram aborted."; exit;;
   -1) zenity --warning --text "No file selected.\nProgram aborted."; exit
esac

zenity --question --text "Do you have a configuration file?" --ok-label "Yes" --cancel-label "No"
case $? in
    0) CONFIG=`zenity --file-selection --title "Select the configuration file" --file-filter "Config file (*.txt) | *.txt"`;;
    1) CONFIG=""
esac

FPS=`zenity --entry --title "FPS needed" --text "Please enter the Frames-per-Second value used"`
case $? in
    1) FPS="1"
esac

python opencv_bacteria.py $MOVIE $CONFIG
python plot_phase.py $FPS ${MOVIE%\.avi}.h5
