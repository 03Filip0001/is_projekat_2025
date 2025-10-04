VENV := .venv
PYTHON := $(VENV)\Scripts\python

ifeq ($(OS), Windows_NT)
	CREATE_VENV := if not exist $(VENV) (python -m venv $(VENV))
	CLEAN_CMD_ENV := if exist $(VENV) rmdir /s /q $(VENV)
	CLEAN_CMD_PYCACHE := for /r %%d in (.) do @if exist "%%d\__pycache__" rmdir /s /q "%%d\__pycache__"
else
	CREATE_VENV := [ ! -d "$(VENV)" ] && python3 -m venv $(VENV)
	CLEAN_CMD_ENV := rm -rf $(VENV)
	CLEAN_CMD_PYCACHE := find . -type d -name "__pycache__" -exec rm -rf {} +
endif

.PHONY: clean, run, venv, requirements

.DEFAULT_GOAL := run

clean:
	@echo Removing __pychache__ folders...
	@$(CLEAN_CMD_PYCACHE)
	@echo Done
	@python -c "print()"

	@echo Removing virtual environment $(VENV) folder...
	@$(CLEAN_CMD_ENV)
	@echo Done
	@python -c "print()"

requirements: venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

venv:
	if not exist $(VENV) (python -m venv $(VENV))

run: requirements
	$(PYTHON) -m streamlit run main.py --server.port 8801
	