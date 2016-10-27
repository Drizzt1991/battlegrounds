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

clean:
	make -C battlegrounds clean

.PHONY: all build venv flake test vtest testloop cov clean doc