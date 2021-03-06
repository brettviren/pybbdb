"""
Configuration tools.
"""

import os


def read_pkginfo(dirname, infofile="pkginfo.py", versionfile="version.py",
                 versionattr="__version__"):
    """
    Read python package information.

    Avoids importing as a module, since that might mean having other stuff
    installed before it needs to be (i.e., at setup stage).

    Args:
        dirname: Directory to read/write sources in.
        infofile: Package information file.
        versionfile: File to write version information to.
        versionattr: Name of attribute storing the version.

    Returns:
        Package information dict.
    """

    # Gather settings from the python file.
    info = Pkginfo()
    path = os.path.join(dirname, infofile)
    if os.path.exists(path):
        info.read(path)

    # Add SCM options for getting and writing version info.
    scm_options = {'write_to': os.path.join(dirname, versionfile),
                   'write_to_template': version_format % versionattr}

    info["__scm_options__"] = scm_options

    return info


class Pkginfo(dict):
    "Helper class to get package information from Python sources."

    def read(self, filename):
        with open(filename) as fp:
            exec(fp.read(), self)

    def __getattr__(self, attr):
        return self[attr]


version_format = """# Autogenerated by setup -- do not edit!

%s = '{version}'
"""
