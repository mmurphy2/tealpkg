# Python interface to Slackware pkgtools, plus helper functions related to
# Slackware package name and version information.
#
# Copyright 2021-2022 Coastal Carolina University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


# TODO: refactor for MVC


import collections
import logging
import os.path
import re
import shlex
import subprocess
import time

from tealpkg.cli.colorprint import cprint
from tealpkg.util.run import log_run

INSTALLPKG = '/sbin/upgradepkg --install-new'
UPGRADEPKG = '/sbin/upgradepkg'
REMOVEPKG = '/sbin/removepkg'

PKG_EXT = re.compile('.*\.t[a-z]z$')


def splitpkg(filename):
    '''
    Splits a package into parts. Returns a named tuple for a valid package filename
    (or basename). Returns None if the package name is invalid.
    '''
    result = None

    # Strip off the file extension if we were given a package name
    if PKG_EXT.match(filename):
        filename = filename[0:-4]
    #

    pieces = os.path.basename(filename).split('-')
    if len(pieces) >= 4:
        PackageInfo = collections.namedtuple('PackageInfo', ['name', 'version', 'architecture', 'build'])
        result = PackageInfo('-'.join(pieces[0:-3]), pieces[-3], pieces[-2], pieces[-1])
    #

    return result
#


class Pkgtools:
    def __init__(self, installpkg=INSTALLPKG, upgradepkg=UPGRADEPKG, removepkg=REMOVEPKG, dry_run=False, quiet=False, log_output=False):
        self.installpkg = shlex.split(installpkg)
        self.upgradepkg = shlex.split(upgradepkg)
        self.removepkg = shlex.split(removepkg)
        self.dry_run = dry_run
        self.quiet = quiet
        self.log_output = log_output
        self.log = logging.getLogger(__name__)
    #
    def run(self, args):
        status = 0

        if self.dry_run:
            cprint('DRY RUN:', ' '.join(args), style='notice')
            time.sleep(1)
        else:
            status = log_run(args, self.quiet, self.log_output)
            if status != 0:
                self.log.error('Process returned error code: %d', status)
            #
        #

        return status
    #
    def install(self, package_path):
        return self.run(self.installpkg + [ package_path ])
    #
    def upgrade(self, package_path):
        return self.run(self.upgradepkg + [ package_path ])
    #
    def remove(self, package_name):
        return self.run(self.removepkg + [ package_name ])
    #
#
