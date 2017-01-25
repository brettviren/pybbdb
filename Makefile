# Makefile for PyBBDB.

PYTHON = python$(VER)
SETUP  = $(PYTHON) setup.py

CLEANFILES = build dist *.egg* *.zip *.el __pycache__ .tox

.DEFAULT:;	@ $(SETUP) $@ $(OPTS)
.PHONY:		build doc

all:		develop

doc build:;	@ $(SETUP) $@

doctest:;	$(PYTHON) -m doctest README

tags:;		find . -name '*.py' | xargs etags

clean:;		$(SETUP) $@
		find . -name '*.py[co]' | xargs rm
		rm -rf $(CLEANFILES)
