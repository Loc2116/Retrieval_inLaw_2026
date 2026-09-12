"""Dung tap huan luyen PAIRWISE tu tap listwise da co. CPU, vai giay, 0 cat doan lai.

Bo cham hien tai cham TUNG cap (cau hoi, van ban) DOC LAP — no chua bao gio nhin
hai ung vien canh nhau. Bo phan xu cap nhin CA HAI roi tra loi "cai nao dung hon".

  input : [CLS] cau hoi [SEP] van ban A [SEP] van ban B [SEP]
  nhan  : 1 neu A la gold, 0 neu B la gold
  mat mat: BCE

THIET KE:
  - Suy tu trainset_listwise_hard_clean.jsonl (1 duong + 4 am hang 2-10) -> 4 cap/nhom.
    Khong cat doan lai: doan da chon doi xung bang pick_chunks(k=1) cho ca duong lan am.
  - DAO THU TU ngau nhien: nua so cap dat gold o A, nua o B. Khong lam viec nay thi
    mo hinh hoc "luon chon A" — thien lech vi tri la loi kinh dien cua bo phan xu cap.
  - Luc suy luan phai CHAM CA HAI CHIEU roi lay trung binh, cung ly do.
"""
import json, random, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "trainset_listwise_hard_clean.jsonl"
OUT = sys.argv[2] if len(sys.argv) > 2 else "pairset_hard.jsonl"
random.seed(0)

n_grp = n_pair = 0
with open(OUT, "w", encoding="utf-8") as f:
    for ln in open(SRC, encoding="utf-8"):
        r = json.loads(ln)
        n_grp += 1
        for neg in r["negs"]:
            gold_la_A = random.random() < 0.5          # dao thu tu
            A, B = (r["pos"], neg) if gold_la_A else (neg, r["pos"])
            f.write(json.dumps({"qid": r["qid"], "question": r["question"],
                                "A": A, "B": B, "label": int(gold_la_A)},
                               ensure_ascii=False) + "\n")
            n_pair += 1
print(f"{n_grp} nhom -> {n_pair} cap -> {OUT}")

# kiem can bang nhan + do dai
rows = [json.loads(l) for l in open(OUT, encoding="utf-8")]
p1 = sum(r["label"] for r in rows) / len(rows)
mx = max(len(r["question"]) + len(r["A"]) + len(r["B"]) for r in rows)
print(f"  ti le nhan=1: {p1:.3f}  (phai ~0.5, lech nhieu = thien lech vi tri)")
print(f"  do dai input toi da: {mx:,} ky tu  -> can MAXLEN >= ~{mx//3:,} token")
print(f"  so qid: {len({r['qid'] for r in rows})}")
