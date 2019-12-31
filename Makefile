ifeq ($(OS),Windows_NT)
	PYTHON_HOME=./venv/Scripts
else
	PYTHON_HOME=./venv/bin
endif

venv:
	@virtualenv --python=python3 venv
	@$(PYTHON_HOME)/python -m pip install -r requirements.txt

run:
	@$(PYTHON_HOME)/python FlappyBirdAI/main.py