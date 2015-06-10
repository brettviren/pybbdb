# Setup script for PyBBDB.

import os
from setuptools import setup

thisdir = os.path.dirname(__file__)
readme = os.path.join(thisdir, "README")

setup(name             = "pybbdb",
      version          = "0.1",

      author           = "Glenn Hutchings",
      author_email     = "zondo42@gmail.com",

      description      = "Pythonic interface to BBDB.",
      long_description = "\n" + open(readme).read(),

      url              = "http://pypi.python.org/pypi/pybbdb",
      license          = "GPL",

      py_modules       = ["bbdb"],
      install_requires = ["pyparsing"],

      classifiers      = [
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
          "Programming Language :: Python :: 2.7",
          "Topic :: Communications :: Email :: Address Book",
          "Topic :: Database",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ])

# flake8: noqa
