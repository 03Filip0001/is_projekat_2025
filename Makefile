VENV := .venv
PYTHON := $(VENV)/Scripts/python

.PHONY: run, venv, requirements

.DEFAULT_GOAL := run

requirements: venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

venv:
	if not exist $(VENV) (python -m venv $(VENV))

run: requirements
	$(PYTHON) main.py