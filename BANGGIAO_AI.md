# BÀN GIAO NGỮ CẢNH — DSC 2026 Task 1 (Legal IR), lane thành viên E

> **Cách dùng:** nạp cả file này vào AI trước khi hỏi bất cứ điều gì về dự án.
> Đây là bản **sơ lược**. Chi tiết đầy đủ: `CLAUDE.md` (1.500 dòng) ·
> đường chạy tái lập: `repo_github/REPRODUCE.md`.
> Cập nhật: 10/09/2026.

---

## 1. Bài toán

| | |
|---|---|
| việc | cho 1 câu hỏi pháp luật, tìm văn bản chứa câu trả lời trong kho **8.532 văn bản** |
| dữ liệu | `Input/train.json` 7.000 câu có nhãn · `Input/public-official.json` 1.000 câu đề thi (answer=null) · `Input/selected-contexts/` corpus |
| **độ đo chính** | **PRECISION** (email BTC 02/08), recall chỉ dùng khi bằng điểm |
| công thức | precision chia cho **số id THỰC NỘP**, không chia 5 cố định — đã xác minh thực nghiệm 07/09 |
| ⇒ | **luôn nộp ĐÚNG 1 id/câu.** Đã chứng minh, đóng vĩnh viễn |
| hạn | **18/09/2026 23:59 GMT+7** · còn vòng **Private Test** riêng |
| tài nguyên | ~100 lượt nộp · ~20h GPU/tuần (Kaggle T4) |

`precision@m` trên dev300: **m=1 → 0.7100** · m=2 → 0.4300 · m=3 → 0.3056 · m=5 → 0.1933.
Nộp thêm id thứ m+1 chỉ tăng precision nếu p(m+1) > trung bình hiện tại — không bao giờ đúng
với danh sách đã xếp hạng.

⚠️ Cột **Score** trên Codabench là **recall**, không phải precision (tỉ số cố định 0,9558).
Bảng xếp hạng hiển thị bài **NỘP MỚI NHẤT**, không phải bài tốt nhất.

### Ràng buộc cứng
- **Ngân sách tham số: cả đội 4B.** D lấy 1B (truy hồi) ⇒ **E còn ~3B.**
  Lượng tử hoá KHÔNG nới được. Qwen3-Reranker-4B = 4,02B → **ngoài ngân sách.**
- **Mọi LLM thương mại (GPT/Gemini/Claude) KHÔNG được dùng để chấm điểm.**
- Cấm gán nhãn tay, cấm dữ liệu ngoài.
- ⚠️ Dưới NF4, `sum(p.numel())` báo chưa tới một nửa số thật. **Phải đếm, đừng tin tên repo.**

---

## 2. Trạng thái hiện tại

| | |
|---|---|
| **bài đang nộp** | `Ketqua_E/lai_ft/sub_FT_N3_k50.zip` — **precision 0,711** |
| **hạng** | **3/84** · GoGo 0,7210 (cách 19 câu) · CMTT 0,7060 (cách 4 câu) |
| lưới an toàn | `Ketqua_E/probe_top1/A_K50_max_DANGNOP.zip` — 0,702 |
| sàn nhiễu LB | ~**1,45 điểm** ở n=1000 ⇒ khoảng cách tới hạng 2 **nằm trong nhiễu** |

⚠️ **Còn ~100 lượt nộp là đủ để dò ra +0,4 điểm public bằng may rủi — và đó chính xác là cách
mất hạng ở vòng private.** Dò LB là fit vào nhiễu, không phải cải tiến.

---

## 3. Pipeline (đúng cấu hình đang nộp)

```
Kho 8.532 văn bản
  ↓ cắt đoạn theo Điều/Khoản, gộp tới MERGE_CHARS=1800
TẦNG 0 (thành viên D) — BM25 mức đoạn ⊕ bi-encoder Vietnamese_Embedding, hoà RRF
  → rổ 50 văn bản/câu + 3 đoạn tốt nhất mỗi văn bản
  → fusion_rrf_top50_public_matchEmbedded.json   (md5 9917c01dd027)
  ↓
TẦNG 1  ce       — CE chấm cả 50 vb/câu, 3 đoạn của rổ, lấy max
TẦNG 2  ce_deep  — M=20 vb đầu bảng, mỗi vb pick_chunks(k=K=50) đoạn
  KHOÁ XẾP HẠNG = max(ce, ce_deep)      ← KHÔNG phải ce_deep
  → scores_public_M20K50_90e09359.json   (md5 90e0935918d7)
  → argmax + nộp 1 id = precision 0,702
  ↓
TẦNG 3  FT listwise — CÙNG model, đã tinh chỉnh, chấm lại order[:3]
  N_DOC=3, K_CHUNK=50 (đọc TRỌN văn bản)
  → public_ft_scores.json (md5 362c16b560cf) → sub_FT_N3_k50.zip = 0,711
```

