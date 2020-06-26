#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""



"""
__author__ = "Group No.18 in DSP of Lanzhou University: Yuming Chen, Huiyi Liu"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__version__ = "0.1"
__maintainer__ = ["Yuming Chen", "Huiyi Liu"]
__email__ = ["chenym18@lzu.edu.cn", "liuhuiyi18@lzu.edu.cn"]
__status__ = "Experimental"


import json
import time
import random
import pandas as pd
from tools import CommitsFeatureExtractor


seed = 0
bug_fixs = json.load(open('../data/prepare_data/all_fix_bug_commits@202006220401.json','r'))
df = pd.DataFrame(columns=['bug','fix','fix_distance','find_bug_time','fix_bug_time'])
random.seed(seed)
sample = random.sample(list(bug_fixs.keys()), 1000)

for bug in sample:
    tmp = {}
    fix = bug_fixs[bug]
    try:
        extractor = CommitsFeatureExtractor(bug, fix)
        commit_lists = extractor.get_commit_lists()
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
        with open('../data/codes/{}'.format(bug),'w') as f:
            f.write(code)
        df = df.append([tmp],ignore_index=True)
    except Exception as err:
        error_message = """
        {time} 
        'Error: ' + {err} 
        Happen in: Bug commit-{bug} , Fix commit-{fix} 
        ---------------------------------------------------
        """.format(time=time.strftime('%a %b %d %H:%M:%S %Y %z',time.localtime()),err=str(err),bug=bug,fix=fix)
        print(error_message)
    finally:
        df.to_csv('../data/sample_commits@{}.csv'.format(seed),encoding='utf-8', index=False)










