#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Group No.18 in DSP of Lanzhou University: Yuming Chen, Huiyi Liu, Jiyang Xing, Qiaoyuan Yang, Shijie Ma"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__maintainer__ = "Yuming Chen"
__email__ = ["chenym18@lzu.edu.cn", "liuhuiyi18@lzu.edu.cn", "xinjy18@lzu.edu.cn", "yangqy2018@lzu.edu.cn",
             " mashj2018@lzu.edu.cn"]
__status__ = "Experimental"

import os
import unicodedata
from subprocess import Popen, PIPE, DEVNULL
from subprocess import CalledProcessError, TimeoutExpired


class InvalidPathError(EnvironmentError):
    pass


class Rep:
    """
    Describe:
    1. "Rep" class is to represent the git repository
    2. "execute" can run the command in the git repository

    Doctest:
    >>> rep = Rep('a')
    Traceback (most recent call last):
        ...
    repo.InvalidPathError
    >>> rep = Rep('linux-stable')
    >>> rep.execute('a',True)
    Traceback (most recent call last):
        ...
    subprocess.CalledProcessError: Command 'a' returned non-zero exit status 1.
    >>> rep.execute( ["git", "log", '--pretty=format:"%an&%h"', "--no-merges","-3"],False)
    '"Linus Torvalds&b3a9e3b9622a"\n"Thomas Cedeno&39030e1351aa"\n"David Sterba&55e20bd12a56"'
    """

    def __init__(self, path: str):
        """
        Describe:
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

    def execute(self, cmd: str or list, shell: bool):
        """
        Describe:
        1. Run the git command and return the output.
        2. Deal with the timeout error and Catch the invalid reversion number.
        """
        p = Popen(cmd, stdout=PIPE, stderr=DEVNULL, shell=shell, cwd=self.path)
        try:
            outs, errs = p.communicate()
            if p.returncode:
                raise CalledProcessError(p.returncode, cmd) from None
        except TimeoutExpired:
            p.kill()
            raise RuntimeError("Timeout during get git commits") from None
        outs = unicodedata.normalize(u'NFKD', outs.decode(encoding="utf-8", errors="ignore"))
        return outs
