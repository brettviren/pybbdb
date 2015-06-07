# Makefile for python module.

SETUP = python setup.py

SRC_FORMATS = gztar,zip

.DEFAULT:;	@ $(SETUP) $@
.PHONY:		build dist

all:		build
tags:;		find . -name '*.py' | xargs etags

build:;		@ $(SETUP) $@
sdist:;		@ $(SETUP) $@ --formats=$(SRC_FORMATS)

upload:;	@ $(SETUP) sdist upload

clean:;		rm -rf MANIFEST PKG-INFO build dist
