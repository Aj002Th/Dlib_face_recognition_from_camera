.PHONY:build test
.DEFAULT_GOAL := build

test:
	echo "test"

build:
	echo "build"
	pip install pyinstaller
	pyinstaller -F -w main.py