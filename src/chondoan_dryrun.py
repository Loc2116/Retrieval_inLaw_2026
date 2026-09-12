"""Chay kho notebook cua D bang du lieu that + model gia, de bat loi logic truoc khi dot GPU."""
import json, os, numpy as np
B=os.path.expanduser("~/mnt/project_DSC")
dev=json.load(open(f"{B}/dev_300_locked.json",encoding="utf-8"))
S=json.load(open(f"{B}/Ketqua_E/scores_dev300_fusion_M20_K20.json",encoding="utf-8"))
gold={q:{str(x) for x in v["answer"]} for q,v in dev.items()}; Q=list(gold)
mx=lambda v: max(v["ce"], v.get("ce_deep",-9e9))
order={q:[d for d,_ in sorted(S[q].items(), key=lambda kv:-mx(kv[1]))] for q in Q}
top1=lambda p: np.mean([p[q] in gold[q] for q in Q])
TOP_DOCS=5

base=top1({q:order[q][0] for q in Q}); assert abs(base-0.7100)<1e-6
cap5=np.mean([bool(gold[q]&set(order[q][:TOP_DOCS])) for q in Q])
print(f"O1 guard OK: moc {base:.4f} · tran top-5 {cap5:.4f}")

# model gia: moi van ban 8 doan, doan dau mang dung diem ce hien co -> ket qua PHAI = moc
rng=np.random.default_rng(0)
res={q:{d:[mx(S[q][d])]+list(rng.uniform(-1,0,7)) for d in order[q][:TOP_DOCS]} for q in Q}

def pick_at(n):
    return {q: max(res[q], key=lambda d: max(sorted(res[q][d],reverse=True)[:n or len(res[q][d])])) for q in Q}

a=top1(pick_at(None))
print(f"O3 voi model gia (doan dau = diem cu, con lai thap hon): {a:.4f}  -> phai bang moc")
assert abs(a-base)<1e-9, "LOI LOGIC pick_at"

# model gia 2: mot doan an nap cua gold co diem cao -> phai leo len tran
res2={q:{d:[mx(S[q][d])]+([9.0] if d in gold[q] else []) for d in order[q][:TOP_DOCS]} for q in Q}
res=res2; b=top1(pick_at(None))
print(f"O3 voi model gia (gold co 1 doan diem 9.0)          : {b:.4f}  -> phai bang tran {cap5:.4f}")
assert abs(b-cap5)<1e-9, "LOI LOGIC pick_at (nhanh 2)"
print("\nDRY-RUN OK — logic do dung o ca hai cuc.")

n=[len(order[q]) for q in Q]
print(f"ung vien/cau: {min(n)}–{max(n)} · se cham lai {TOP_DOCS} van ban/cau")
