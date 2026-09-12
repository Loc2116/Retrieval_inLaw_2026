"""Doc ket qua fusion_dev1000 (K=50). DANH SACH PHEP DO DA KHOA 07/09 — khong them gi.
Chay: python dev1000_doc.py <scores_dev1000_fusion_M20_K50_matchEmbedded.json>
"""
import json, sys, os, numpy as np
from math import comb

F = sys.argv[1] if len(sys.argv) > 1 else "scores_dev1000_fusion_M20_K50_matchEmbedded.json"
B = os.path.dirname(os.path.abspath(__file__))
dev = json.load(open(f"{B}/dev_1000_locked.json", encoding="utf-8"))
S   = json.load(open(F, encoding="utf-8"))
gold = {q: {str(x) for x in v["answer"]} for q, v in dev.items()}
Q = [q for q in gold if q in S]
print(f"{len(Q)}/{len(gold)} cau co diem\n")

V = {"base": lambda v: v["ce"],
     "max": lambda v: max(v["ce"], v.get("ce_deep", -9e9)),
     "replace": lambda v: v.get("ce_deep", v["ce"])}
run = lambda f: np.array([max(S[q].items(), key=lambda kv: f(kv[1]))[0] in gold[q] for q in Q])

def mc(A, Bv):
    w = int((A & ~Bv).sum()); l = int((Bv & ~A).sum()); n = w + l
    p = (sum(comb(n, i) for i in range(max(w, l), n + 1)) / 2**n * 2) if n else 1.0
    return w, l, min(p, 1.0)

REF = run(V["max"])
print("=" * 70)
print("① MOC + HIEU CHUAN CAI CAN  (LB that: max 0.702 · replace 0.671 · chenh -3,1)")
print("=" * 70)
for n in ("max", "base", "replace"):
    A = run(V[n]); w, l, p = mc(A, REF)
    t = "" if n == "max" else f"   thang {w} thua {l}  p={p:.4f}"
    print(f"  {n:<9}{A.mean():.4f}  ({A.mean()-REF.mean():+.4f}){t}")
d = run(V["replace"]).mean() - REF.mean()
print(f"\n  chenh replace-max = {d*100:+.2f} diem · LB do duoc -3,10")
print("  => lech <1,5 diem: CAN DUNG, moi thi nghiem sau quyet tren dev1000, khoi ton luot nop")
print("  => lech >1,5 diem: dev1000 KHONG thay duoc LB, van phai nop de quyet\n")

print("=" * 70)
print("② CONG RRF: max(ce,ce_deep) + L*z(rrf)   [ung vien duong yeu duy nhat con lai]")
print("=" * 70)
z = {}
for q in Q:
    r = np.array([v["bm25"] for v in S[q].values()])
    c = np.array([V["max"](v) for v in S[q].values()])
    f = lambda a: (a - a.mean()) / (a.std() + 1e-9)
    z[q] = (list(S[q]), f(c), f(r))
for L in (0, .05, .1, .15, .2, .3, .5):
    A = np.array([z[q][0][int(np.argmax(z[q][1] + L * z[q][2]))] in gold[q] for q in Q])
    w, l, p = mc(A, REF)
    star = "  <<< CO Y NGHIA" if p < 0.05 and A.mean() > REF.mean() else ""
    print(f"  L={L:<5}{A.mean():.4f}  ({A.mean()-REF.mean():+.4f})  thang {w} thua {l}  p={p:.4f}{star}")
print("\n  NGUONG DA KHOA: chi nhan L nao dat p<0.05 VA Δ>+0,010. Khong dat -> DONG, khong nop.")

print("\n" + "=" * 70)
print("③ CAU TRUC LOI (de quyet co lam bo phan xu cap khong)")
print("=" * 70)
o = {q: [d for d, _ in sorted(S[q].items(), key=lambda kv: -V["max"](kv[1]))] for q in Q}
r = [min([o[q].index(g) + 1 for g in gold[q] if g in o[q]], default=999) for q in Q]
r = np.array(r)
bad = r[r > 1]
print(f"  sai {len(bad)} cau · gold o hang 2: {(bad==2).sum()} ({(bad==2).sum()/len(bad)*100:.0f}%)"
      f" · hang 2-3: {((bad>=2)&(bad<=3)).sum()} ({((bad>=2)&(bad<=3)).sum()/len(bad)*100:.0f}%)")
m = np.array([V["max"](S[q][o[q][0]]) - V["max"](S[q][o[q][1]]) for q in Q])
lo = m < 0.005
n_ok = int((lo & (r == 1)).sum()); n_fix = int((lo & (r == 2)).sum())
print(f"  dai chenh<0.005: {n_ok} cau DANG DUNG · {n_fix} cau cuu duoc"
      f"  => bo phan xu phai dung >{n_ok/max(n_ok+n_fix,1)*100:.1f}% moi hoa von")
print("  (dev300 cho 70,8% — neu dev1000 cung quanh do thi cuoc nay van kho)")
