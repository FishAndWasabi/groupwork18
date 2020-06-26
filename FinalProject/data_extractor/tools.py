#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module is the tools


"""

__author__ = "Group No.18 in DSP of Lanzhou University: Yuming Chen, Huiyi Liu"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__version__ = "0.1"
__maintainer__ = ["Yuming Chen", "Huiyi Liu"]
__email__ = ["chenym18@lzu.edu.cn", "liuhuiyi18@lzu.edu.cn"]
__status__ = "Experimental"

import re
import json
from datetime import datetime
from repo import Rep
PATH = 'linux-stable'
REP = Rep(PATH)

COMMIT = re.compile('^commit [0-9a-z]{40}$', re.IGNORECASE)
FIX = re.compile('^\W+Fixes: [a-f0-9]{8,40} \(.*\)$', re.IGNORECASE)
POSITION = re.compile('^@@ -\d+[,]*\d+ \+\d+[,]*\d+ @@', re.IGNORECASE)
FILE_NAME = re.compile('^diff --git ', re.IGNORECASE)
DATE = re.compile('^Date:   .*', re.IGNORECASE)

def get_all_fix_bug_commits():
    cmd = ["git", "log", "-P", "--no-merges"]
    data = REP.execute(cmd, False)
    fix_bug_commits = {}
    count = 0
    for line in data.split("\n"):
        if COMMIT.match(line):
            cur_commit = line[7:]
        if FIX.match(line):
            count += 1
            line = line.strip()
            index = line.find('(')
            bug_commit = line[7:index].rstrip()
            fix_bug_commits[bug_commit] = cur_commit
    print('All fix commits are collected, total:', count)
    return fix_bug_commits


def get_all_author():
    cmd = ["git", "log", '--pretty=format:"%an&%h" ', "--no-merges"]
    data = REP.execute(cmd, False)
    authors = {}
    for line in data.split('\n'):
        line = line.replace('\"','')
        author = line.split('&')[0]
        commit = line.split('&')[1].rstrip()
        authors[author] = authors.get(author,[]) + [commit]
    print('All authors are collected, total:', len(data.split('\n')))
    return authors


class CommitsFeatureExtractor:
    def __init__(self, bug, fix):
        self.__bug = bug
        self.__fix = fix
        self.__commit_lists = []
        self.__path_position_dict = {}

    def __path_position(self):
        cmd = ["git", "show", self.__fix]
        data = REP.execute(cmd, False)
        for line in data.split('\n'):
            if FILE_NAME.match(line):
                path = line[FILE_NAME.match(line).span()[1]:].split(' ')
                path = path[1][2:]
                if path not in self.__path_position_dict:
                    self.__path_position_dict[path] = []
            if POSITION.match(line):
                position = POSITION.match(line).group(0)
                for i in '@-+':
                    position = position.replace(i, '')
                position = position.strip().split(' ')[0].split(',')
                self.__path_position_dict[path].append(position)

    def __commit_list(self, data):
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
        cmd = ['git', 'show', self.__bug]
        bug_data = REP.execute(cmd, False).split('\n')
        codes = ''
        for index in range(len(bug_data)):
            if POSITION.match(bug_data[index]):
                code = bug_data[index][POSITION.match(bug_data[index]).span()[1]:].strip()
                index += 1
                while index <= len(bug_data) - 1 and not (
                        FILE_NAME.match(bug_data[index]) or POSITION.match(bug_data[index])):
                    code += bug_data[index][1:] + '\n'
                    index += 1
                codes += code + '\n'
        return codes

    def get_commit_lists(self):
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
                cmd = 'git log  -L {x},+{y}:{path} {fix}...{bug} -- {path}'.format(x=position[0], y=position[1],
                                                                                   path=path, fix=self.__fix,
                                                                                   bug=self.__bug)
                data = REP.execute(cmd, True)
                if not data:
                    continue
                commit_list = self.__commit_list(data)
                commit_list.append(bug_info)
                commit_lists.append(commit_list)
        self.__commit_lists = commit_lists
        return commit_lists

    def get_fix_time(self):
        if not self.__commit_lists:
            self.get_commit_lists()
        time_diff = 0
        for commit_list in self.__commit_lists:
            time_diff += (commit_list[0][1] - commit_list[-1][1]).total_seconds()
        time_diff = time_diff / len(self.__commit_lists)
        return time_diff

    def get_fix_distance(self):
        if not self.__commit_lists:
            self.get_commit_lists()
        fix_distance = 0
        for commit_list in self.__commit_lists:
            fix_distance += len(commit_list) - 1
        fix_distance = fix_distance / len(self.__commit_lists)
        return fix_distance

    def get_find_time(self):
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
