#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
These are solutions for the two challenges in class.
"""

__author__ = "Group No.18 in DSP of Lanzhou University"
__copyright__ = "Copyright 2020, Study Project in Lanzhou University , China"
__license__ = "GPL V3"
__version__ = "0.1"
__email__ = ["chenym18@lzu.edu.cn"]
__status__ = "Experimental"

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('v4.4.csv',comment="#",header=0,index_col="lv")
# Challenge 1
df.insert(1,'diff',df['hour'] - df['hour'].shift(1).fillna(value=0))

# Challenge 2
df['diff'].hist(bins=15)
plt.show()

