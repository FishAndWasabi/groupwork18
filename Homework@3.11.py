#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
get the commit count per sublevel pointwise or cumulative (c)
arguments is the tag as displayed by git tag and the number
of sublevels to be counted. If count is out of range for a
specific sublevel it will terminate the loop

Fix list:
1. Add specific Exception class (rewrite)
2. Use "argparse" to handel arguments
3. Add error handling to catch the invalid reversion, invalid git repository and invalid reversion range
4. Restructure the code into two class: "Counter" and "Rep"
5. Complete the documentation
6. Add header in this file
7. Change some detail codes
"""

__author__ = "Group No.18 in DSP of Lanzhou University"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__version__ = "0.1"
__maintainer__ = "Yuming Chen"
__email__ = "Chenym18@lzu.edu.cn"
__status__ = "Experimental"

import os, re, time
import argparse
from subprocess import Popen, PIPE, DEVNULL
from subprocess import CalledProcessError, TimeoutExpired
import pandas as pd


class InvalidRevError(Exception):
    pass
class InvalidRangeError(Exception):
    pass
class InvalidPathError(EnvironmentError):
    pass


def getArg():
    """
    "argparse" is much better and more comprehensive than the "sys".
    It can limit the arguments type and give the Info of each argument.
    Returns:
        args: A dict storing arguments
    """
    parser = argparse.ArgumentParser(description="Count the commit")
    parser.add_argument('-p', '--path', metavar='DIR', default='../linux/', help='path to Git Repository')
    parser.add_argument('-r', '--rev', type=str, default='v4.4', help='First Reversion')
    parser.add_argument('-b', '--base', type=str, default='v4.4', help='Base Reversion')  # Not sure to do that
    parser.add_argument('-g', '--rev-range', type=int, default=10, help='Range of Reversion')
    # Use boolean replace 1 0
    parser.add_argument('-c', '--cumulative', action='store_true', default=False, help='Enable cumulative arguments')
    return parser.parse_args()


class Counter:
    """
    "Counter" class contain the four methods.
    "execute" is the method to start the Counter main process.
    "get_tag_days","setupTable" and "get_commit_cnt" are the methods which serve as tools for Counter
    """

    def __init__(self, args):
        """
        Init Arguments
        Args:
            args: Arguments
        """
        self.rep = Rep(args.path)  # Init "Rep" class
        self.rev = args.rev
        self.rev_range = args.rev_range
        self.cumulative = args.cumulative
        # Catch the Invalid Reversion Range Error
        self.max = self.rep.execute(["git", "tag", "|", "grep", self.rev, "|", "sort", "-n", "-k3", "-t\".\"", "-r", "|","head", "-n", "1"])
        self.max = self.max[len(self.rev + "."):]
        try:
            assert int(self.max) >= self.rev_range
        except AssertionError:
            print("Invalid Reversion Range", "Max rev %s" % self.max)
            raise InvalidRangeError
        # Extract the time of the base commit from git
        self.base = self.rep.execute(["git", "log", "-1", "--pretty=format:\"%ct\" ", args.base])
        self.result = {'lv': [], 'hour': [], 'bugs': []}

    def get_tag_days(self, git_tag_date):
        """
        Count the hours between given tag date and base tag date
        """
        SecPerHour = 3600
        return int(git_tag_date) - int(self.base) // SecPerHour

    def setupTable(self):
        """
        Create a data frame to store the count result which is much better than printing directly.
        Returns:
            title: string
            df: Table using pandas.DataFrame
        """
        df = pd.DataFrame(data=self.result)
        # Reformat the Table
        df.set_index('lv')  # Change index
        title = "#sublevel commits %s stable fixes" % self.rev  # Add title
        return title, df

    @staticmethod
    def get_commit_cnt(git_rev_list):
        """
        Count the number of bugs
        """
        cnt = re.findall('[0-9]*-[0-9]*-[0-9]*', git_rev_list)
        return len(cnt)

    def run(self):
        """
        Start counting
        """
        rev1 = self.rev + "." + "0"
        # Fill the 'result'
        for sl in range(1, self.rev_range + 1):
            rev2 = self.rev
            gitcnt = ["git", "rev-list", "--pretty=format:\"%ai\"", rev1 + "..." + rev2]
            gittag = ["git", "log", "-1", "--pretty=format:\"%ct\" ", rev2]
            git_rev_list = self.rep.execute(gitcnt)
            commit_cnt = self.get_commit_cnt(git_rev_list)
            if not self.cumulative:
                rev1 = rev2
            git_tag_date = self.rep.execute(gittag)
            days = self.get_tag_days(git_tag_date)
            self.result['lv'].append(sl)
            self.result['hour'].append(days)
            self.result['bugs'].append(commit_cnt)
        return self.setupTable()


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

    def execute(self, cmd):
        """
        Run the git command and return the output.
        Deal with the timeout error and Catch the invalid reversion number.
        """
        p = Popen(cmd, stdout=PIPE, stderr=DEVNULL, shell=True,
                  cwd=self.path)
        try:
            outs, errs = p.communicate(timeout=15)
            if p.returncode:
                print('Invalid Reversion')
                raise CalledProcessError(p.returncode, cmd) from None
        except TimeoutExpired:
            p.kill()
            raise RuntimeError("Timeout during get git commits") from None
        return outs.decode("utf-8")


if __name__ == "__main__":
    args = getArg()
    r = Counter(args)
    title, result = r.run()
    print(title)
    print(result)