**Model:** `AITeamVN/Vietnamese_Reranker` (0,568B) — tốt nhất trong 10 model đã đối chứng
(`bang_ablation.md`). Số tham số KHÔNG dự đoán chất lượng: `mMiniLMv2` 0,118B hơn
`ViRanker` 0,568B tới +3,50 điểm.

**Tham số phải đặt tay** — mặc định module KHÁC cấu hình đã nộp:
`DC.MERGE_CHARS=1800` (mặc định 0) · `M,K = 20,50` (mặc định 10,20) · `MAXLEN=1024`.

### Fine-tune listwise (bước ăn điểm duy nhất của dự án)
```python
TRAIN   = trainset_listwise_v2.jsonl   # 5521 nhom, md5 492b6ae6b654
MODEL   = "AITeamVN/Vietnamese_Reranker"  # num_labels=1
MAXLEN=1024 · GROUPS=1 · ACC=16 · LR=1e-5 · EPOCHS=1 · HOLDOUT=400
model.gradient_checkpointing_enable()          # KHONG CO -> OOM tren T4
loss = Fn.cross_entropy(logits, zeros)         # softmax listwise trong nhom
```
Tập huấn luyện: 1 dương + **4 âm hạng 10–20**, `pick_chunks(k=1)` **đối xứng** cho cả dương
lẫn âm, loại toàn bộ `dev_1000_locked`. Kiểm tra nội bộ **0,8300 → 0,8975**. 45 phút T4.
Chấm đề thi: 108.326 cặp, **34,7 cặp/s**, ~52 phút.

---

## 4. Dư địa còn lại — đo trên dev300 (300 câu, thước = đúng ở hạng 1)

| mốc | điểm |
|---|---|
| thứ tự rổ RRF (không chấm lại) | 0.5933 |
| `ce` (tầng 1) | 0.6100 |
| `ce_deep` (tầng 2) | 0.6900 |
| **`max(ce, ce_deep)` = mốc sản xuất** | **0.7100** |
| FT listwise @ N=3,k=10 | 0.7467 |
| trần nếu thu hẹp còn 3 ứng viên | 0.8933 |
| **trần của rổ (recall@50)** | **0.9883** (dev1000: 0.9832) |

**Toàn bộ dư địa nằm ở khâu CHỌN, không ở khâu lấy rổ.**

### Cấu trúc lỗi — 82 câu sai của mốc 0.7100
| gold thực sự ở hạng | số câu | % câu sai |
|---|---|---|
| **2** | **41** | **50,0%** |
| 3 | 14 | 17,1% |
| 4–5 · 6–10 · 11–50 | 12 · 9 · 6 | 14,6% · 11,0% · 7,3% |

**67% câu sai có gold ở hạng 2–3.** Đây KHÔNG phải bài toán truy hồi, mà là bài toán
**phân biệt hai văn bản gần giống nhau**.

### Margin (chênh điểm hạng 1 − hạng 2) = thước độ tin cậy
| ngũ phân vị theo margin | tỉ lệ đúng |
|---|---|
| 1/5 (0.000–0.002) · 2/5 · 3/5 | 0.600 · 0.600 · 0.617 |
| 4/5 · 5/5 (0.509–0.986) | 0.817 · **0.917** |

⇒ 60% câu margin thấp chỉ đúng ~0,61. Can thiệp chỉ vào dải đó + chỉ 2–3 ứng viên đầu
**rẻ hơn lượt chấm hiện tại ~28 lần**.

**Ngưỡng hoà vốn của bộ phân xử cặp: 70,1%** (dev1000) / 70,8% (dev300).

