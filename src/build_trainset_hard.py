"""Dung tap huan luyen listwise. CPU thuan. Ghi theo dong, xa cache, chay lai la noi tiep.

THIET KE (doi chieu chan doan 19/08):
  - BIEN THE KHO: negative hang 2-10 (BO hang 1 - de la gold chua gan nhan nhat).
    Ly do: val acc TRUOC huan luyen tren bo hang 10-20 da la 0.83 => bai qua de,
    trong khi bai THAT (hang 1 vs hang 2 trong ro fusion) mo hinh chi dung ~70%.
    Chan doan 19/08 canh bao negative qua kho -- nhung do la voi muc tieu POINTWISE.
    Listwise softmax so sanh TUONG DOI trong nhom nen chiu duoc negative kho hon nhieu.
  - chon doan DOI XUNG cho ca duong lan am: pick_chunks(k=1) cho MOI van ban.
    Bat doi xung (duong chon bang CE, am chon bang BM25) day mo hinh hoc phan biet
    "kieu chon doan" thay vi hoc lien quan -> ro ri thang, hong am tham.
  - nhan duong la VAN BAN (chac chan dung); doan chi la bang chung yeu hon, khong phai nhan SAI.
    Vi the pick_chunks dung duoc o day, trong khi voi muc tieu POINTWISE truoc kia thi khong.
"""
import json, os, sys, random, gc
sys.path.insert(0, ".")
import deep_chunk as DC
DC.MERGE_CHARS = 1800
CTX, OUT = "Input/selected-contexts", "trainset_listwise_hard.jsonl"
N_NEG, LO, HI = 4, 2, 10   # BIEN THE KHO: hang 2-10 thay vi 10-20
random.seed(0)

tr    = json.load(open("Input/train.json", encoding="utf-8-sig"))
cand  = json.load(open("bm25_ids_train_FALLBACK.json", encoding="utf-8"))
dev1k = set(map(str, json.load(open("dev_1000_locked.json", encoding="utf-8"))))

done = set()
if os.path.exists(OUT):
    for ln in open(OUT, encoding="utf-8"):
        try: done.add(json.loads(ln)["qid"])
        except Exception: pass
todo = [q for q in tr if q not in dev1k and q in cand and q not in done]
print(f"da co {len(done)} · con {len(todo)}", flush=True)

f = open(OUT, "a", encoding="utf-8")
n = 0
for i, q in enumerate(todo, 1):
    qt   = tr[q]["question"]
    gold = {str(x) for x in tr[q]["answer"]}
    ids  = [str(c["doc_id"]) for c in cand[q]]
    pos  = next((d for d in ids if d in gold), None)
    if pos is None: continue
    pool = [d for d in ids[LO-1:HI] if d not in gold]
    if len(pool) < N_NEG: continue
    negs = random.sample(pool, N_NEG)
    try:
        ck = {d: (DC.pick_chunks(qt, CTX, d, k=1) or [""])[0] for d in [pos] + negs}
    except Exception:
        continue
    if not ck[pos].strip(): continue
    # 10-09: doan duong trung Y HET mot doan am -> nhan tu mau thuan.
    #   Van ban phap luat sao chep nguyen dieu/khoan sang van ban khac nen
    #   xay ra thuc su: 13/5521 nhom o dai hang 2-10, 1/5521 o dai 10-20.
    if ck[pos] in [ck[d] for d in negs]: continue
    f.write(json.dumps({"qid": q, "question": qt, "pos_doc": pos,
                        "pos": ck[pos][:1800], "negs": [ck[d][:1800] for d in negs]},
                       ensure_ascii=False) + "\n")
    n += 1
    if i % 200 == 0:
        f.flush(); DC._cache.clear(); gc.collect()
        print(f"  {i}/{len(todo)} · ghi {n}", flush=True)
f.close()
print(f"XONG · ghi them {n} nhom -> {OUT}", flush=True)
