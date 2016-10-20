FLAGS=


flake:
	flake8 client engine tests

setup:
	pip install -Ue .

test: flake
	py.test -s --tb=native $(FLAGS) tests

vtest: flake
	py.test -s -v --tb=native $(FLAGS) tests

cov cover coverage: flake
	coverage erase
	coverage run --source=engine,client,tests -m nose -s $(FLAGS) tests
	coverage report
	coverage html
	echo "open file://`pwd`/htmlcov/index.html"

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf cover
	python setup.py clean

.PHONY: flake test vtest cov clean doc