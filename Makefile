FLAGS=

setup:
	pip install -r requirements.txt
	make -C battlegrounds setup

test:
	make -C battlegrounds test

vtest:
	make -C battlegrounds vtest

cov cover coverage:
	make -C battlegrounds cov

cov-all:
	make -C battlegrounds cov

clean:
	make -C battlegrounds clean

doc:
	make -C docs html
	@echo "open file://`pwd`/docs/_build/html/index.html"

.PHONY: all build venv flake test vtest testloop cov clean doc