### dev300 vs dev1000
`base` (chỉ `ce`) top-1: dev300 **0.6100** · dev1000 **0.6110** — lệch 0,10 điểm.
⇒ hai tập **tương đương về mức tuyệt đối**; dev1000 chỉ mua **độ phân giải**.
`train.json 7000 ⊃ dev1000 ⊃ dev300`.

---

## 5. HƯỚNG ĐÃ ĐÓNG — mỗi dòng là một phép đo đã trả tiền. Đừng đào lại.

| hướng | số liệu đóng nó |
|---|---|
| nộp 2–5 id | precision@m giảm đơn điệu (0.7100 → 0.1933) |
| `replace` thay vì `max(ce,ce_deep)` | **LB −3,1 điểm** trên 133 câu bất đồng |
| cộng λ·RRF vào điểm CE (late fusion) | dev +0,6…+2,3 (p≥0.109) → **LB −0,9** |
| **nhét điểm BM25 vào input (CE_BM25CAT)** | **53,7% trên tập cứu được = tung xu.** Xem §7 |
| **trục `k`** (k=10/20 vs k=50) | k=20 đổi ~17 câu/1000 = dưới sàn nhiễu. Xem §7 |
| góc nhìn `head`/tiêu đề | đứng riêng +3,67 nhưng ghép vào pipeline âm mạnh (p<0.001) — `ce_deep` bao trùm |
| model to hơn (4B/7B/8B) | 15 câu khó, đúng ở hạng 1: CE 0,568B **5/15** · 4B 4/15 · 8B 4/15 · 7B **1/15**. Quy mô mua RECALL, không mua PRECISION |
| chưng cất từ 8B | NET −16 nhóm/600. **Thầy 0,5417 THUA trò 0,5683** |
| fine-tune kiểu cũ (pointwise) | −0,50 rồi −6,50. Nguyên nhân: âm lấy từ top-20 = quá khó cho pointwise |
| ưu tiên văn bản mới / năm ban hành | gold là vb mới nhất đúng **2,0%** = ngẫu nhiên. p=0.000 |
| ưu thế theo loại vb / thẩm quyền (**toàn cục**) | âm, kể cả khi ước tham số ngay trên dev300 |
| khớp tiêu đề, hoà z-score, ensemble, trộn 2 pipeline | tất cả p>0.2, dưới sàn nhiễu |
| mở rộng M, nâng K, chọn đoạn, thứ tự trong rổ | trần +1,7 / +0,06 / +1–2 / 0 — lane của D đã cạn |
| hướng trích dẫn / số hiệu văn bản | câu hỏi chứa số hiệu: **3/300**. Đề bài là ngôn ngữ đời thường |
| dev300 "là mẫu dễ" | **RÚT LẠI** — đo trên recall@5, không phải hạng 1 |

**Bài học lặp lại 2 lần:** dương nhất quán trên dev + p>0.05 **KHÔNG phải bằng chứng yếu, mà
là KHÔNG CÓ bằng chứng** (RRF và `replace` đều dương trên dev rồi âm trên LB).

---

## 6. Việc 08/09 — sự cố bộ điểm trùng tên (đọc kỹ, sẽ lặp lại)

Bản chạy public FT đầu tiên **hỏng đúng một nửa**. Bài `N=1` lệch bài cơ sở 104/1000 câu
trong khi nó **phải** trùng khít. Đếm theo khối 100 câu: `[0,0,0,0,0,56,53,43,53,45]` —
ranh giới sạch ở câu 500.

Nguyên nhân: `find()` đi bộ `/kaggle/input` và bắt được file **trùng đúng tên nhưng khác
ruột** — bản M10 chỉ 10.000 bản ghi `ce_deep` thay vì 20.000. Thứ tự `os.walk` đổi khi
thêm/bớt dataset giữa các phiên. **Một cái tên trỏ vào hai thứ khác nhau.**

Ba quy tắc rút ra:
- **8.** Nhận diện dữ liệu vào bằng **RUỘT**, không bằng **TÊN** — chốt md5 + hình dạng.
- **9.** **`N=1` là dây tín hiệu.** Bài `N=1` không trùng khít bài cơ sở ⇒ rổ sai, dừng ngay.
- **10.** **Đặt vân tay vào TÊN file** — `scores_public_M20K50_90e09359.json`.

Cứu được: bài lai (FT nửa đầu + gốc nửa sau) = **0,712**, rồi bản sạch `N=3` = **0,711**.

