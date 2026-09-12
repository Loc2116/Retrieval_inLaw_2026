"""Do TRAN cua y tuong CE_BM25CAT (Askari et al., ECIR 2023) tren du lieu cua nhom.

Y tuong bai bao: nhet diem tang 1 vao INPUT duoi dang text
    [CLS] query [SEP] <diem_tang1_da_chuan_hoa> [SEP] passage [SEP]
roi fine-tune. Bai bao bao +0.023 nDCG@10 (BERT-Base) va thang HAN interpolation
(.422 vs .353) tren MSMARCO.

Cau hoi o day KHONG phai "bai bao co dung khong" ma "diem tang 1 co MANG THEM
thong tin ma CE chua lay duoc, o dung cho nhom dang sai khong".
Thuoc do cua nhom la dung-o-hang-1, va 67% cau sai co gold o hang 2-3.
"""
import json, ast, sys, os

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
P = lambda *a: os.path.join(BASE, *a)
S = json.load(open(P("Ketqua_E/scores_dev300_fusion_M20_K20.json"), encoding="utf-8"))
G = json.load(open(P("dev_300_locked.json"), encoding="utf-8"))
def _ans(a):
    if isinstance(a, str): a = ast.literal_eval(a)
    return {str(x) for x in a}
gold = {q: _ans(G[q]["answer"]) for q in G}
Q = [q for q in S if q in gold]

mx = lambda v: max(v["ce"], v.get("ce_deep", -9e9))
rk = lambda q: sorted(S[q], key=lambda d: -mx(S[q][d]))          # xep theo CE
fs = lambda q, d: S[q][d]["bm25"]                                # diem tang 1 (RRF hoa)

# ---- CUA KIEM: dung lai moc 0.7100 truoc khi doc bat ky so nao ----
base = sum(rk(q)[0] in gold[q] for q in Q) / len(Q)
print(f"guard: dung-o-hang-1 cua max(ce,ce_deep) = {base:.4f}  (moc phai la 0.7100)")
assert abs(base - 0.7100) < 0.0051, "khong dung lai duoc moc -> dung doc tiep"

# ---- 1. Diem tang 1 co phan giai noi hai ung vien dau bang khong? ----
# Bieu dien tot nhat cua bai bao: min-max TOAN CUC -> so nguyen -> chuoi.
allv = [fs(q, d) for q in Q for d in S[q]]
lo, hi = min(allv), max(allv)
qz = lambda x, n=196: int(round((x - lo) / (hi - lo) * n))        # 0..196 nhu bai bao
col = sum(qz(fs(q, rk(q)[0])) == qz(fs(q, rk(q)[1])) for q in Q)
print(f"\n[1] PHAN GIAI sau min-max toan cuc -> int 0..196")
print(f"  hang 1 va hang 2 nhan CUNG mot so nguyen: {col}/{len(Q)} = {col/len(Q):.1%}")
print(f"  -> o {col/len(Q):.1%} cau, token duoc nhet vao KHONG phan biet noi hai ung vien dau")

# ---- 2. TRAN: diem tang 1 co tro dung ung vien nao khong? ----
# Chi xet cau ma quyet dinh THAT SU la giua hang 1 va hang 2 cua CE.
top2 = [q for q in Q if gold[q] & set(rk(q)[:2])]
cuu = hong = mu = 0
for q in top2:
    d1, d2 = rk(q)[:2]
    s1, s2 = fs(q, d1), fs(q, d2)
    dung1 = d1 in gold[q]
    if s1 == s2: mu += 1;  continue          # diem tang 1 khong noi gi
    theo_ts = d1 if s1 > s2 else d2          # di theo diem tang 1
    if not dung1 and theo_ts in gold[q]: cuu += 1
    if dung1 and theo_ts not in gold[q]:     hong += 1
print(f"\n[2] TRAN ARBITRAGE — {len(top2)}/{len(Q)} cau co gold trong top-2 cua CE")
print(f"  di theo diem tang 1 khi no khac nhau:  cuu {cuu} · hong {hong} · NET {cuu-hong:+d} cau")
print(f"  = {(cuu-hong)/len(Q)*100:+.2f} diem tren 300 cau · {mu} cau diem tang 1 hoa nhau")

# ---- 3. Diem tang 1 co du doan duoc gold trong top-2 khong? (AUC tho) ----
h = t = 0
for q in top2:
    d1, d2 = rk(q)[:2]
    gd = d1 if d1 in gold[q] else d2
    bd = d2 if gd == d1 else d1
    if fs(q, gd) > fs(q, bd): h += 1
    elif fs(q, gd) == fs(q, bd): t += 1
print(f"\n[3] gold co diem tang 1 CAO HON doi thu: {h}/{len(top2)} = {h/len(top2):.1%}  (hoa {t})")
print(f"  nguong hoa von cua moi bo phan xu top-2 la ~70,8% (dev300)")

# ---- 4. Doi chieu: CE va diem tang 1 co doc lap khong? ----
agree = sum(rk(q)[0] == max(S[q], key=lambda d: fs(q, d)) for q in Q)
r1 = sum(max(S[q], key=lambda d: fs(q, d)) in gold[q] for q in Q) / len(Q)
print(f"\n[4] hang 1 cua CE == hang 1 cua diem tang 1: {agree}/{len(Q)} = {agree/len(Q):.1%}")
print(f"  dung-o-hang-1 neu CHI dung diem tang 1: {r1:.4f}  (CE: {base:.4f})")

