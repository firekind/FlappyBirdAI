ifeq ($(OS),Windows_NT)
	PYTHON_HOME=./venv/Scripts
	PYTORCH_FIND_LINKS_FLAG=-f https://download.pytorch.org/whl/torch_stable.html
else
	PYTHON_HOME=./venv/bin
	PYTORCH_FIND_LINKS_FLAG=
endif

venv:
	@virtualenv --python=python3 venv
	@$(PYTHON_HOME)/python -m pip install -r requirements.txt $(PYTORCH_FIND_LINKS_FLAG)
	$(PYTHON_HOME)/python -m ipykernel install --user --name flappybirdai --display-name "Python (flappybirdai)"

run:
	@$(PYTHON_HOME)/python FlappyBirdAI/main.py