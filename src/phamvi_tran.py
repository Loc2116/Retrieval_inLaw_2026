"""Do TRAN cua dac trung THU BAC / PHAM VI PHAP LY (quy tac 9). CPU, vai giay.

Kieu loi that: ca 138214 — model chon QD UBND Ha Noi thay vi Nghi dinh toan quoc
(trung chu nhieu hon nhung sai pham vi). CE cham tuong dong cau hoi-doan KHONG CO
CHO bieu dien thu bac phap ly.

Nhom da thu "uu the theo loai vb / tham quyen" -> AM. Nhung do la uu the TOAN CUC.
Quy tac 5: uu the toan cuc khong thang noi bo cham, TRU KHI no noi duoc dieu gi
RIENG CHO TUNG CAU. O day do dang DIEU KIEN tren dung quyet dinh hang 1 vs hang 2.
"""
import json, ast, re, sys, os, collections

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
P = lambda *a: os.path.join(BASE, *a)
S = json.load(open(P("Ketqua_E/scores_dev300_fusion_M20_K20.json"), encoding="utf-8"))
M = json.load(open(P("Ketqua_E/vanban_meta.json"), encoding="utf-8"))
G = json.load(open(P("dev_300_locked.json"), encoding="utf-8"))
def _ans(a):
    if isinstance(a, str): a = ast.literal_eval(a)
    return {str(x) for x in a}
gold = {q: _ans(G[q]["answer"]) for q in G}
Q = [q for q in S if q in gold]
mx = lambda v: max(v["ce"], v.get("ce_deep", -9e9))
rk = lambda q: sorted(S[q], key=lambda d: -mx(S[q][d]))

base = sum(rk(q)[0] in gold[q] for q in Q) / len(Q)
print(f"guard: moc = {base:.4f} (phai la 0.7100)")
assert abs(base - 0.7100) < 0.0051

# ---- thu bac phap ly, suy tu slug ----
BAC = [("hien-phap",9),("bo-luat",8),("luat-",8),("phap-lenh",7),("nghi-dinh",6),
       ("nghi-quyet",5),("thong-tu-lien-tich",4),("thong-tu",4),("quyet-dinh",3),
       ("chi-thi",2),("cong-van",1),("thong-bao",1)]
def bac(d):
    s = (M.get(d, {}).get("slug") or "").lower()
    for k, v in BAC:
        if s.startswith(k): return v
    return 0                                  # khong ro
def dp(d): return bool(M.get(d, {}).get("dp"))

cov = sum(bac(d) > 0 for q in Q for d in rk(q)[:2]) / (2*len(Q))
print(f"phu do metadata tren top-2: {cov:.1%} van ban suy duoc thu bac")

rec  = [q for q in Q if gold[q] & set(rk(q)[:2]) and rk(q)[0] not in gold[q]]
keep = [q for q in Q if gold[q] & set(rk(q)[:2]) and rk(q)[0] in gold[q]]
print(f"cuu duoc {len(rec)} cau · dang dung {len(keep)} cau\n")

def do(nm, key):
    """key(q,d) -> so; cao hon = uu tien hon. Do tren CA HAI tap."""
    out = {}
    for tag, qs in [("cuu duoc", rec), ("dang dung", keep)]:
        ok = tie = 0
        for q in qs:
            d1, d2 = rk(q)[:2]
            gd = d1 if d1 in gold[q] else d2
            bd = d2 if gd == d1 else d1
            a, b = key(q, gd), key(q, bd)
            if a > b: ok += 1
            elif a == b: tie += 1
        out[tag] = (ok, tie, len(qs))
    (o1,t1,n1),(o2,t2,n2) = out["cuu duoc"], out["dang dung"]
    # NET neu di theo dac trung nay o moi cau top-2 no khong hoa
    net = o1 - (n2 - o2 - t2)
    print(f"{nm}")
    print(f"  cuu duoc : {o1}/{n1} = {o1/n1:6.1%}  (hoa {t1})")
    print(f"  dang dung: {o2}/{n2} = {o2/n2:6.1%}  (hoa {t2})")
    print(f"  NET neu di theo: {net:+d} cau = {net/len(Q)*100:+.2f} diem\n")

do("[A] thu bac loai van ban (Luat>ND>TT>QD)", lambda q,d: bac(d))
do("[B] KHONG phai van ban dia phuong",        lambda q,d: 0 if dp(d) else 1)
do("[C] thu bac, chi khi mot ben la dia phuong", lambda q,d: (0 if dp(d) else 1)*100 + bac(d))

# ---- doi chieu: ca 138214 co trong dev300 khong, va no the hien the nao ----
print("--- phan bo thu bac cua gold vs ung vien sai (tap cuu duoc) ---")
cg = collections.Counter(); cb = collections.Counter()
for q in rec:
    d1, d2 = rk(q)[:2]
    gd = d1 if d1 in gold[q] else d2
    bd = d2 if gd == d1 else d1
    cg[bac(gd)] += 1; cb[bac(bd)] += 1
for b in sorted(set(cg) | set(cb), reverse=True):
    nm = next((k for k, v in BAC if v == b), "khong ro")
    print(f"  bac {b} {nm:<20} gold {cg[b]:>3} · sai {cb[b]:>3}")
