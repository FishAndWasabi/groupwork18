# /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is
"""

__author__ = "Group No.18 in DSP of Lanzhou University"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__version__ = "0.1"
__maintainer__ = "Yuming Chen, Huiyi Liu"
__email__ = "Chenym18@lzu.edu.cn"
__status__ = "Experimental"

import git
import pandas as pd
import re


class Rep:
    def __init__(self, path):
        self.rep = git.Git(path)

    def gitFileDynamics(self, fileName, kernelRange):
        cmd = ["git", "-P", "log", "--stat", "--oneline", "--follow", kernelRange, fileName]
        data = self.rep.execute(cmd).split('\n')
        lines = []
        num = 0
        for line in data[::3]:
            # b3e0b1b6d841
            hashid = line.split(' ')[0]
            # "locking, sched: Introduce smp_cond_acquire() and use it"
            desc = '"%s"' % (' '.join(line.split(' ')[1:]))
            # filename
            fileName = data[num + 1].split('|')[0]
            # insertions
            pattern = re.compile(r'\d+ insertions|\d+ insertion')
            count = re.search(pattern, data[num + 2]).group().split(' ')[0]
            lines.append([hashid, desc, fileName, count])
            num += 3

        df = pd.DataFrame(columns=['HashNum', 'Description', 'FileName', 'Insertion'], data=lines)
        return df


if __name__ == "__main__":
    path = '..\linux'
    r = git.Repo(path)
    print(r.git.log())
