#!/usr/bin/env python3
"""页壳：从 chapters/01b.html 剥出空页壳（保留九个 h2、今天怎么看的图例、空的 TEXT 标记）。
用法（在 republic/ 下）：python3 -I tools/new_shell.py 03a 03b …（按顺序，标题写「第N卷（k/总数）」，卷名、总数要改下面一行）。之后 gen_text.py --en-only 先填英文。"""
import re,sys
src=open('chapters/01b.html').read()
for k,pid in enumerate(sys.argv[1:],1):
    s=src.replace('第一卷（2/4）',f'第五卷（{k}/{len(sys.argv)-1}）').replace('data-page="01b"',f'data-page="{pid}"')
    head,rest=s.split('<main>\n',1); body,tail=rest.split('</main>',1)
    parts=re.split(r'(?=<h2 id=")',body)
    out=[parts[0]]
    for p in parts[1:]:
        h2=p.split('\n',1)[0]; sid=re.match(r'<h2 id="(\w+)"',h2).group(1)
        if sid=='fulltext':
            c1,c2=p.split('\n')[1:3]
            c1=c1.replace('01b',pid); c2=c2.replace('01b',pid)
            out.append(f'{h2}\n{c1}\n{c2}\n<!-- TEXT:END -->\n')
        elif sid=='today':
            keep=[l for l in p.split('\n')[1:] if l.startswith('<p class="lede">') or l.startswith('<ul class="verdicts">')]
            out.append(h2+'\n'+'\n'.join(keep)+'\n<p class="wip">待写</p>\n\n')
        else:
            out.append(h2+'\n<p class="wip">待写</p>\n\n')
    open(f'chapters/{pid}.html','w').write(head+'<main>\n'+''.join(out)+'</main>'+tail)
