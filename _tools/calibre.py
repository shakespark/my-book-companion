#!/usr/bin/env python3
"""在 Calibre 书库里查书，把选中的一本挂到某个导读目录的 source/ 下。对书库只读，绝不写入。
  python3 _tools/calibre.py find <关键词>          按书名或作者查，列出 id、格式、路径
  python3 _tools/calibre.py link <目录名> <id> [链接名]
                                                  建 <目录名>/source/，在里面放软链接 calibre（或给定的链接名）-> 书库里这本书的目录。
                                                  一本导读用到几本书（原版、译本、姊妹篇）时，第二本起给链接名，如 calibre-zh
书库位置默认 /mnt/d/calibre/books（D:\\calibre\\books），可用环境变量 CALIBRE_LIBRARY 改。"""
import os, shutil, sqlite3, sys, tempfile

LIB = os.environ.get("CALIBRE_LIBRARY", "/mnt/d/calibre/books")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def db():
    # Calibre 开着时可能锁住 metadata.db，先复制一份再以只读方式打开
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    shutil.copyfile(os.path.join(LIB, "metadata.db"), tmp.name)
    conn = sqlite3.connect(f"file:{tmp.name}?mode=ro", uri=True)
    os.unlink(tmp.name)  # 已打开的文件在 Linux 上删掉也能继续读
    return conn


QUERY = """
select b.id, b.title, b.path,
  (select group_concat(a.name, ' & ') from books_authors_link l join authors a on a.id = l.author where l.book = b.id),
  (select group_concat(d.format, ' ') from data d where d.book = b.id)
from books b"""


def find(words):
    kw = f"%{' '.join(words)}%"
    rows = db().execute(QUERY + """ where b.title like ? or exists (
        select 1 from books_authors_link l join authors a on a.id = l.author where l.book = b.id and a.name like ?)
        order by b.title""", (kw, kw)).fetchall()
    for id_, title, path, authors, fmts in rows:
        print(f"{id_:>6}  {title} — {authors or '?'}  [{fmts or '无文件'}]\n        {path}")
    print(f"共 {len(rows)} 本")


def link(slug, id_, name="calibre"):
    row = db().execute(QUERY + " where b.id = ?", (int(id_),)).fetchone()
    if not row:
        sys.exit(f"书库里没有 id {id_}")
    _, title, path, authors, fmts = row
    target = os.path.join(LIB, path)
    if not os.path.isdir(target):
        sys.exit(f"书库里找不到目录 {target}")
    src = os.path.join(ROOT, slug, "source")
    os.makedirs(src, exist_ok=True)
    ln = os.path.join(src, name)
    if os.path.lexists(ln):
        sys.exit(f"{ln} 已存在（指向 {os.readlink(ln)}），要换书先删掉它")
    os.symlink(target, ln)
    print(f"{slug}/source/{name} -> {target}\n  {title} — {authors}  [{fmts}]")
    if "EPUB" not in (fmts or ""):
        print("  注意：这本没有 EPUB，提取脚本都是按 epub 写的，先在 Calibre 里转一份")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "find":
        find(a[1:])
    elif len(a) in (3, 4) and a[0] == "link":
        link(*a[1:])
    else:
        sys.exit(__doc__)
