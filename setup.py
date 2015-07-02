# Setup script for PyBBDB.

import os
from setuptools import setup

# Bootstrap setuptools.
from conf.ez_setup import use_setuptools
use_setuptools()

# Do the setup.
from conf.tools import read_pkginfo
from conf.unittest import PyTest

info = read_pkginfo("bbdb")

thisdir = os.path.dirname(__file__)
readme = os.path.join(thisdir, "README")

setup(name             = info.__title__,
      version          = info.__version__,
      author           = info.__author__,
      author_email     = info.__email__,
      description      = info.__desc__,
      long_description = "\n" + open(readme).read(),
      url              = info.__url__,
      classifiers      = info.__classifiers__.strip().split("\n"),
      license          = info.__license__,

      packages         = ["bbdb"],
      cmdclass         = {'test': PyTest},
      setup_requires   = ["hgtools"],
      install_requires = ["pyparsing", "voluptuous", "six"],
      tests_require    = ["pytest"])

# flake8: noqa
