all: ui_click_mean2.py ui_video.py

ui_%.py: %.ui
	pyuic4 -o $@ $^

