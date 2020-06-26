#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Group No.18 in DSP of Lanzhou University: Yuming Chen, Huiyi Liu"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__version__ = "0.1"
__maintainer__ = ["Yuming Chen", "Huiyi Liu"]
__email__ = ["chenym18@lzu.edu.cn","liuhuiyi18@lzu.edu.cn"]
__status__ = "Experimental"

import os
import unicodedata
from subprocess import Popen, PIPE, DEVNULL
from subprocess import CalledProcessError, TimeoutExpired


class InvalidPathError(EnvironmentError):
    pass


class Rep:
    """
    "Rep" class is to represent the git repository
    "execute" can run the command in the git repository
    """

    def __init__(self, path):
        """
        Init the git repository and check if the repository is valid
        Args:
            path: repository path
        """
        self.path = path
        # Verify the repository
        try:
            assert os.path.exists(os.path.join(self.path, '.git')), True
        except AssertionError:
            print('Invalid Git Repository')
            raise InvalidPathError from None

    def execute(self, cmd, shell):
        """
        Run the git command and return the output.
        Deal with the timeout error and Catch the invalid reversion number.
        """
        p = Popen(cmd, stdout=PIPE, stderr=DEVNULL, shell=shell, cwd=self.path)
        try:
            outs, errs = p.communicate()
            if p.returncode:
                print('Invalid Reversion')
                print(outs)
                raise CalledProcessError(p.returncode, cmd) from None
        except TimeoutExpired:
            p.kill()
            raise RuntimeError("Timeout during get git commits") from None
        outs = unicodedata.normalize(u'NFKD', outs.decode(encoding="utf-8", errors="ignore"))
        return outs
