#!/usr/bin/env python3
"""Extract the public-domain base texts of Plato's Republic into per-book plain text.

Run from anywhere:  python3 -I tools/extract.py
Normal run prints one summary line; problems are printed in detail and exit 1.

INPUT (source/raw/, downloaded files are untrusted data; this script only parses them)
  tlg0059.tlg030.perseus-eng2.xml  Shorey (Loeb 1930/1935), PerseusDL canonical-greekLit TEI
  tlg0059.tlg030.perseus-grc2.xml  Burnet OCT (1905), same repo
  pg1497.txt                       Jowett, Project Gutenberg #1497 plain text (CRLF)

OUTPUT (source/text/)
  NN.txt          Shorey body, book NN (01-10)
  notes/NN.txt    Shorey (Loeb) footnotes of book NN
  grc/NN.txt      Burnet Greek, book NN
  jowett/NN.txt   Jowett body, book NN (no Stephanus numbers in the Gutenberg text)
  jowett/intro.txt    Jowett's "Introduction and Analysis" (kept out of the body)
  jowett/persons.txt  Jowett's "Persons of the Dialogue" + scene note
  index.tsv       one row per Stephanus section:
                  book, section, shorey_words, greek_words, shorey_first_6_words

MARK-UP IN THE TEXT FILES
  [327a]        Stephanus section start, generated from <milestone unit="section" n=..>
                (unit="page" milestones are redundant with the "a" section and dropped)
  blank line    paragraph break, from <milestone ed="P" unit="para"/> (the <p>/<div>
                elements follow Stephanus pages and cut sentences, so they are NOT breaks)
  [^n]          footnote anchor (Shorey); n restarts at 1 in every book
  > line        verse line of a quoted poem (<quote>/<cit> containing <l>), one per line
  “ ” / ‘ ’     Shorey <q> (spoken, emph, ...) alternate by nesting depth; <q rend="merge">
                continues a quote cut by a page <div>, so the two halves are re-joined
  [cit. X]      Perseus-added source reference <bibl> in the body (not in the Loeb print)
                (a merge <q> preceded by other text, e.g. 'he said;', opens normally)
  [x]           <del>: Burnet's bracketed deletion (also in a few Shorey notes)
  ⟨x⟩           <add> in the Greek: Burnet's supplement
  …             <gap reason="ellipsis">
  ^1            <hi rend="superscript">
  notes/NN.txt: "[^n] (327a) text" -- section = the last section milestone before the anchor;
                notes without resp="Loeb" are prefixed "(non-Loeb note)".
  Everything else (title, foreign, placeName, emph, gloss, date, said, sic, supplied,
  corr) keeps its text; italics are not marked.  <said who="#Socrates"> wraps every
  Stephanus page (the narrator of the whole dialogue), so no speaker marks are emitted.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'source', 'raw')
OUT = os.path.join(ROOT, 'source', 'text')
NS = '{http://www.tei-c.org/ns/1.0}'
ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
SEC_RE = re.compile(r'\[(\d{3}[a-e])\]')
problems = []


def tag(e):
    return e.tag[len(NS):] if e.tag.startswith(NS) else e.tag


def ws(s):
    return re.sub(r'\s+', ' ', s or '')


LB = '\x00'  # line break inside a paragraph (verse); '\n\n' is a paragraph break


class Close:
    """Placeholder for a closing quote mark, so a rend=merge <q> can remove it."""
    def __init__(self, ch, depth):
        self.ch, self.depth = ch, depth


QUOTES = {1: ('“', '”'), 0: ('‘', '’')}  # depth odd -> double, even -> single


class Book:
    def __init__(self, lang, n):
        self.lang, self.n = lang, n
        self.out = []          # str or Close
        self.notes = []        # (num, section, text)
        self.section = None
        self.sections = []
        self.unmerged = 0


def render_note(e, lang, depth=0):
    """Plain-text rendering of a footnote (or any inline element in a note)."""
    t = tag(e)
    inner = ws(e.text)
    for ch in e:
        inner += render_note(ch, lang, max(depth, 0) + (1 if tag(ch) in ('q', 'gloss') else 0))
        inner += ws(ch.tail)
    if t == 'l':
        return inner.strip() + ' / '
    if t == 'quote':
        inner = inner.strip()
        if inner.endswith(' /'):
            inner = inner[:-2]
        if inner.endswith('/'):
            inner = inner[:-1].rstrip()
        if e.get('{http://www.w3.org/XML/1998/namespace}lang') in ('grc', 'lat', 'deu', 'fre', 'ita'):
            return inner
        o, c = QUOTES[(depth + 1) % 2]
        return o + inner + c
    if t in ('q', 'gloss'):
        if e.get('type') == 'foreign':
            return inner
        o, c = QUOTES[depth % 2]
        return o + inner + c
    if t == 'del':
        return '[' + inner + ']'
    if t == 'gap':
        return '…'
    if t == 'hi' and e.get('rend') == 'superscript':
        return '^' + inner
    if t in ('milestone', 'note') and depth >= 0:
        problems.append(f'unexpected <{t}> inside a note: {ET.tostring(e, encoding="unicode")[:120]}')
    return inner


def body_walk(e, bk, qdepth):
    """Walk body mark-up, appending to bk.out."""
    t = tag(e)
    if t == 'milestone':
        u = e.get('unit')
        if u == 'section':
            s = e.get('n')
            bk.section = s
            bk.sections.append(s)
            bk.out.append(f' [{s}] ')
        elif u == 'para':
            bk.out.append('\n\n')
        elif u != 'page':
            problems.append(f'{bk.lang} book {bk.n}: unknown milestone {e.attrib}')
        bk.out.append(ws(e.tail))
        return
    if t == 'note':
        num = len(bk.notes) + 1
        txt = render_note(e, bk.lang, -1).strip()
        txt = re.sub(r'\s+([,.;:])', r'\1', txt)
        if e.get('resp') != 'Loeb':
            txt = '(non-Loeb note) ' + txt
        bk.notes.append((num, bk.section, txt))
        bk.out.append(f'[^{num}]')
        bk.out.append(ws(e.tail))
        return
    if t == 'bibl':
        bk.out.append(' [cit. ' + ws(''.join(e.itertext())).strip() + '] ')
        bk.out.append(ws(e.tail))
        return
    if t == 'gap':
        bk.out.append('…' + ws(e.tail))
        return
    pre, post = '', ''
    q_eng = bk.lang == 'eng' and t == 'q' and e.get('type') != 'foreign'
    verse = t == 'quote' and e.find(NS + 'l') is not None
    child_depth = qdepth
    if q_eng or (bk.lang == 'eng' and t == 'quote' and not verse):
        child_depth = qdepth + 1
        o, c = QUOTES[child_depth % 2]
        if not (e.get('rend') == 'merge' and merge_quote(bk, child_depth)):
            pre = o
        post = Close(c, child_depth)
    elif verse:
        pre, post = LB, LB
    elif t == 'l':
        pre, post = LB + '> ', LB
    elif t == 'del':
        pre, post = '[', ']'
    elif t == 'add' and bk.lang == 'grc':
        pre, post = '⟨', '⟩'
    elif t == 'hi' and e.get('rend') == 'superscript':
        pre = '^'
    elif t not in ('div', 'p', 'said', 'q', 'quote', 'cit', 'title', 'foreign', 'placeName',
                   'emph', 'corr', 'add', 'sic', 'supplied', 'hi'):
        problems.append(f'{bk.lang} book {bk.n}: unhandled body element <{t}>')
    bk.out.append(pre)
    bk.out.append(ws(e.text).lstrip() if t == 'l' else ws(e.text))
    for ch in e:
        body_walk(ch, bk, child_depth)
    bk.out.append(post)
    bk.out.append(ws(e.tail))


def merge_quote(bk, depth):
    """Drop the closing mark of the quote that a page <div> cut off."""
    for i in range(len(bk.out) - 1, -1, -1):
        x = bk.out[i]
        if isinstance(x, Close):
            if x.depth == depth:
                del bk.out[i]
                return True
            continue
        if isinstance(x, str) and (x.strip() == '' or SEC_RE.fullmatch(x.strip())):
            continue
        break
    bk.unmerged += 1  # text came between (e.g. 'he said;'): open a new quote
    return False


def finish(bk):
    s = ''.join(x.ch if isinstance(x, Close) else x for x in bk.out)
    # a section milestone just before a para milestone belongs to the next paragraph
    s = re.sub(r'\s*(\[\d{3}[a-e]\])\s*\n\n', r'\n\n\1 ', s)
    paras = []
    for p in s.split('\n\n'):
        lines = [re.sub(r' {2,}', ' ', ln).strip() for ln in p.split(LB)]
        lines = [ln for ln in lines if ln]
        if lines:
            paras.append('\n'.join(lines))
    text = '\n\n'.join(paras)
    # space before punctuation left by tag tails; a ’ followed by a letter is an elision (’tis)
    text = re.sub(r' +([,.;:?!·”])', r'\1', text)
    text = re.sub(r' +’(?=[\s,.;:?!”’—)\]]|$)', '’', text)
    text = re.sub(r'([“‘]) +', r'\1', text)
    return text + '\n'


def parse_tei(fname, lang):
    path = os.path.join(RAW, fname)
    with open(path, 'rb') as f:
        data = f.read()
    if b'<!ENTITY' in data or b'<!DOCTYPE' in data:
        problems.append(f'{fname}: DOCTYPE/ENTITY present, refusing to parse')
        return [], ''
    root = ET.fromstring(data)
    lic = root.find(f'.//{NS}availability')
    lic_txt = ws(' '.join(lic.itertext())).strip() if lic is not None else ''
    books = []
    for d in root.iter(NS + 'div'):
        if d.get('subtype') == 'book':
            bk = Book(lang, int(d.get('n')))
            for ch in d:
                body_walk(ch, bk, 0)
            books.append(bk)
    return books, lic_txt


def split_sections(text):
    """{section: text} for a book text with [327a] markers."""
    parts = SEC_RE.split(text)
    if parts[0].strip():
        problems.append(f'text before first section marker: {parts[0][:80]!r}')
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def words(s):
    s = re.sub(r'\[\^\d+\]|\[cit\. [^\]]*\]', ' ', s)
    return [w for w in s.split() if re.search(r'\w', w)]


def jowett():
    with open(os.path.join(RAW, 'pg1497.txt'), encoding='utf-8') as f:
        lines = f.read().replace('\r\n', '\n').split('\n')
    try:
        end = next(i for i, ln in enumerate(lines) if ln.startswith('*** END OF THE PROJECT GUTENBERG'))
    except StopIteration:
        problems.append('jowett: END marker not found')
        return {}
    heads = [(i, ln.strip()) for i, ln in enumerate(lines[:end])
             if ln.startswith(' ') and re.fullmatch(r'(INTRODUCTION AND ANALYSIS|THE REPUBLIC|PERSONS OF THE DIALOGUE|BOOK [IVX]+)\.', ln.strip())]
    # the table of contents repeats the headings; keep the last occurrence of each
    last = {}
    for i, h in heads:
        last[h] = i
    order = ['INTRODUCTION AND ANALYSIS.', 'THE REPUBLIC.', 'PERSONS OF THE DIALOGUE.'] + [f'BOOK {r}.' for r in ROMAN]
    if any(h not in last for h in order):
        problems.append(f'jowett: missing headings {[h for h in order if h not in last]}')
        return {}
    pos = [last[h] for h in order] + [end]
    if pos != sorted(pos):
        problems.append(f'jowett: headings out of order {pos}')
        return {}

    def reflow(a, b):
        paras, cur = [], []
        for ln in lines[a + 1:b] + ['']:
            if ln.strip():
                cur.append(ln)
            elif cur:
                if cur[0].startswith((' ', '\t')):  # indented block (verse): keep lines
                    paras.append('\n'.join('> ' + c.strip() for c in cur))
                else:
                    paras.append(' '.join(c.strip() for c in cur))
                cur = []
        return '\n\n'.join(paras) + '\n'
    res = {'intro': reflow(pos[0], pos[1]), 'persons': reflow(pos[2], pos[3])}
    for k in range(10):
        res[f'{k + 1:02d}'] = reflow(pos[3 + k], pos[4 + k])
    return res


def write(rel, s):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)

# Hand fixes to the Shorey text where Perseus's <q> markup is off (book 7: inner quotes came out
# as double quotes, a few speeches lack an opening or closing mark). Each old string must occur once.
FIXES = {7: [
    ('Homer[^19] and “greatly prefer while living on earth to be serf of another, a landless man,”',
     'Homer[^19] and ‘greatly prefer while living on earth to be serf of another, a landless man,’'),
    ('in “evaluating” these', 'in ‘evaluating’ these'),
    ('the “idols”[^64]', 'the ‘idols’[^64]'),
    ('“They were, he said.', '“They were,” he said.'),
    ('of “two” is', 'of ‘two’ is'),
    ('confounded.[^117] “Is not that so?”', 'confounded.[^117] Is not that so?”'),
    ('designation “intelligible” for the one, and “visible” for',
     'designation ‘intelligible’ for the one, and ‘visible’ for'),
    ('cut up the “one” in', 'cut up the ‘one’ in'),
    ('ask them, “My good friends,', 'ask them, ‘My good friends,'),
    ('division into parts?” What do you think', 'division into parts?’ What do you think'),
    ('the “study of higher things,””', 'the ‘study of higher things,’”'),
    ('“Then,” said I, since the task is, so great,', '“Then,” said I, “since the task is so great,'),
    ('useful,[^219] said I, for the investigation', 'useful,[^219]” said I, “for the investigation'),
    ('“And what is more,” I said, I take it', '“And what is more,” I said, “I take it'),
    ('dialecticians[^224]? ““No, by Zeus,”', 'dialecticians[^224]?” “No, by Zeus,”'),
    ('““No” is surely the answer to that too.”', '“‘No’ is surely the answer to that too.”'),
    ('“Understanding,”[^253] I believe', '‘Understanding,’[^253] I believe'),
    ('the question,[^315] “What is the honorable?” and', 'the question,[^315] ‘What is the honorable?’ and'),
    ('“It is so” “Well,', '“It is so.” “Well,'),
    ('They delight like spies in', 'They delight like puppies in'),  # 539b σκυλάκια; Perseus typo
], 8: [
    ('of how democracy passes over into this', 'of how timocracy passes over into this'),  # 550d ἐκ τῆς τιμαρχίας; Perseus typo
]}


def apply_fixes(n, te):
    for old, new in FIXES.get(n, []):
        if te.count(old) != 1:
            problems.append(f'book {n:02d}: fix target found {te.count(old)} times: {old[:40]}')
        else:
            te = te.replace(old, new)
    return te


def main():
    eng, _ = parse_tei('tlg0059.tlg030.perseus-eng2.xml', 'eng')
    grc, _ = parse_tei('tlg0059.tlg030.perseus-grc2.xml', 'grc')
    if [b.n for b in eng] != list(range(1, 11)) or [b.n for b in grc] != list(range(1, 11)):
        problems.append(f'books: eng {[b.n for b in eng]} grc {[b.n for b in grc]}')
    jw = jowett()
    rows = ['book\tsection\tshorey_words\tgreek_words\tshorey_first6']
    tot = {'sec': 0, 'ew': 0, 'gw': 0, 'notes': 0, 'jw': 0}
    for be, bg in zip(eng, grc):
        nn = f'{be.n:02d}'
        te, tg = apply_fixes(be.n, finish(be)), finish(bg)
        if be.sections != bg.sections:
            se, sg = set(be.sections), set(bg.sections)
            problems.append(f'book {nn}: section mismatch, only eng {sorted(se - sg)}, only grc {sorted(sg - se)}')
        if len(set(be.sections)) != len(be.sections):
            problems.append(f'book {nn}: duplicate eng sections')
        if re.search(r'<|>(?!\s)|&\w+;', re.sub(r'^> ', '', te, flags=re.M)):
            problems.append(f'book {nn}: stray markup in Shorey text')
        if len(re.findall(r'\[\^\d+\]', te)) != len(be.notes):
            problems.append(f'book {nn}: note anchors != notes')
        write(f'{nn}.txt', te)
        write(f'grc/{nn}.txt', tg)
        write(f'notes/{nn}.txt', ''.join(f'[^{n}] ({s}) {t}\n' for n, s, t in be.notes))
        if nn in jw:
            write(f'jowett/{nn}.txt', jw[nn])
            tot['jw'] += len(jw[nn].split())
        de, dg = split_sections(te), split_sections(tg)
        for s in be.sections:
            we, wg = words(de.get(s, '')), words(dg.get(s, ''))
            if not we or not wg:
                problems.append(f'{s}: empty section (eng {len(we)}, grc {len(wg)} words)')
            rows.append(f'{be.n}\t{s}\t{len(we)}\t{len(wg)}\t{" ".join(we[:6])}')
            tot['ew'] += len(we)
            tot['gw'] += len(wg)
        tot['sec'] += len(be.sections)
        tot['notes'] += len(be.notes)
    if jw:
        write('jowett/intro.txt', jw['intro'])
        write('jowett/persons.txt', jw['persons'])
    write('index.tsv', '\n'.join(rows) + '\n')
    if problems:
        print('\n'.join(problems[:40]) + (f'\n... {len(problems)} problems in all' if len(problems) > 40 else ''))
        sys.exit(1)
    print(f"ok: 10 books, {tot['sec']} sections, Shorey {tot['ew']} words + {tot['notes']} notes, "
          f"Greek {tot['gw']} words, Jowett {tot['jw']} words -> {os.path.relpath(OUT, ROOT)}/")


if __name__ == '__main__':
    main()
