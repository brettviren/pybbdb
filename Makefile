# Makefile for python module.

NAME = "PyStar -- A* graph search algorithm"
URL  = http://fluffybunny.memebot.com/pystar.html

EPYDOC = epydoc -v --name $(NAME) --url $(URL) --no-private
MODULES = build/lib/astar

SETUP = python setup.py

SRC_FORMATS = gztar,zip
BIN_FORMATS = wininst

.DEFAULT:;	@ $(SETUP) $@
.PHONY:		build dist

all:		build
dist:		doc sdist
tags:;		find . -name '*.py' | xargs etags

build:;		@ $(SETUP) $@
sdist:;		@ $(SETUP) $@ -f --formats=$(SRC_FORMATS)
bdist:;		@ $(SETUP) $@ --formats=$(BIN_FORMATS)
help:;		@ $(SETUP) --help
commands:;	@ $(SETUP) --help-commands

doc:		build
		$(EPYDOC) $(MODULES)

pdf:		build
		$(EPYDOC) --pdf $(MODULES)

doccheck:	build
		$(EPYDOC) --check $(MODULES)

upload:;	@ $(SETUP) sdist upload

clean:;		@ (cd src; $(MAKE) -s clean)
		rm -rf MANIFEST PKG-INFO build dist
