venv:
	@virtualenv --python=python3 venv && venv/bin/python -m pip install -r requirements.txt

run:
	@python FlappyBirdAI/main.py