#!/usr/bin/env python3

from sys import platform, stderr, version_info

from distutils.command.sdist import sdist
from setuptools import setup

from kargparse import get_release_string_pep440

# Disable version normalization performed by setup(). This code
# indirectly depends on the CustomSDist class to handle our 'rc'
# version numbers, which have the following format: 'X.Y.Z.rcN'.
# The desired package name format is: 'package-X.Y.Z.rcN.tar.gz'.
# Without CustomSDist, we get: 'package-X.Y.ZrcN.tar.gz' (i.e.,
# the '.' separator between 'Z' and 'rcN' has been eliminated.
# The patch/workaround below is documented here:
#
#   https://github.com/pypa/setuptools/issues/308
#
try:
    # Try the approach of using sic(), added in setuptools 46.1.0.
    from setuptools import sic
except ImportError:
    # Try the approach of replacing packaging.version.Version.
    sic = lambda v: v
    try:
        # Note that setuptools >=39.0.0 uses packaging from setuptools.extern.
        from setuptools.extern import packaging
    except ImportError:
        # Note that setuptools <39.0.0 uses packaging from pkg_resources.extern.
        from pkg_resources.extern import packaging
    packaging.version.Version = packaging.version.LegacyVersion

class CustomSDist(sdist):

    def run(self):
        super().run()

    def prune_file_list(self):
        """Prune off branches that might slip into the file list as created
        by 'read_template()', but really don't belong there:
          * the build tree (typically "build")
          * the release tree itself (only an issue if we ran "sdist"
            previously with --keep-temp, or it aborted)
          * any RCS, CVS, .svn, .hg, .git*, .bzr, _darcs directories
        """
        build = self.get_finalized_command('build')
        base_dir = self.distribution.get_fullname()

        self.filelist.exclude_pattern(None, prefix=build.build_base)
        self.filelist.exclude_pattern(None, prefix=base_dir)

        # pruning out vcs directories
        # both separators are used under win32
        if platform == 'win32':
            seps = r'/|\\'
        else:
            seps = '/'

        vcs_dirs = ['RCS', 'CVS', r'\.svn', r'\.hg', r'\.git.*', r'\.bzr', '_darcs']
        vcs_ptrn = r'(^|%s)(%s)(%s).*' % (seps, '|'.join(vcs_dirs), seps)
        self.filelist.exclude_pattern(vcs_ptrn, is_regex=1)

if version_info < (3, 6, 0):
    print("This project requires Python version 3.6.0 or higher.", file=stderr)
    exit(2)

setup(
    author='Luke Monroe',
    author_email='lmmonroe.git@korelogic.com',
    classifiers=['Operating System :: POSIX :: Linux'],
    cmdclass={'sdist': CustomSDist},
    description="""A korified extension of Python's argparse module.""",
    license='GPL-3',
    long_description="""
                     KArgParse is a korified extension of Python's argparse module,
                     which was originally developed by Steven J. Bethard.
                     """,
    maintainer='Klayton Monroe',
    maintainer_email='kargparse-project@korelogic.com',
    name='kargparse',
    packages=['kargparse'],
    platforms=['Linux'],
    scripts=[],
    url='https://github.com/KoreLogicSecurity/kargparse',
    version=sic(get_release_string_pep440())
)