# ---- 5. TACH TI LE NEN (quy tac 3) ----
# [3] bi lam dep boi ti le nen: 84% cau top-2 da dung san, va diem tang 1 dong y
# voi CE o phan lon so do. Con so THAT SU quan trong la: tren tap CO THE CUU DUOC,
# diem tang 1 co tro dung khong.
rec = [q for q in top2 if rk(q)[0] not in gold[q]]      # gold o hang 2 -> cuu duoc
keep = [q for q in top2 if rk(q)[0] in gold[q]]         # dang dung -> co the lam hong
def diem_tro_dung(qs):
    ok = tie = 0
    for q in qs:
        d1, d2 = rk(q)[:2]
        gd = d1 if d1 in gold[q] else d2
        bd = d2 if gd == d1 else d1
        if   fs(q, gd) >  fs(q, bd): ok += 1
        elif fs(q, gd) == fs(q, bd): tie += 1
    return ok, tie, len(qs)
print(f"\n[5] TACH TI LE NEN")
for nm, qs in [("cuu duoc (gold o hang 2)", rec), ("dang dung (gold o hang 1)", keep)]:
    ok, tie, n = diem_tro_dung(qs)
    print(f"  {nm:<28} {ok}/{n} = {ok/n:6.1%}  (hoa {tie})")
print("  -> con so quyet dinh la dong TREN: tren tap co the cuu, diem tang 1 chi")
print("     tro dung ~1/2 lan. 80,7% cua [3] la ti le nen, khong phai suc phan giai.")

# ---- 6. DAI MARGIN THAP: dung so sanh voi nguong hoa von 70,8% ----
gap = lambda q: mx(S[q][rk(q)[0]]) - mx(S[q][rk(q)[1]])
lo_band = sorted(Q, key=gap)[:int(len(Q) * .6)]          # 60% cau chenh diem thap nhat
lb2 = [q for q in lo_band if gold[q] & set(rk(q)[:2])]
c = h_ = 0
for q in lb2:
    d1, d2 = rk(q)[:2]
    s1, s2 = fs(q, d1), fs(q, d2)
    if s1 == s2: continue
    theo = d1 if s1 > s2 else d2
    if d1 not in gold[q] and theo in gold[q]: c += 1
    if d1 in gold[q] and theo not in gold[q]: h_ += 1
print(f"\n[6] DAI MARGIN THAP (60% cau chenh diem CE nho nhat) — {len(lb2)} cau co gold trong top-2")
print(f"  di theo diem tang 1: cuu {c} · hong {h_} · NET {c-h_:+d} cau = {(c-h_)/len(Q)*100:+.2f} diem")
print(f"  do chinh xac cua bo phan xu 'diem tang 1': {c}/{c+h_} = {c/(c+h_):.1%} vs hoa von 70,8%")

# ---- 7. TRAN TUYET DOI: neu mo hinh HOC DUOC khi nao nen tin diem tang 1 ----
print(f"\n[7] TRAN TUYET DOI (oracle cong: chi dung diem tang 1 khi no giup)")
print(f"  +{cuu} cau = +{cuu/len(Q)*100:.2f} diem  (0.7100 -> {(base*len(Q)+cuu)/len(Q):.4f})")
print(f"  san: theo mu quang = {(cuu-hong)/len(Q)*100:+.2f} diem")

# ---- 8. BIEN THE: BM25 THEO TUNG DOAN (pick_chunks da tinh roi NEM DI) ----
# Trong bai bao, diem tang 1 la MOT SCALAR MOI CAP (query, passage) va passage la
# don vi xep hang. Trong pipeline nay don vi xep hang la VAN BAN nhung don vi cham
# la DOAN, nen diem muc van ban se KHONG DOI tren moi doan cua cung mot van ban
# => luong thong tin y HET phep cong RRF da dong (LB -0,9), chi khac dang ham.
# Bien the that su MOI: diem BM25 tung doan, thay doi trong long mot van ban.
if "--chunk" in sys.argv:
    import statistics as st
    sys.path.insert(0, BASE); import deep_chunk as DC
    DC.MERGE_CHARS = 1800
    CTX = P("Input/selected-contexts")
    def chunk_bm25(question, doc_id):
        parts, tfs, lens, idf, avg = DC._index(CTX, doc_id)
        qs = set(DC.tok(question))
        return [sum(idf.get(w, 0.) * tf[w] * (DC.K1 + 1) /
                    (tf[w] + DC.K1 * (1 - DC.B + DC.B * L / avg))
                    for w in qs if w in tf)
                for tf, L in zip(tfs, lens)]
    def arb(qs, agg, cap=None):
        ok = tie = 0; qs = qs[:cap] if cap else qs
        for q in qs:
            d1, d2 = rk(q)[:2]
            gd = d1 if d1 in gold[q] else d2
            bd = d2 if gd == d1 else d1
            try: a, b = agg(chunk_bm25(G[q]["question"], gd)), agg(chunk_bm25(G[q]["question"], bd))
            except Exception: continue
            if a > b: ok += 1
            elif a == b: tie += 1
        return ok, tie, len(qs)
    print("\n[8] BM25 THEO DOAN — tro dung ung vien nao?")
    for nm, agg in [("max doan", max), ("tb 3 doan cao nhat", lambda v: st.mean(sorted(v)[-3:]))]:
        o1, _, n1 = arb(rec, agg)
        o2, _, n2 = arb(keep, agg, cap=120)
        print(f"  {nm:<20} cuu duoc {o1}/{n1}={o1/n1:5.1%} · dang dung {o2}/{n2}={o2/n2:5.1%}")
    print("  (doi chieu diem RRF muc van ban: 53,7% va 85,9%)")
    print("  -> BM25 muc doan KEM HON HAN: no bat dong voi CE o gan mot nua so cau")
    print("     CE dang lam DUNG, nen di theo no la pha he thong.")
