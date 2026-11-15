#!/usr/bin/env python3
"""Writes preview/: a copy of the site whose links name index.html explicitly,
for viewing through raw-file services such as raw.githack.com.
Run after build.py:  python3 _src/make_preview.py"""
import re,pathlib,shutil
root=pathlib.Path(__file__).resolve().parent.parent; out=root/'preview'
for f in root.rglob('index.html'):
    rel=f.relative_to(root)
    if rel.parts[0] in ('preview','_src','.git','screenshots'): continue
    s=f.read_text()
    def fix(m):
        attr,url=m.group(1),m.group(2)
        if re.match(r'(https?:|mailto:|tel:|sms:|#|data:)',url): return m.group(0)
        if 'assets/' in url: return f'{attr}="../{url}"'
        path,_,frag=url.partition('#')
        path='index.html' if path=='./' else (path+'index.html' if path.endswith('/') else path)
        return f'{attr}="{path}{"#"+frag if frag else ""}"'
    s=re.sub(r'\b(href|src)="([^"]*)"',fix,s)
    s=re.sub(r'url=(\.\./[^"#]*?)/(#[^"]*)?"',lambda m:f'url={m.group(1)}/index.html{m.group(2) or ""}"',s)
    d=out/rel; d.parent.mkdir(parents=True,exist_ok=True); d.write_text(s)
