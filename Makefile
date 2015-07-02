# Makefile for PyBBDB.

PYTHON = python$(VER)
SETUP  = $(PYTHON) setup.py

CLEANFILES = build dist *.egg* *.zip *.el __pycache__ .tox

.DEFAULT:;	@ $(SETUP) $@
.PHONY:		build

all:		build

build:;		@ $(SETUP) $@

test:;		$(PYTHON) -m doctest README

clean:;		@ $(SETUP) $@
		rm -rf $(CLEANFILES)
