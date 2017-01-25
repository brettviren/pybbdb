# Setup script for PyBBDB.

import os
import sys

# Bootstrap setuptools.
from conf.ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

# Do the setup.
from conf.tools import read_pkginfo

info = read_pkginfo("bbdb")

# Build setup requirements.
setup_requires = []

if os.path.exists('.hg'):
    setup_requires.append('setuptools_scm')

if {'pytest', 'test', 'ptr'}.intersection(sys.argv):
    setup_requires.append('pytest-runner')

# Find the README for long description.
thisdir = os.path.dirname(__file__)
readme = os.path.join(thisdir, "README")

# Do the setup.
setup(name             = info.__title__,
      author           = info.__author__,
      author_email     = info.__email__,
      description      = info.__desc__,
      long_description = "\n" + open(readme).read(),
      url              = info.__url__,
      classifiers      = info.__classifiers__.strip().split("\n"),
      license          = info.__license__,
      packages         = ["bbdb"],
      setup_requires   = setup_requires,
      use_scm_version  = info.__scm_options__,
      install_requires = ["pyparsing", "voluptuous", "six"],
      tests_require    = ["pytest"])

# flake8: noqa
