#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains several tools which are used in the process of data extracting

The major tools are:
1. Function - "get_all_fix_bug_commits"
1.1 Use in:
data_extractor/prepare_data/get_all_bug_commits.py

2. Function - "get_all_author"
2.1 Use in:
data_extractor/prepare_data/get_all_author.py

3. Class - "CommitsFeatureExtractor"
3.1 Use in:
data_extractor/commit_data.py
data_extractor/author_data.py

3.2 Methods:
3.2.1 Private:
1) "__commit_list" use in "get_commits_lists"
2) "__path_position" use in "get_commits_lists"

3.2.2 Public:
1) get_code
2) get_commits_lists
3) get_fix_time
4) get_find_time
5) get_fix_distance

4. Function - "error_log"
"""

__author__ = "Group No.18 in DSP of Lanzhou University: Yuming Chen, Huiyi Liu"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__version__ = "0.1"
__maintainer__ = ["Yuming Chen"]
__email__ = ["chenym18@lzu.edu.cn", "liuhuiyi18@lzu.edu.cn", "", "", ""]
__status__ = "Experimental"

import re
from datetime import datetime
from repo import Rep

# Init "Rep" class
PATH = 'linux-stable'
REP = Rep(PATH)

# Regular Expressions
# e.g. "commit 1da8347d8505c137fb07ff06bbcd3f2bf37409bc"
COMMIT = re.compile('^commit [0-9a-z]{40}$', re.IGNORECASE)

# e.h. "Fixes: ee2636b8670b1 ("iommu/vt-d: Enable base Intel IOMMU debugfs support")"
BUG_COMMIT = re.compile('^\W+Fixes: [a-f0-9]{8,40} \(.*\)$', re.IGNORECASE)

# The position where the code be modified
# e.g. "@@ -282,9 +282,16 @@"
POSITION = re.compile('^@@ -\d+[,]*\d+ \+\d+[,]*\d+ @@', re.IGNORECASE)

# The file path  where the commit point to
# e.g. "diff --git a/drivers/iommu/intel-iommu-debugfs.c b/drivers/iommu/intel-iommu-debugfs.c"
FILE_PATH = re.compile('^diff --git ', re.IGNORECASE)

# e.g. "Date:   Sat Mar 14 11:39:59 2020 +0800"
DATE = re.compile('^Date:   .*', re.IGNORECASE)

LOG_PATH = 'log'


def error_log(message: str):
    """
    Record error message when data extracting
    """
    print(message)
    with open(LOG_PATH, 'a+') as f:
        f.write(message)


def get_all_fix_bug_commits():
    """
    Describe:
    1. Get all the hash ID of commits which have Fix tag
    and the hash ID of commits which be pointed to by Fix tag.
    2. Store the result into dict -> easy to dump into json file
    { bug commit : fix commit }
    """
    cmd = ["git", "log", "-P", "--no-merges"]
    data = REP.execute(cmd, False)
    fix_bug_commits = {}
    count = 0
    for line in data.split("\n"):
        # Check if the line is the hash ID of current commit
        # "commit 1da8347d8505c137fb07ff06bbcd3f2bf37409bc"
        if COMMIT.match(line):
            cur_commit = line[7:]
        # Check if the line is the hash ID of bug commit which is pointed by current commit
        # "Fixes: ee2636b8670b1 ("iommu/vt-d: Enable base Intel IOMMU debugfs support")"
        if BUG_COMMIT.match(line):
            count += 1
            line = line
            index = line.find('(')
            bug_commit = line[7:index].rstrip()
            fix_bug_commits[bug_commit] = cur_commit
    print('All fix commits are collected, total:', count)
    return fix_bug_commits


def get_all_author():
    """
    Describe:
    1. Get all of the authors in linx-stable and the hash ID of their commits
    2. Store the result into dict  -> easy to dump into json file
    { author : [commits] }
    3. Use --pretty=format:"%an&%h" as git shell
    1) %h: Short Hash ID make it easy to search.
        Because the bug commit which is pointed by current commit is short ID.
    2) &: Make it easy to split the author name and hash ID.
    """
    cmd = ["git", "log", '--pretty=format:"%an&%h"', "--no-merges"]
    data = REP.execute(cmd, False)
    # The result of git commit:
    # "Linus Torvalds&b3a9e3b9622a"
    authors = {}
    for line in data.split('\n'):
        line = line.replace('\"', '')
        author = line.split('&')[0]
        commit = line.split('&')[1].rstrip()
        authors[author] = authors.get(author, []) + [commit]
    print('All authors are collected, total:', len(data.split('\n')))
    return authors


class CommitsFeatureExtractor:
    """
    Describe:
    This is a class to get the features of fix-bug commits
    """
    def __init__(self, bug: str, fix: str):
        """
        Describe:
        Init the extractor

        Argus:
        1. bug: The hash ID of Bug commit
        2. fix: The hash ID of Fix commit
                Fix commit -> Bug commit
        """
        self.__bug = bug
        self.__fix = fix
        self.__commit_lists = []
        self.__path_position_dict = {}

    def __path_position(self):
        """
        Describe:
        1. Get the paths of files whose change was signed by Fix commit
        2. Get the position(line) of file whose change was signed by Fix commit
        3. Store the result into private attribute -> self.__path_position_dict
        { path: [ positions ]}
        """
        cmd = ["git", "show", self.__fix]
        data = REP.execute(cmd, False)
        for line in data.split('\n'):
            # Check if the line is the file path
            # "diff --git a/drivers/iommu/intel-iommu-debugfs.c b/drivers/iommu/intel-iommu-debugfs.c"
            if FILE_PATH.match(line):
                # Divide into "a/drivers/iommu/intel-iommu-debugfs.c" and "b/drivers/iommu/intel-iommu-debugfs.c"
                path = line[FILE_PATH.match(line).span()[1]:].split(' ')
                # The first is the workspace file, second is the Local library file
                # We think use second path is better
                path = path[1][2:]
                if path not in self.__path_position_dict:
                    self.__path_position_dict[path] = []
            # Check if the line is "@@ -282,9 +282,16 @@"
            if POSITION.match(line):
                position = POSITION.match(line).group(0)
                # Remove symbol
                for i in '@-+':
                    position = position.replace(i, '')
                # Divide into -282,9 and +282,16
                # The first position is before change, second is after change
                # We use first path is better
                position = position.strip().split(' ')[0].split(',')
                self.__path_position_dict[path].append(position)

    def __commit_list(self, data):
        """
        Describe:
        1. Get the hash ID of given commit
        2. Get the date of given commit
        3. Store the result is a list [(commit,date)]
        """
        commit_list = []
        for line in data.split("\n"):
            if COMMIT.match(line):
                commit = line[7:]
            if DATE.match(line):
                date = line[8:]
                date = datetime.strptime(date, "%a %b %d %H:%M:%S %Y %z")
                commit_list.append((commit, date))
        return commit_list

    def get_code(self):
        """
        Describe:
        1. Get the code of Bug commit
        2. The code of commit's format:
        @@ -282,9 +282,16 @@
                    ...
                    code
                    ...
        @@ -425,6 +432,7 @@ or diff --git a/drivers/iommu/intel-iommu-debugfs.c b/drivers/iommu/intel-iommu-debugfs.c
                    ...
                    code
                    ...
        """
        cmd = ['git', 'show', self.__bug]
        bug_data = REP.execute(cmd, False).split('\n')
        codes = ''
        for index in range(len(bug_data)):
            if POSITION.match(bug_data[index]):
                code = bug_data[index][POSITION.match(bug_data[index]).span()[1]:].strip()
                index += 1
                while index <= len(bug_data) - 1 and not (
                        FILE_PATH.match(bug_data[index]) or POSITION.match(bug_data[index])):
                    code += bug_data[index][1:] + '\n'
                    index += 1
                codes += code + '\n'
        return codes

    def get_commit_lists(self):
        """
        Describe:
        1. Get the commit list (Not only one list) between the Fix commit and the Bug commit
        2. Store the result into list [ [ (fix commit, time),...,(bug commit, time)],[ (fix commit, time),...,(bug commit, time)]...]
        """
        if self.__commit_lists:
            return self.__commit_lists
        self.__path_position()
        cmd = ['git', 'show', self.__bug]
        bug_data = REP.execute(cmd, False)
        bug_info = self.__commit_list(bug_data)[0]
        commit_lists = []
        for path in self.__path_position_dict:
            positions = self.__path_position_dict[path]
            for position in positions:
                # Firstly we try to use the function name as a flag to build the git shell
                # But most of code do not have function name
                # Therefore, we choose set line position as a flag
                cmd = 'git log  -L {x},+{y}:{path} {fix}...{bug} -- {path}'.format(x=position[0], y=position[1],path=path, fix=self.__fix,bug=self.__bug)
                data = REP.execute(cmd, True)
                if not data:
                    continue
                commit_list = self.__commit_list(data)
                commit_list.append(bug_info)
                commit_lists.append(commit_list)
        self.__commit_lists = commit_lists
        return commit_lists

    def get_fix_time(self):
        """
        Describe:
        1. Calculate the time difference between the Fix commit and the Bug commit
        2. The result is average = time_diff/number_commits
        """
        if not self.__commit_lists:
            self.get_commit_lists()
        time_diff = 0
        for commit_list in self.__commit_lists:
            time_diff += (commit_list[0][1] - commit_list[-1][1]).total_seconds()
        time_diff = time_diff / len(self.__commit_lists)
        return time_diff

    def get_fix_distance(self):
        """
        Describe:
        1. Calculate the number of commits between the Fix commit and the Bug commit
        (Include Fix commit, Not include Bug commit)
        2. The result is average = fix_distance/number_commits
        """
        if not self.__commit_lists:
            self.get_commit_lists()
        fix_distance = 0
        for commit_list in self.__commit_lists:
            fix_distance += len(commit_list) - 1
        fix_distance = fix_distance / len(self.__commit_lists)
        return fix_distance

    def get_find_time(self):
        """
        Describe:
        1. Calculate the time difference between the first commit in the commits list and the Bug commit
        2. The result is average = time_diff/number_commits
        """
        if not self.__commit_lists:
            self.get_commit_lists()
        time_diff = 0
        for commit_list in self.__commit_lists:
            time_diff += (commit_list[-2][1] - commit_list[-1][1]).total_seconds()
        time_diff = time_diff / len(self.__commit_lists)
        return time_diff


if __name__ == '__main__':
    fix = '1da8347d8505c137fb07ff06bbcd3f2bf37409bc'
    bug = 'ee2636b8670b1'
    extractor = CommitsFeatureExtractor(bug, fix)
    print(extractor.get_commit_lists())
    print(extractor.get_find_time())
    print(extractor.get_fix_distance())
    print(extractor.get_fix_time())
    print(extractor.get_code())