| | câu đổi | NET |
|---|---|---|
| nửa đầu (bài lai) | 97 | **+10** |
| nửa sau (mới) | 95 | **−1** |
| **gộp** | **192** | **+9** → 0,711 |

**Đọc đúng:** chênh hai nửa 11 câu, sd≈13,9 → z≈0,79 ⇒ **hai nửa tương thích, nửa đầu chỉ
MAY.** Gộp +9/192: z=0,65 (p≈0,52); kể cả chỉ 40 câu phân định thì z=1,42 (p≈0,16).
**Không đạt ý nghĩa ở mọi giả định.** Ước lượng tốt nhất cho hiệu ứng FT: **+0,9 điểm.**

Nhưng đây là **hiệu ứng ĐẦU TIÊN sống sót khi ra bảng thật** — dev300 dự đoán +1,4…+1,9,
thực nhận +1,0, cùng chiều cùng cỡ. Ba nguồn độc lập cùng dấu: dev300 McNemar 22–8
(p=0,0161) · lưới `richharness` FT thắng gốc **20/20 ô** · public +9/192.

**0,712 và 0,711 lệch ĐÚNG 1 CÂU** — chọn cái cao hơn là chọn nhiễu, và bài lai còn là
phương pháp không nhất quán.

---

## 7. Việc 10/09 (mới nhất)

### ⛔ Trục `k`: ĐÓNG, 0 giây GPU
Dòng cũ *"93% văn bản chạm trần k=10 ⇒ k=20 còn đất"* **đã lạc hậu** — bản chạy public đặt
`K_CHUNK=50`, tức **đã đọc trọn văn bản** (trung vị 47 đoạn/vb).

Không dựng được bài k=10 từ bộ điểm đã có: `pick_chunks` trả trọn văn bản **theo thứ tự văn
bản** khi `len(parts) <= k`, top-k **theo thứ tự điểm** khi lớn hơn ⇒ chỉ 1448/3000 (48,3%)
cặp suy được. Trên tập suy được:

| hạ k từ 50 xuống | câu đổi (235 câu) | quy ra 1000 |
|---|---|---|
| k=35 · k=20 · k=10 | 2 · **4** · 20 | ~9 · **~17** · ~85 |

k=20 đáng ~1,7 điểm **trần**, dưới sàn nhiễu 1,45 — và đó là số câu ĐỔI, không phải NET.
Cộng với trục k **đơn điệu TĂNG** trên dev300 (k=1 0.6667 → k=10 0.7467) ⇒ kỳ vọng ròng ≈ 0.

### ⛔ CE_BM25CAT (arXiv 2301.09728): ĐÓNG
Ý tưởng: nhét điểm tầng 1 vào input dạng text `[CLS] q [SEP] <điểm> [SEP] passage [SEP]`
rồi fine-tune. MSMARCO +2,3 điểm và **thắng hẳn interpolation (.422 vs .353)** — nên phép
cộng RRF âm của nhóm KHÔNG phủ định được nó. Phải đo.

`bm25cat_tran.py` (CPU, dev300):

| tập | điểm tầng 1 trỏ đúng ứng viên |
|---|---|
| **cứu được (41 câu, gold ở hạng 2)** | **22/41 = 53,7%** ← tung xu |
| đang đúng (213 câu) | 183/213 = 85,9% |

Đi theo nó trên top-2: cứu 22 · hỏng 24 · **NET −2 câu**. Trần oracle (chỉ dùng khi nó
giúp): +22 câu = +7,33 điểm.

**Điểm không thành:** BM25 đã bị tiêu thụ **hai lần** rồi (dựng rổ qua RRF + chọn đoạn qua
`pick_chunks`), nên nhét lần ba không thêm bit nào. Sâu hơn là **thu hẹp miền giá trị**: cả
hai ứng viên top-2 đều đã được chính điểm tầng 1 chọn vào rổ ⇒ phương sai còn lại là nhiễu.
Biến thể BM25 **theo từng đoạn** còn kém hơn (58,3% ở tập đang đúng ⇒ phá hệ thống).

⚠️ **Bẫy tỉ lệ nền đã tránh:** số thô cho "80,7% gold có điểm tầng 1 cao hơn", nhìn như vượt
hoà vốn 70,8%. Sai — 84% câu top-2 đã đúng sẵn. Tách ra còn 53,7%.

