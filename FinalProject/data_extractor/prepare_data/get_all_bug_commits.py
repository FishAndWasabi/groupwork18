#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Group No.18 in DSP of Lanzhou University: Yuming Chen, Huiyi Liu"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__version__ = "0.1"
__maintainer__ = ["Yuming Chen", "Huiyi Liu"]
__email__ = ["chenym18@lzu.edu.cn","liuhuiyi18@lzu.edu.cn"]
__status__ = "Experimental"
import sys
import os
import json
os.chdir('..')
sys.path.append('.')
from tools import get_all_fix_bug_commits




if __name__ == '__main__':
    time = '202006220401'
    store_path = '../data/prepare_data/all_fix_bug_commits@{}.json'.format(time)
    fix_bug_commits = get_all_fix_bug_commits()
    json.dump(fix_bug_commits, open(store_path, 'w'))

