#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Extracting author level data

1. Main process:
1) Get author name from sample list
2) Get hash ID of the commits from authors dict "{author:[commits]}" for each author
3) Get hash ID of fix commit from bug-fixes dict "{bug:fix}" for each commit
4) Get the feature of the commit
5) Store the result

2. Result (DataFrame):
1) commit_number
The number of all commits
2) bug_commits_number
The number of commits which are pointed by the Fix commit
3) total_fix_distance
The sum of bug commits' fix distance
4) total_find_bug_time
The sum of bug commits' find time
5) total_fix_bug_time
The sum of bug commits' fix time

"""

__author__ = "Group No.18 in DSP of Lanzhou University: Yuming Chen, Huiyi Liu, Jiyang Xing, Qiaoyuan Yang, Shijie Ma"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__maintainer__ = "Yuming Chen"
__email__ = ["chenym18@lzu.edu.cn", "liuhuiyi18@lzu.edu.cn","xinjy18@lzu.edu.cn","yangqy2018@lzu.edu.cn"," mashj2018@lzu.edu.cn"]
__status__ = "Experimental"

import json
import time
import pandas as pd
from tools import CommitsFeatureExtractor, error_log

# Init param
store_path = '../data/rdata/author_level/sample_author@1.1.csv'

columns = ['author', 'commits_number','bug_commits_number','total_fix_distance', 'total_find_bug_time', 'total_fix_bug_time']
samples = pd.read_csv('../data/rdata/author_level/author@1.1.csv', index_col=None)

bug_fixes = json.load(open('../data/rdata/prepare_data/all_fix_bug_commit@202006220401.json', 'r'))
authors = json.load(open('../data/rdata/prepare_data/all_author@202006220401.json', 'r'))
# Init DataFrame
result = pd.DataFrame(columns=columns)

# Main process
for author in samples['author']:
    try:
        tmp = {}
        commits = authors.get(author, None)
        if not commits:
            continue
        count = 0
        for commit in commits:
            fix = bug_fixes.get(commit, None)
            if not fix:
                continue
            extractor = CommitsFeatureExtractor(commit, fix)
            tmp['total_fix_distance'] = tmp.get('total_fix_distance', 0) + extractor.get_fix_distance()
            tmp['total_find_bug_time'] = tmp.get('total_find_bug_time', 0) + extractor.get_find_time()
            tmp['total_fix_bug_time'] = tmp.get('total_fix_bug_time', 0) + extractor.get_fix_time()
            count += 1
        tmp['bug_commits_number'] = count
        tmp['author'] = author
        tmp['commits_number'] = len(commits)
        result = result.append([tmp], ignore_index=True)
        print('No.{id} {author} complete'.format(id=result.shape[0],author=author))
    except Exception as err:
        # Prevent unexpected Error which cause stop.
        error_message = "{time} - Error: {err}\nHappen in: {author}\n".format(time=time.strftime('%a %b %d %H:%M:%S %Y %z', time.localtime()), err=str(err), author=author)
        error_log(error_message)
    finally:
        result.to_csv(store_path, encoding='utf-8', index=False)