**Giữ lại được:** biểu diễn min-max **toàn cục → số nguyên → chuỗi** là tốt nhất (bảng
ablation của họ). Nếu sau này cần nhét scalar vào input thì dùng luôn, khỏi dò.

### ✅ Tập huấn luyện âm hạng 2–10: ĐÃ XONG, chưa train
`build_trainset_hard.py` viết 08/09 nhưng chỉ chạy được 1193/5521 nhóm rồi ngắt và **chưa
bao giờ được train**. Đã build nốt.

| file | nhóm | dải hạng của âm |
|---|---|---|
| `trainset_listwise_v2.jsonl` (bài 0,711 dùng) | 5521 | 10–20 |
| `trainset_listwise_hard.jsonl` | 5521 | **2–10** |
| `trainset_listwise_v2_clean.jsonl` | **5507** | 10–20 |
| `trainset_listwise_hard_clean.jsonl` | **5507** | **2–10** |

Kiểm ruột: cùng tập qid · cùng nhãn dương 5521/5521 · 0% nhóm có âm trùng hoàn toàn với bản
dễ ⇒ **ghép cặp sạch, chỉ đổi một biến**.

**Phát hiện:** 13 nhóm có đoạn dương **trùng y hệt** một đoạn âm (bộ dễ chỉ 1 nhóm). Văn bản
pháp luật sao chép nguyên điều/khoản sang văn bản khác ⇒ softmax listwise bị bảo "đẩy chuỗi
X lên và đẩy chuỗi X xuống". Đã thêm guard vào cả hai script build; bản `_clean` bỏ hợp của
14 qid rò rỉ.

### ✅ Gói tái lập: XONG
`repo_github/REPRODUCE.md` — đường chạy 5 bước cho bài 0,711, md5 cả 7 tạo phẩm (đã verify
7/7), tham số phải đặt tay, 3 cổng kiểm, và mục "những chỗ KHÔNG tái lập được".

🔴 **Lỗ tái lập:** notebook huấn luyện seed thứ tự dữ liệu (`random.Random(0).shuffle`) nhưng
**không seed torch/CUDA** ⇒ train lại ra mô hình KHÁC. Hiệu ứng FT chỉ +0,9 với sai số lớn
hơn thế ⇒ lượt train lại có thể trả 0,705 hoặc 0,715 mà không có gì sai. Thêm cho lượt sau:
```python
torch.manual_seed(0); torch.cuda.manual_seed_all(0); random.seed(0); np.random.seed(0)
torch.use_deterministic_algorithms(True, warn_only=True)
```

---

## 8. VIỆC TIẾP THEO, theo thứ tự

### ① Train trên `trainset_listwise_hard_clean.jsonl` — 45 phút T4
**Lý do:** 67% câu sai có gold ở hạng 2–3, nhưng mô hình đang học trên âm hạng 10–20 —
**một biên quyết định nó không bao giờ phải đối mặt**. Kiểm tra nội bộ TRƯỚC huấn luyện trên
bộ dễ đã là 0,83 = bài quá dễ.

**NGƯỠNG KHOÁ TRƯỚC KHI CHẠY:** đo trên dev300 bằng đúng lưới `richharness`.
Nhận nếu **thắng bản FT hiện tại ở ≥15/20 ô** VÀ McNemar tại N=3,k=10 cho **p<0.05**.
Không đạt ⇒ **đóng, không nộp.**
Chỉ đổi MỘT biến: giữ nguyên loss, LR, EPOCHS, HOLDOUT, MAXLEN.

### ② Bộ phân xử cặp + gộp kiểu Elo
Hướng duy nhất chưa thử, trần **+13,7 điểm** (phân biệt hoàn hảo hạng 1 vs 2), hoà vốn
**70,1%**. CE hiện tại chấm từng cặp (câu, văn bản) **độc lập** — nó chưa bao giờ nhìn hai
ứng viên cạnh nhau.

Công thức lấy từ `zerank-1` (ZeroEntropy): bỏ điểm tuyệt đối pointwise → **sở thích theo
cặp** → huấn luyện **comparator nhỏ** → gộp nhiều lượt đối đầu thành thang toàn cục bằng
**mô hình kiểu Elo**, kèm học độ lệch riêng theo từng câu. **Elo trả lời phần nhóm còn thiếu:
cách gộp phán quyết cặp thành thứ hạng.**

