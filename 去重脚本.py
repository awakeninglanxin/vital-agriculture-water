#!/usr/bin/env python3
"""逆M详细代码_v2 去重脚本 - 保留非27路径, 删除27里与已有重复的副本"""
import os, hashlib, subprocess
NEW = r'D:\AAA我的文件\PKS_千禧难题_GitHub版\02_应用科技\20_分形研究\逆M详细代码_v2'
print(f'扫描: {NEW}')
files = []
for dp, dn, fn in os.walk(NEW):
    for f in fn:
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, NEW).replace(os.sep, '/')
        try:
            h = hashlib.md5(open(p, 'rb').read()).hexdigest()
        except Exception:
            h = 'ERR'
        files.append((h, rel, p, os.path.getsize(p)))

from collections import defaultdict
grp = defaultdict(list)
for h, r, p, s in files:
    grp[h].append((r, p, s))

to_del = []
for h, lst in grp.items():
    if len(lst) <= 1:
        continue
    non_27 = [(r, p, s) for r, p, s in lst if not r.startswith('27_')]
    is_27 = [(r, p, s) for r, p, s in lst if r.startswith('27_')]
    if non_27:
        # 保留一个非27, 删其余
        kept = non_27[0]
        to_del.extend(is_27)
        to_del.extend(non_27[1:])
    else:
        # 全部在27里, 留第一个
        to_del.extend(is_27[1:])

print(f'待删除冗余文件: {len(to_del)} 个, 合计 {sum(s for _,_,s in to_del)/1024/1024:.1f}MB')
for r, p, s in to_del[:15]:
    print(f'  DEL: {r} ({s}B)')
if len(to_del) > 15:
    print(f'  ... 还有 {len(to_del)-15} 个')

# 执行删除
err = 0
for r, p, s in to_del:
    try:
        os.remove(p)
    except Exception as e:
        err += 1
        print(f'  ❌ 失败: {r}: {e}')

# 统计
import subprocess
result = subprocess.run(['powershell', '-NoProfile', '-Command',
    f"(Get-ChildItem -Path '{NEW}' -Recurse -File).Count"],
    capture_output=True, text=True)
# 如果powershell被沙箱拦截,用纯python
if result.returncode != 0:
    count = sum(1 for _, _, fn in os.walk(NEW) for _ in fn)
    total = sum(os.path.getsize(os.path.join(dp, f))
                for dp, dn, fn in os.walk(NEW)
                for f in fn)
    print(f'剩余: {count} 个文件, {total/1024/1024:.1f}MB')
else:
    print(f'剩余文件数: {result.stdout.strip()}')
print(f'删除失败: {err}')
