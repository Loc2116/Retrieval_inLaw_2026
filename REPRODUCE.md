# Tái lập bài nộp — DSC 2026 Task 1

Tài liệu này dựng lại **đúng một** bài nộp, từ dữ liệu thô của BTC tới file `.zip`.

| | |
|---|---|
| bài nộp | `sub_FT_N3_k50.zip` — 1.000 câu, **1 doc_id mỗi câu** |
| điểm public | **precision 0,711** (08/09/2026) |
| kiến trúc | rổ hoà RRF → cross-encoder 2 tầng → **cross-encoder tinh chỉnh listwise** xếp lại top-3 |
| phần cứng | Kaggle T4 ×1 · tổng **~1,6 giờ GPU** cho toàn bộ đường chạy |
| nền tảng | Kaggle notebook, Python 3.11, `requirements.txt` |

> **Vì sao là 0,711 mà không phải 0,712.** Bài `sub_LAI_FT3_nua_dau.zip` đạt 0,712 nhưng
> nó lấy mô hình tinh chỉnh cho 500 câu đầu và mô hình gốc cho 500 câu sau — **một
> phương pháp không nhất quán**, sinh ra để cứu một lượt chạy hỏng. Hai bài lệch nhau
> **đúng 1 câu trên 1.000**, nằm sâu dưới sàn nhiễu (~1,45 điểm). Gói này tái lập bài
> áp **một phương pháp duy nhất cho cả 1.000 câu**.

---

## 0. Độ đo — đọc trước, nếu không sẽ tái lập ra số khác hẳn

Email BTC ngày 02/08/2026: *"Precision là độ đo chính và Recall là độ đo được sử dụng
trong trường hợp các nhóm có điểm Precision bằng nhau."*

Bộ chấm tính precision **chia cho số id thực nộp**, không chia cho 5 cố định — đã xác
minh bằng thực nghiệm ngày 07/09 (nộp 1 id, ngưỡng đặt trước 0,60–0,70, nhận về 0,702).

Hệ quả: `precision@m` trên dev300 là **m=1 → 0,7100** · m=2 → 0,4300 · m=3 → 0,3056 ·
m=5 → 0,1933. Nộp thêm id thứ `m+1` chỉ tăng precision nếu `p(m+1)` lớn hơn trung bình
hiện tại, điều không xảy ra với một danh sách đã xếp hạng. **Mọi bài nộp ở đây là 1 id.**

Cột **Score** trên *My Submissions* của Codabench là **recall**, không phải precision.
Tỉ số giữa hai độ đo cố định ở 0,9558 (do 1,047 gold/câu), nên so recall giữa hai bài
1-id là tương đương so precision.

---

## 1. Dữ liệu đầu vào

Repo không tái phát tán dữ liệu BTC. Đặt vào `data/` — xem `data/README.md`.

| file | kích thước (byte) | md5 (12 ký tự đầu) |
|---|---:|---|
| `public-official.json` | 186.517 | `d26eecddbecf` |
| `train.json` | 1.526.741 | `34a6b8ffdd1f` |
| `selected-contexts/` | 8.532 file | — |

---

## 2. Đường chạy — 5 bước

### Bước 1 · Rổ ứng viên — **Phần 1 của hệ thống, repo riêng**

