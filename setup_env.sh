#!/bin/bash

# Needstart is an additional functionality for time management.
# To avoid checking repository apt once again.

# Check for needrestart, if dosent have - install
if ! command -v needrestart &> /dev/null; then
    sudo apt install -y needrestart
fi

# Checking when apt update was last run
if needrestart -b | grep -q "apt"; then
    sudo apt update
else
    echo "No update required"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
	echo "Created virtual environment"
	python3 -m venv venv

	# Activate & install dependecy
	exec bash --init-file <(echo "source venv/bin/activate; python3 -m pip install -U pip && python3 -m pip install -r requirements.txt; pre-commit install")

	echo "After running the script, you are left in a new shell with venv enabled."
	echo "If you want to exit it, press Ctrl + D"
else
	echo "Virtual environment alredy have!"
fi

echo "Exit"
