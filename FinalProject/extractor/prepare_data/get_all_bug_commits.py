#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a preparation for data extracting.

1. Intend:
1) To reduce the time complexity
-> This is because Fix commit --> Bug commit
-> But the commit we get is bug commit, we need to find the fix commit
-> The time complexity is high when we use travel
Therefore, we decide to sacrifice space to store all of the "Fix commit --> Bug commit"
into json(dict) format which we can use the key(bug commit) to find the value(fix commit) directly

2) Make easy to reuse
The result will dump into the json file
It maintains the dict format and easy to reuse
Moreover, reduce the space complexity in some degree
"""

__author__ = "Group No.18 in DSP of Lanzhou University: Yuming Chen, Huiyi Liu, Jiyang Xing, Qiaoyuan Yang, Shijie Ma"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__maintainer__ = "Yuming Chen"
__email__ = ["chenym18@lzu.edu.cn", "liuhuiyi18@lzu.edu.cn","xinjy18@lzu.edu.cn","yangqy2018@lzu.edu.cn"," mashj2018@lzu.edu.cn"]
__status__ = "Experimental"
import sys
import os
import json
os.chdir('..')
sys.path.append('.')
from tools import get_all_fix_bug_commits


if __name__ == '__main__':
    # Record the time stamp because it is dynamic
    time = '202006220401'
    store_path = '../data/rdata/prepare_data/all_fix_bug_commit@{}.json'.format(time)
    fix_bug_commits = get_all_fix_bug_commits()
    json.dump(fix_bug_commits, open(store_path, 'w'))

