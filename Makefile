PYTHON ?= python
export PYTHONPATH := $(CURDIR)/src

.PHONY: test experiments clean

test:
	$(PYTHON) -m pytest -q

experiments:
	cd experiments && PYTHONPATH=../src $(PYTHON) run_all.py

clean:
	rm -f results/* figures/*.png