Điều kiện: comparator phải **học trong miền** — bằng chứng là FT listwise đã lật dấu từ âm
sang dương trên đúng model đó.

### ③ Đặc trưng khớp phạm vi pháp lý — CPU, 0 GPU, 0 tham số
**Chưa đo.** Kiểu lỗi thật của nhóm là **thẩm quyền/phạm vi**: ca `138214` model chọn QĐ UBND
Hà Nội thay vì Nghị định toàn quốc — **trùng chữ nhiều hơn nhưng sai phạm vi**. CE chấm
tương đồng câu hỏi–đoạn **không có chỗ biểu diễn thứ bậc pháp lý**.

Nhóm đã thử "ưu thế theo loại vb/thẩm quyền" → âm, **nhưng đó là ưu thế TOÀN CỤC**. Quy tắc 5
nói: *ưu thế toàn cục không thắng nổi bộ chấm, trừ khi nó nói được điều gì riêng cho từng câu.*
Dạng đúng là **khớp phạm vi** (câu hỏi toàn quốc/địa phương × văn bản cấp nào) — đặc trưng
theo cặp, không phải prior. `Ketqua_E/vanban_meta.json` đã có 5.244 vb kèm loại · năm · cấp
địa phương. Đo trần trên 41 câu cứu được: >70,8% thì có cửa, <55% thì đóng.

### ④ LLM + prompt: CHƯA kết luận được (không phải đã đóng)
Lần trước hỏng vì dùng LLM **pointwise** — cách dùng tệ nhất (ZeroEntropy: pointwise LLM
"uncalibrated, worst of both worlds"). Nên 4/15 · 4/15 · 1/15 **không** phải bằng chứng LLM
vô dụng; nó **bị nhiễu biến** giữa hai thứ:
- **thất bại phương pháp** (kiến thức có trong trọng số, hỏi sai cách) → prompt/pairwise sửa được
- **thất bại kiến thức** (không có trong trọng số) → không prompt nào lấy ra được

**Phép thử tách hai thứ:** lấy 13 ca khó, hỏi model trong ngân sách 3B **câu hỏi kiến thức
tách khỏi xếp hạng** — *"câu này phạm vi toàn quốc hay địa phương?"*, *"văn bản này cấp nào
ban hành?"*. Sai → đóng dứt điểm. Đúng → prompt + pairwise là hướng sống.

Vướng: E còn ~3B, và Qwen2.5-7B (to nhất đã thử) lại **tệ nhất** (1/15).

### ⑤ Gói tái lập — hạn 18/09, đã xong bản đầu, cần Khim review + commit
⚠️ `repo_github/.git` còn sót `index.lock` + `HEAD.lock` — xoá trước khi commit.

---

## 9. QUY LUẬT & BẪY — đọc TRƯỚC khi đề xuất bất kỳ thí nghiệm nào

1. **Ngưỡng phải TƯƠNG ĐỐI so với mốc hiện có**, không bao giờ là số tuyệt đối bốc ra.
2. **Mọi phép đo bộ chấm phải in kèm dòng "rổ trần, không reranker".** Thua dòng đó thì DỪNG.
3. **Không đánh giá model B trên mẫu được chọn bằng LỖI của model A.** Hồi quy về trung bình.
4. **Mọi con số dư địa phải đo ở ĐÚNG cấu hình bài đang nộp**, ghi kèm cấu hình bên cạnh số.
5. **"Có tín hiệu thô" ≠ "cộng vào được".** Ưu thế TOÀN CỤC không thắng nổi bộ chấm đã đọc
   nội dung, trừ khi nó nói được điều gì **riêng cho từng câu**.
6. **"Không thấy hiệu ứng ở MỘT điểm đo" ≠ "hiệu ứng không tồn tại".**
7. **Nhiều "giải pháp" hoá ra là một — đừng cộng dồn.** Đọc sâu, tiêu đề, rổ tốt hơn, chấm
   lại: tất cả sửa **cùng một nhóm câu**. **Kiểm chồng lấn TRƯỚC khi cộng.**
   *(Đã kiểm thật: 2 cần gạt cộng dồn ngây thơ +2,33 → gộp thật chỉ +1,33.)*
