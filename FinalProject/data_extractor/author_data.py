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



bug_fixs = json.load(open('../data/prepare_data/all_fix_bug_commits@202006220401.json','r'))
authors = json.load(open('../data/prepare_data/all_author@202006220401.json','r'))
samples = pd.read_csv('../data/prepare_data/sample_author.csv',index_col=None)

result = pd.DataFrame(columns=['author','number_commits','avg_fix_distance','avg_find_bug_time','avg_fix_bug_time'])
for author in samples['author'][::-1]:
    try:
        tmp = {}
        commits = authors.get(author,None)
        if not commits:
            continue
        print(author)
        tmp['author'] = author
        tmp['number_commits'] = len(commits)
        for commit in commits:
            fix = bug_fixs.get(commit,None)
            if not fix:
                continue
            extractor = CommitsFeatureExtractor(commit,fix)
            tmp['avg_fix_distance'] = tmp.get('avg_fix_distance', 0) + extractor.get_fix_distance()
            tmp['avg_find_bug_time'] = tmp.get('avg_find_bug_time', 0) + extractor.get_find_time()
            tmp['avg_fix_bug_time'] = tmp.get('avg_fix_bug_time', 0) + extractor.get_fix_time()
        tmp['avg_fix_distance'] = tmp.get('avg_fix_distance', 0)/tmp['number_commits']
        tmp['avg_find_bug_time'] = tmp.get('avg_find_bug_time', 0) / tmp['number_commits']
        tmp['avg_fix_bug_time'] = tmp.get('avg_fix_bug_time', 0) / tmp['number_commits']
        result = result.append([tmp], ignore_index=True)
        print(result.shape)
    except Exception as err:
        error_message = """
                    {time}
                    Error: {err}
                    Happen in: author-{author}
                    ---------------------------------------------------
                    """.format(time=time.strftime('%a %b %d %H:%M:%S %Y %z', time.localtime()), err=str(err),
                               author=author)
        print(error_message)
    finally:
        result.to_csv('../data/sample_authors.csv',encoding='utf-8', index=False)
