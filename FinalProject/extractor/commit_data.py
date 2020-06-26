#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Extracting commit level and code level data

1. Main process:
1) Randomly select the sample from all the fix-bug commits. (Sample size = 1000)
2) Get the feature of the Bug-Fix commit
3) Get the code of the bug commit
4) Store the result

2. Result (DataFrame):
1) fix_distance (Mean)
The number of commits between Bug commit and Fix commit
2) find_bug_time (Mean)
The time difference (Seconds) between commit which is the first find the bug and the Bug commit
3) fix_bug_time (Mean)
The time difference (Seconds) between Bug commit and Fix commit

"""

__author__ = "Group No.18 in DSP of Lanzhou University: Yuming Chen, Huiyi Liu, Jiyang Xing, Qiaoyuan Yang, Shijie Ma"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__maintainer__ = "Yuming Chen"
__email__ = ["chenym18@lzu.edu.cn", "liuhuiyi18@lzu.edu.cn","xinjy18@lzu.edu.cn","yangqy2018@lzu.edu.cn"," mashj2018@lzu.edu.cn"]
__status__ = "Experimental"

import json
import time
import random
import pandas as pd
from tools import CommitsFeatureExtractor, error_log


bug_fix = json.load(open('../data/rdata/prepare_data/all_fix_bug_commit@202006220401.json', 'r'))
result = pd.DataFrame(columns=['bug', 'fix', 'fix_distance', 'find_bug_time', 'fix_bug_time'])

# Select sample
seed = 0
random.seed(seed)
sample = random.sample(list(bug_fix.keys()), 1000)

store_path = '../data/rdata/code&commit/commit_{}.csv'.format(seed)
code_dir = '../data/rdata/code&commit/code_content_{}/'.format(seed)

for bug in sample:
    tmp = {}
    fix = bug_fix[bug]
    try:
        extractor = CommitsFeatureExtractor(bug, fix)
        commit_lists = extractor.get_commits_lists()
        if len(commit_lists) == 0:
            raise Exception
        code = extractor.get_code()
        fix_distance = extractor.get_fix_distance()
        find_bug_time = extractor.get_find_time()
        fix_bug_time = extractor.get_fix_time()
        tmp['bug'] = bug
        tmp['fix'] = fix
        tmp['fix_distance'] = fix_distance
        tmp['find_bug_time'] = find_bug_time
        tmp['fix_bug_time']= fix_bug_time
        with open(code_dir+'{}'.format(bug),'w') as f:
            f.write(code)
        result = result.append([tmp], ignore_index=True)
    except Exception as err:
        error_message = """{time} - Error: {err}\n Happen in: Bug commit-{bug} , Fix commit-{fix}\n""".format(time=time.strftime('%a %b %d %H:%M:%S %Y %z',time.localtime()),err=str(err),bug=bug,fix=fix)
        error_log(error_message)
    finally:
        result.to_csv(store_path, encoding='utf-8', index=False)










