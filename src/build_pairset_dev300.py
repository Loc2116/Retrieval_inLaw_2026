"""Tap DANH GIA cho bo phan xu cap: dung cap (hang 1, hang 2) ma no phai quyet that.

Doan lay bang pick_chunks(k=1) — KHOP voi phan bo luc huan luyen (pairset_hard.jsonl).
Ghi kem margin (chenh diem CE hang1-hang2) de luc doc ket qua cat duoc theo dai.
"""
import json, ast, sys
sys.path.insert(0, ".")
import deep_chunk as DC
DC.MERGE_CHARS = 1800
CTX = "Input/selected-contexts"

S = json.load(open("Ketqua_E/scores_dev300_fusion_M20_K20.json", encoding="utf-8"))
G = json.load(open("dev_300_locked.json", encoding="utf-8"))
def _ans(a):
    if isinstance(a, str): a = ast.literal_eval(a)
    return {str(x) for x in a}
gold = {q: _ans(G[q]["answer"]) for q in G}
Q = [q for q in S if q in gold]
mx = lambda v: max(v["ce"], v.get("ce_deep", -9e9))
rk = lambda q: sorted(S[q], key=lambda d: -mx(S[q][d]))

# CUA KIEM: dung lai moc 0.7100 truoc khi ghi bat ky gi
base = sum(rk(q)[0] in gold[q] for q in Q) / len(Q)
assert abs(base - 0.7100) < 0.0051, f"moc {base:.4f} != 0.7100"
print(f"guard: moc {base:.4f} OK")

n = 0
with open("pairset_dev300.jsonl", "w", encoding="utf-8") as f:
    for q in Q:
        d1, d2 = rk(q)[:2]
        if not (gold[q] & {d1, d2}): continue        # gold khong o top-2 -> phan xu vo nghia
        qt = G[q]["question"]
        try:
            c1 = (DC.pick_chunks(qt, CTX, d1, k=1) or [""])[0][:1800]
            c2 = (DC.pick_chunks(qt, CTX, d2, k=1) or [""])[0][:1800]
        except Exception:
            continue
        if not c1.strip() or not c2.strip(): continue
        f.write(json.dumps({
            "qid": q, "question": qt,
            "A": c1, "B": c2, "doc_A": d1, "doc_B": d2,
            "label": int(d1 in gold[q]),              # 1 = hang 1 dang DUNG
            "margin": mx(S[q][d1]) - mx(S[q][d2]),
        }, ensure_ascii=False) + "\n")
        n += 1

rows = [json.loads(l) for l in open("pairset_dev300.jsonl", encoding="utf-8")]
dung = sum(r["label"] for r in rows)
print(f"\n{n} cap danh gia (gold nam trong top-2)")
print(f"  hang 1 DANG DUNG : {dung}/{n} = {dung/n:.1%}   <- do chinh xac neu KHONG lam gi")
print(f"  co the cuu       : {n-dung}")
for t in (0.005, 0.02, 0.10):
    sub = [r for r in rows if abs(r["margin"]) < t]
    if not sub: continue
    d = sum(r["label"] for r in sub)
    print(f"  dai margin < {t:<6} : {len(sub):>3} cap · dang dung {d} · cuu duoc {len(sub)-d}"
          f" · HOA VON = {d/len(sub):.1%}")