8. **Chỉ chạy thí nghiệm kỳ vọng đổi ≥2 điểm.** Dưới ~1,5 là dưới sàn nhiễu dev300.
9. **Đo trần TRƯỚC khi chạy.** Đã cứu M=30 (~4h), chưng cất (~18h), trục k (16 phút + 2 lượt nộp).
10. **Ước chi phí trên phân bố của VĂN BẢN ĐƯỢC TRUY HỒI, không phải toàn kho.** Đã ước sai
    gấp đôi (6,6h → 13,1h thật) và sai 3,7× theo chiều ngược lại (9,35 vs 34,7 cặp/s).
    **Đừng mượn thông lượng đo ở cấu hình khác.**

### Bẫy kỹ thuật
- **⑧ KHOÁ XẾP HẠNG LÀ `max(ce, ce_deep)`, KHÔNG PHẢI `ce_deep`.** Dùng sai khoá đã ra kết
  luận **ngược dấu**. ⇒ **Mọi phân tích CPU phải dựng lại bài nộp và kiểm khớp 1000/1000
  TRƯỚC khi đọc bất kỳ Δ nào.** Mất 5 giây, đã cứu một kết luận sai hoàn toàn.
- Đường dẫn Kaggle: tự dò, kiểm bằng **có file `context_*.json` bên trong**, không phải `isdir`.
- Cache vector kiểm bằng số hàng là kiểm hờ (đoạn 900 và 1800 ký tự cùng số hàng) → **đổi TÊN
  file theo cấu hình**.
- `deepen_all` **chỉ trả về câu được truyền vào** → phải `scores.update(...)`, đừng gán đè.
- `deepen_all` **không ghi đệm** → mọi vòng lặp GPU dài phải tự lưu theo lô.
- Kaggle Accelerator = None ⇒ image CPU ⇒ `Torch not compiled with CUDA`.
- Guard kiểm bằng `inspect.getsource` tự bắn vào chân (docstring trích code cũ) → kiểm bằng
  **chữ ký hàm** hoặc hành vi.
- **Vượt 5 id ở một câu → CHỈ câu đó bị 0**, không phải cả bài.
- ⚠️ **Trình duyệt của AI không tải file lên Codabench được.** AI dựng file, **người nộp**.

### Bài học quy trình (đã dính 3 lần)
**Đọc danh sách hướng đã đóng + 10 quy tắc + mã của lượt chạy trước, TRƯỚC khi đề xuất thí
nghiệm.** Ba lần đề xuất thứ mà kết luận đã nằm sẵn trong file: `headview_run` (07/09),
trục k (10/09 — ô 1 của `public_ft_run.ipynb` đã có comment nói đúng lý do), và suy "LLM thiếu
domain knowledge" từ một thí nghiệm pointwise (10/09 — nhiễu biến, đã rút).

---

## 10. FILE QUAN TRỌNG

| file | nội dung |
|---|---|
| `CLAUDE.md` | **nguồn sự thật, 1.500 dòng.** Mọi kết luận kèm phép đo đứng sau nó |
| `CLAUDE_LUUTRU_den_28-08.md` | nhật ký chi tiết 12–28/08 (4.009 dòng) |
| `repo_github/REPRODUCE.md` | đường chạy 5 bước tái lập bài 0,711 |
| `Ketqua_E/lai_ft/` | bộ điểm + 4 bài nộp của tầng FT |
| `Ketqua_E/probe_top1/` | 10 bài nộp "0 GPU" dựng từ bộ điểm đã có |
| `bm25cat_tran.py` · `k_tran.py` | đo trần trên CPU, **có sẵn đủ cổng kiểm bài nộp** |
| `dev1000_doc.py` | danh sách phép đo dev1000 đã khoá trước khi số về |
| `bang_ablation.md` | đối chứng 10 cross-encoder trên cùng 15.000 cặp |
| `Ketqua_E/vanban_meta.json` | 5.244 vb: loại · năm · có phải cấp địa phương |
| `finetune_listwise_run.ipynb` · `public_ft_run.ipynb` | 2 notebook sinh ra bài đang nộp |
| `richharness_run.ipynb` | lưới N×k để đo bản FT trên dev300 |

**Quy ước trả lời (Khim chốt 10/09):** ngắn, dễ hiểu, kết luận trước. Đưa kết luận + số quyết
định + việc cần làm. Khim sẽ tự hỏi khi cần bóc chi tiết.
