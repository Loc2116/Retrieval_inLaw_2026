"""Do TRAN cua truc k TRUOC khi tieu GPU (quy tac 9). CPU thuan, vai giay.

CAU HOI: bai da nop chay K_CHUNK=50 (doc tron van ban) nhung bang NxK tren dev300
chi do toi k=10. max-pool tren ~47 doan co pha loang so voi ~10 doan khong?

KHONG dung duoc bai k=10 tu bo diem nay -- o1 cua public_ft_run.ipynb da canh bao:
pick_chunks tra
  len(parts) <= k -> TRON van ban, THU TU VAN BAN
  len(parts) >  k -> top-k theo BM25, THU TU DIEM
nen v[:10] chi bang pick_chunks(k=10) o cap CO len(v)==50 (tuc bi cat).

Nhung tren dung tap cap do, truc k suy duoc CHINH XAC -> do tran that o day.
De thi KHONG co nhan, nen day la tran + ngan sach thong tin, KHONG phai diem.
"""
import json, zipfile, collections, os, sys

# BASE = thu muc lam viec cua du an (chua Input/ va Ketqua_E/). Mac dinh la thu muc hien tai.
BASE  = sys.argv[1] if len(sys.argv) > 1 else "."
P     = lambda *a: os.path.join(BASE, *a)
SC    = P("Ketqua_E/lai_ft/scores_public_M20K50_90e09359.json")  # bo diem san xuat
FTSC  = P("Ketqua_E/lai_ft/public_ft_scores.json")               # diem mo hinh FT
TESTF = P("Input/public-official.json")
CUR_Z = P("Ketqua_E/probe_top1/A_K50_max_DANGNOP.zip")           # bai 0.702
FT_Z  = P("Ketqua_E/lai_ft/sub_FT_N3_k50.zip")                   # bai 0.711
N_DOC = 3

for _f in (SC, FTSC, TESTF, CUR_Z, FT_Z):
    if not os.path.isfile(_f):
        sys.exit(f"THIEU {_f}\n  chay: python k_tran.py <thu-muc-du-an>")

def unzip_sub(p):
    z = zipfile.ZipFile(p)
    return {q: v["answer"][0] for q, v in json.loads(z.read(z.namelist()[0])).items()}

test = json.load(open(TESTF, encoding="utf-8-sig"))
S    = json.load(open(SC, encoding="utf-8"))
res  = json.load(open(FTSC, encoding="utf-8"))
CUR, FT = unzip_sub(CUR_Z), unzip_sub(FT_Z)
Q = list(test)

mx = lambda v: max(v["ce"], v.get("ce_deep", -9e9))
order = {q: [d for d, _ in sorted(S[q].items(), key=lambda kv: -mx(kv[1]))] for q in Q}

# ---- CUA KIEM (bay 8): dung lai bai da nop TRUOC khi doc bat ky Delta nao ----
assert {q: order[q][0] for q in Q} == CUR, "khong dung lai duoc bai 0.702 tu bo diem"
bad = [q for q in Q if list(res[q]) != order[q][:N_DOC]]
assert not bad, f"{len(bad)} cau cham nham ro (vd {bad[:3]})"

def pick(N, k=None):
    o = {}
    for q in Q:
        best, bs = None, -9e9
        for d in order[q][:N]:
            v = res[q].get(d)
            if not v: continue
            s = max(v) if k is None else max(v[:k])
            if s > bs: bs, best = s, d
        o[q] = best or order[q][0]
    return o

assert pick(1) == CUR, "N=1 khong trung bai dang nop -> ro sai"
assert pick(3) == FT,  "N=3 khong dung lai duoc bai 0.711"
print("guard: bai 0.702 dung lai OK · ro khop order[:3] 1000/1000 · N=1==0.702 · N=3==0.711")

# ---- 1. TRAN: doan THANG nam o hang BM25 nao? (chi tren cap suy duoc) ----
ranks = [max(range(50), key=lambda i: v[i])
         for q in Q for v in res[q].values() if len(v) == 50]
c = collections.Counter(ranks)
cum = lambda n: sum(v for r, v in c.items() if r < n) / len(ranks)
print(f"\n[1] TRAN TRUC k - {len(ranks)} cap suy duoc (len==50, thu tu BM25)")
for n in (10, 20, 35):
    print(f"  doan thang nam trong top-{n:<2} BM25 : {cum(n):6.1%}")
print(f"  => ha k 50->10 doi diem max o    : {1-cum(10):6.1%} cap")

# ---- 2. NGAN SACH THONG TIN: ha k co doi lua chon van ban khong? ----
sub = [q for q in Q if all(len(res[q][d]) == 50 for d in order[q][:N_DOC])]
base = pick(N_DOC)
print(f"\n[2] NGAN SACH THONG TIN - {len(sub)}/1000 cau co ca {N_DOC} vb suy duoc")
for k in (10, 20, 35):
    p = pick(N_DOC, k)
    print(f"  k={k:<3} doi {sum(p[q]!=base[q] for q in sub):>3}/{len(sub)} cau tren tap suy duoc"
          f"   ({sum(p[q]!=base[q] for q in Q)}/1000 ca bo, KHONG dung nghia)")

# ---- 3. cap TRON van ban: index = VI TRI trong van ban (doi chieu voi enrich_front) ----
pos = [max(range(len(v)), key=lambda i: v[i]) / (len(v)-1)
       for q in Q for v in res[q].values() if 10 < len(v) < 50]
print(f"\n[3] {len(pos)} cap TRON van ban: vi tri tuong doi cua doan thang")
print(f"  trung binh {sum(pos)/len(pos):.3f} (0=dau van ban, 1=cuoi)"
      f" · nam o 20% dau: {sum(x<0.2 for x in pos)/len(pos):.1%}")
