FLAGS=

setup:
	pip install -r requirements.txt
	make -C client setup

test:
	make -C client test

vtest:
	make -C client vtest

cov cover coverage:
	make -C client cov

clean:
	make -C client clean

.PHONY: all build venv flake test vtest testloop cov clean doc