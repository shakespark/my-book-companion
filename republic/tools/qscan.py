#!/usr/bin/env python3
"""引号扫描（切页前跑）：python3 -I tools/qscan.py source/text/NN.txt。双引号嵌套、缺开 / 收引号、「said I, 小写」漏开引号都打印出来；没输出就是干净的。修在 extract.py 的 FIXES。"""
import re,sys
t=open(sys.argv[1]).read()
t2=re.sub(r'\[\d+[a-e]\] ?','',t)
t2=re.sub(r'\[\^\d+\]','',t2)
depth=0;last=0
for m in re.finditer(r'[“”]',t2):
    i=m.start();c=m.group()
    ctx=t2[max(0,i-60):i+60].replace('\n',' ')
    if c=='“':
        if depth==1: print('OPEN-IN-OPEN:',ctx)
        depth=1
    else:
        if depth==0: print('CLOSE-NO-OPEN:',ctx)
        depth=0
# narration outside quotes heuristics: ', said I, ' patterns
for m in re.finditer(r'” (said|says|I said|he said|said he|said I|I replied|he replied|I asked)[^“”]{0,15}?, [a-z]',t2):
    print('MISSING-REOPEN?:',t2[m.start()-40:m.end()+40].replace('\n',' '))
for m in re.finditer(r'[a-z,] (said I|said he|he said|I said),? [A-Za-z]',t2):
    s=t2[max(0,m.start()-50):m.end()+30]
    print('NARR-NO-QUOTE?:',s.replace('\n',' '))
