import git
import pandas as pd
import re


class Rep:
    def __init__(self, path):
        self.r = git.Git(path)

    def gitFileDynamics(self, fileName, kernelRange):
        cmd = ' '.join(["git", "-P", "log", "--stat", "--oneline", "--follow", kernelRange, fileName])
        data = self.r.execute(cmd).split('\n')
        lines = []
        num = 0
        for line in data[::3]:
            # b3e0b1b6d841
            hashid = line.split(' ')[0]
            # "locking, sched: Introduce smp_cond_acquire() and use it"
            desc = '"%s"' % (' '.join(line.split(' ')[1:]))
            # filename
            fileName = data[num + 1].split('|')[0]
            # insertions
            pattern = re.compile(r'\d+ insertions|\d+ insertion')
            count = re.search(pattern, data[num + 2]).group().split(' ')[0]
            lines.append([hashid,desc,fileName,count])
            num += 3

        df = pd.DataFrame(columns=['HashNum','Description','FileName','Insertion'],data=lines)
        return df


r = Rep('linux')
df = r.gitFileDynamics("kernel/sched/core.c", "v4.4..v4.5")
print(df.info)
