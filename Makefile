PYTHON ?= python3
PHONY=check clean dist distclean test rmChangeLog flake8
#: Clean up temporary files
clean:
	find . | grep -E '\.pyc' | xargs rm -rvf;
	find . | grep -E '\.pyo' | xargs rm -rvf;
	$(PYTHON) ./setup.py $@
