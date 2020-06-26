#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Group No.18 in DSP of Lanzhou University: Yuming Chen, Huiyi Liu"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__version__ = "0.1"
__maintainer__ = ["Yuming Chen"]
__email__ = ["chenym18@lzu.edu.cn"]
__status__ = "Experimental"

import os
from subprocess import Popen, PIPE, DEVNULL
from subprocess import CalledProcessError, TimeoutExpired
from pandas import DataFrame


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
            outs, errs = p.communicate(timeout=100)
            if p.returncode:
                raise CalledProcessError(p.returncode, cmd) from None
        except TimeoutExpired:
            p.kill()
            raise RuntimeError("Timeout during get git commits") from None
        return outs.decode("latin")


def count(lines):
    counts = {}
    commits = {}
    for line in lines.split('\n'):
        line = line.replace('"', '')
        commit = line.split(',')[0]
        author = line.split(',')[1]
        commits[commit] = author
        counts[author]= counts.get(author,0) +1
    results = [(commit, commits[commit], counts[commits[commit]]) for commit in commits]
    return DataFrame(data=results, columns=['commit', 'author', 'total_commit_count_of_that_author'])


if __name__ == '__main__':
    rep = Rep('../../linux-stable')
    lines = rep.execute(['git','log','--no-merges','--pretty=format:"%h, %an"'],False)
    df = count(lines)
    print(df)