> **Mã nguồn: [justySusanto/Task1_Retrieval](https://github.com/justySusanto/Task1_Retrieval)**

Hoà RRF giữa BM25 mức đoạn và bi-encoder `Vietnamese_Embedding`, giữ 50 văn bản/câu.

```
=> fusion_rrf_top50_public_matchEmbedded.json   207.470.561 B   md5 9917c01dd027
```

Rổ này là đầu vào cố định của mọi bước sau. Trần của nó là `recall@50 = 0,9832` trên
dev1000 — tức 98,3% số câu đã chứa đáp án, toàn bộ dư địa còn lại nằm ở khâu **chọn**.

### Bước 2 · Cross-encoder hai tầng (0 tinh chỉnh)

Model `AITeamVN/Vietnamese_Reranker` (0,568B — tốt nhất trong 10 model đã đối chứng,
xem `docs/bang_ablation.md`).

**Tham số phải đặt tay — mặc định của module KHÁC cấu hình đã nộp:**

```python
import deep_chunk as DC
DC.MERGE_CHARS = 1800        # mac dinh module la 0
M, K           = 20, 50      # mac dinh module la DEFAULT_M, DEFAULT_K = 10, 20
MAXLEN         = 1024
```

- **tầng 1** `ce`: chấm cả 50 văn bản/câu, mỗi văn bản 3 đoạn của rổ, lấy max.
- **tầng 2** `ce_deep`: 20 văn bản đầu bảng, mỗi văn bản `pick_chunks(k=50)` đoạn.
- **khoá xếp hạng cuối** là `max(ce, ce_deep)`, **không phải** `ce_deep`.

```
=> scores_public_M20K50_90e09359.json   4.137.008 B   md5 90e0935918d7
   50 ứng viên/câu · 20.000 bản ghi có ce_deep
```

Lấy `argmax max(ce, ce_deep)` ở đây và nộp 1 id được **precision 0,702** — mốc cơ sở
của bước 5.

### Bước 3 · Tập huấn luyện listwise · CPU, ~7 phút

```bash
python src/build_trainset.py        # -> trainset_listwise.jsonl
```

Thiết kế (đối chiếu chẩn đoán 19/08 về hai lượt tinh chỉnh hỏng trước đó):

- **1 dương + 4 âm, âm lấy ở hạng 10–20** của BM25. Hai lượt tinh chỉnh hỏng trước đây
  lấy âm ở top-20 — trong kho pháp luật, top-20 đầy văn bản trả lời được câu hỏi mà
  không được gán nhãn; dạy máy "những cái đó SAI" là dạy điều không đúng.
- **chọn đoạn đối xứng** cho cả dương lẫn âm: `pick_chunks(k=1)` cho mọi văn bản. Bất
  đối xứng (dương chọn bằng CE, âm chọn bằng BM25) sẽ dạy máy phân biệt *kiểu chọn đoạn*
  thay vì phân biệt liên quan — rò rỉ thắng, hỏng âm thầm.
- **loại toàn bộ `dev_1000_locked`** khỏi tập huấn luyện. `train.json ⊃ dev1000 ⊃ dev300`.

```
=> trainset_listwise_v2.jsonl   59.245.845 B   md5 492b6ae6b654   5.521 nhóm
```

### Bước 4 · Tinh chỉnh listwise · **45 phút T4**

`notebooks/finetune_listwise_run.ipynb`

```python
MODEL   = "AITeamVN/Vietnamese_Reranker"   # num_labels=1
MAXLEN  = 1024      # = max_length luc cham that
GROUPS  = 1         # 1 nhom = 5 cap. GROUPS=2 -> OOM tren T4
ACC     = 16        # batch hieu dung 16 nhom
LR      = 1e-5      # AdamW, weight_decay=0.01, OneCycleLR pct_start=0.1
EPOCHS  = 1
HOLDOUT = 400       # random.Random(0).shuffle(rows); val = rows[:400]
model.gradient_checkpointing_enable()      # KHONG CO -> OOM
# mat mat: Fn.cross_entropy(logits, zeros) -- softmax listwise trong nhom
```

Kiểm tra nội bộ: **0,8300 → 0,8975**. Không overfit (bước 500 đã 0,87).

### Bước 5 · Chấm đề thi và dựng bài nộp · **~52 phút T4**

`notebooks/public_ft_run.ipynb`

```python
N_DOC, K_CHUNK = 3, 50    # xep lai 3 van ban dau bang, doc TRON van ban
```

Mô hình tinh chỉnh chấm lại `order[q][:3]` (thứ tự theo `max(ce, ce_deep)` của bước 2),
điểm mỗi văn bản = max trên các đoạn đã chấm, chọn 1 văn bản cao nhất.

```
108.326 cặp · 34,7 cặp/s trên T4
=> public_ft_scores.json   1.345.729 B   md5 362c16b560cf
=> sub_FT_N3_k50.zip           7.575 B   md5 8254a2f60fbf
```

`K_CHUNK` **không suy được xuống nhỏ hơn** từ bộ điểm này. `pick_chunks` trả trọn văn
bản **theo thứ tự văn bản** khi `len(parts) <= k`, và top-k **theo thứ tự điểm** khi
`len(parts) > k` — hai tập khác nhau. Muốn đo `k` khác thì phải chấm lại.

---

## 3. Cổng kiểm — vì sao chúng tồn tại

Ba quy tắc dưới đây đều mua bằng một lượt chạy hỏng, không phải suy luận.

**Nhận diện dữ liệu vào bằng RUỘT, không bằng TÊN.** Một lượt chạy public hỏng đúng một
nửa vì `find()` đi bộ `/kaggle/input` và bắt được file **trùng tên nhưng khác ruột** —
`scores_public_fusion_M20_K50_matchEmbedded.json` có một bản M10 chỉ 10.000 bản ghi
`ce_deep`. Thứ tự `os.walk` đổi khi thêm/bớt dataset giữa các phiên, nên `assert` trên
tên file không bảo vệ được gì. Ô 1 nay chốt **md5 + hình dạng** (50 ứng viên/câu,
≥20.000 bản ghi `ce_deep`).

**`N=1` là dây tín hiệu.** Với `N_DOC=1` chỉ `order[q][0]` được xét, nên bài nộp **phải**
trùng khít bài cơ sở 0,702. Lệch một câu là rổ sai — dừng ngay, không cần biết `N=2`,
`N=3` ra sao. `assert dif == 0` nằm trong ô 3.

**Đặt vân tay vào TÊN file.** Tên trung tính thì bản cũ trà trộn được; tên
`scores_public_M20K50_90e09359.json` thì không bản nào giả dạng nổi.

Năm cửa kiểm chạy độc lập với notebook, trên CPU:

| cửa | kết quả phải có |
|---|---|
| số câu | 1000/1000 |
| rổ đã chấm `== order[:3]` | 1000/1000 |
| 500 câu đầu `==` seed | 500/500, không chấm lại |
| bài cơ sở dựng lại từ bộ điểm | khớp bài 0,702 ở 1000/1000 |
| zip khớp khi tính lại (N=1/2/3) | 1000 · 1000 · 1000 |

---

## 4. Những chỗ gói này KHÔNG tái lập được — nói thẳng

**① Trọng số mô hình tinh chỉnh không tái lập bit-perfect.** `finetune_listwise_run.ipynb`
seed thứ tự dữ liệu (`random.Random(0).shuffle`) nhưng **không** seed torch/CUDA. Chạy
lại bước 4 cho ra một mô hình *khác*, tuy cùng phân bố. Hiệu ứng đo được trên public là
**+0,9 điểm** với sai số lớn hơn thế, nên một lượt huấn luyện lại có thể ra 0,705 hoặc
0,715 mà không có gì sai. Cách sửa cho lượt sau, chưa áp vào bài đã nộp:

```python
import torch, random, numpy as np
torch.manual_seed(0); torch.cuda.manual_seed_all(0)
random.seed(0); np.random.seed(0)
torch.use_deterministic_algorithms(True, warn_only=True)
```

**② Sức mạnh bằng chứng của hiệu ứng tinh chỉnh.** Trên public: 192 câu đổi, **NET +9**.
Nếu cả 192 câu đều phân định thì `z = 9/√192 = 0,65` (p ≈ 0,52); kể cả chỉ 40 câu phân
định thì `z = 1,42` (p ≈ 0,16). **Không đạt ý nghĩa thống kê ở mọi giả định.** Ba nguồn
độc lập cùng dấu cùng cỡ (dev300 McNemar 22–8 p=0,0161 · lưới `richharness` thắng 20/20
ô · public +9/192) là lý do tin nó có thật, nhưng ước lượng điểm là **+0,9**, không phải +2.

**③ Không có dự đoán trên đề thi trong repo.** `.gitignore` loại `scores_public_*`,
`order_public*`, `submission*.zip`. Cuộc thi chưa kết thúc.

**④ File rổ ứng viên (bước 1) không kèm theo** — 207 MB mỗi file, quá lớn cho git.
Nhưng **mã nguồn dựng nó có**: [justySusanto/Task1_Retrieval](https://github.com/justySusanto/Task1_Retrieval).
Chạy Phần 1 trước để sinh rổ, rồi mới chạy các bước 2–5 ở repo này.

---

## 5. Kiểm lại trên CPU, không cần GPU

```bash
pip install -r requirements.txt
python src/k_tran.py <thu-muc-du-an>     # thu muc chua Input/ va Ketqua_E/
```

`src/k_tran.py` chạy đủ bộ cổng kiểm ở mục 3 rồi in trần của trục `k`. Cần bộ điểm của
bước 2 và bước 5 nằm đúng chỗ; không có thì script dừng ở `assert` chứ không ra số sai.
