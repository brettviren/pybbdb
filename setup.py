# Setup script for python module.

from distutils.core import setup
from src import __author__, __contact__, __version__, __license__

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: POSIX :: Linux",
    "Operating System :: MacOS",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules"
]

setup(name         = "pystar",
      author       = __author__,
      author_email = __contact__,
      url          = "http://fluffybunny.memebot.com/pystar.html",
      description  = "A* graph search algorithm implementation.",
      version      = __version__,
      license      = __license__,
      package_dir  = {"astar": "src"},
      packages     = ["astar"],
      classifiers  = classifiers)
