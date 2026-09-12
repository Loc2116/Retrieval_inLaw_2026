# Báo cáo — Fine-tune listwise với negative hạng 2–10

**Người thực hiện:** Khim (thành viên E) · **Ngày:** 10–11/09/2026
**Kết luận:** ❌ **Không đạt ngưỡng. Đóng hướng. Giữ nguyên bài nộp `precision 0,711`.**

---

## 1. Tóm tắt

| | |
|---|---|
| thí nghiệm | huấn luyện lại cross-encoder listwise, **chỉ đổi dải hạng của negative**: 10–20 → **2–10** |
| kết quả huấn luyện | val nội bộ **0,7300 → 0,8150** (tăng đẹp, không overfit) |
| kết quả trên dev300 | **thắng 4 · thua 4 · hoà 4** trên 12 ô lưới so với model đang nộp |
| ngưỡng khoá trước | ≥ 9/12 ô **và** McNemar p<0,05 tại N=10,k=10 → **trượt cả hai** |
| chi phí | **~1,4 giờ GPU T4** (47 phút train + 25 phút lưới + 5 phút lượt hỏng) |
| giá trị thu được | đóng dứt điểm một giả thuyết lớn · **vá 1 lỗi guard** · **vá 1 lỗ tái lập** |

---

## 2. Vì sao thử hướng này

Cấu trúc lỗi trên dev300 (mốc sản xuất 0,7100, 82 câu sai):

| gold thực sự nằm ở hạng | số câu | % số câu sai |
|---|---|---|
| **2** | **41** | **50,0%** |
| 3 | 14 | 17,1% |
| 4–5 · 6–10 · 11–50 | 12 · 9 · 6 | 14,6% · 11,0% · 7,3% |

**67% câu sai có gold ở hạng 2–3.** Nhưng tập huấn luyện của model đang nộp lấy negative ở
**hạng 10–20** — tức model được dạy phân biệt trên một biên quyết định **nó không bao giờ phải
đối mặt**. Bằng chứng bổ sung: độ chính xác kiểm tra **trước khi huấn luyện** trên bộ 10–20 đã
là **0,83**, tức bài quá dễ.

**Giả thuyết:** chuyển negative về hạng 2–10 sẽ dạy model đúng biên nó phải quyết định.

**Rủi ro đã biết trước:** chẩn đoán 19/08 chỉ ra negative **quá khó** chính là nguyên nhân làm
hỏng hai lượt fine-tune đầu tiên (−0,50 rồi −6,50) — trong kho pháp luật, top-20 đầy văn bản
trả lời được câu hỏi mà không được gán nhãn. Lý do lần này khác: hai lượt đó là **pointwise**
(chấm điểm tuyệt đối), còn listwise softmax chỉ so **tương đối trong nhóm** nên chịu được
negative khó hơn nhiều.

---

## 3. Thiết kế — chỉ đổi MỘT biến

| | bài đang nộp (0,711) | thí nghiệm |
|---|---|---|
| model | `AITeamVN/Vietnamese_Reranker` 0,568B | y hệt |
| loss | `cross_entropy` softmax listwise | y hệt |
| LR · EPOCHS · HOLDOUT · MAXLEN · GROUPS · ACC | 1e-5 · 1 · 400 · 1024 · 1 · 16 | **y hệt** |
| **tập huấn luyện** | `trainset_listwise_v2.jsonl` — âm hạng **10–20** | `trainset_listwise_hard_clean.jsonl` — âm hạng **2–10** |

Hai tập **ghép cặp sạch**: cùng 5.507 nhóm, cùng tập qid, cùng nhãn dương 100%, và **0% nhóm có
âm trùng hoàn toàn** với bản kia.

### Phát hiện phụ khi dựng tập: nhãn tự mâu thuẫn
Khi kiểm ruột tập mới, phát hiện **13 nhóm có đoạn dương trùng Y HỆT một đoạn âm** (bộ cũ chỉ
có 1 nhóm). Nguyên nhân: văn bản pháp luật **sao chép nguyên điều/khoản** sang văn bản khác, nên
hai `doc_id` khác nhau chứa cùng một đoạn 1800 ký tự. Softmax listwise khi đó bị bảo *"đẩy chuỗi
X lên và đẩy chuỗi X xuống"* — gradient tự triệt tiêu.

Gấp 13 lần là đúng chiều dự đoán: càng gần hạng 1 càng nhiều văn bản trùng ruột. Đã thêm guard
vào cả hai script dựng tập và lọc ra hai bản `_clean` (5.507 nhóm mỗi bên, bỏ hợp của 14 qid rò rỉ).

### Ngưỡng khoá TRƯỚC khi chạy
So với **model đang nộp** (không phải so với model gốc), trên lưới `richharness` dev300:

1. FT-hard vượt FT-easy ở **≥ 9/12 ô**
2. Tại **N=10, k=10**: vượt **0,7433** **và** McNemar so sản xuất đạt **p<0,05**

*(FT-easy ở ô này đạt 0,7433, thắng 26 thua 10, p=0,0113 — nên đây là bar ngang bằng, không nới lỏng.)*

**Không đạt ⇒ đóng, không nộp.**

---

## 4. Sự cố: lượt chạy đầu bị dừng oan ở phút thứ 5

```
>>> CHOT 500 BUOC: loss giam -0.1208 · kiem tra 0.7650
!!! LOSS KHONG GIAM -> DUNG, dung ngoi cho het epoch.
```

Guard `if d < 0.02: break` (d = loss 100 bước đầu − loss 100 bước cuối) đã cắt lượt chạy khi mới
đi **500/5107 bước**.

**Guard sai, không phải model sai:**

- `ACC=16` ⇒ 500 bước batch = **~31 bước tối ưu**
- `OneCycleLR(pct_start=0.1)` trên `total_steps = 5107//16+1 = 320` ⇒ **warmup = 32 bước tối ưu**

Tức cửa sổ đo loss nằm **trọn trong giai đoạn warmup**: 100 bước đầu chạy ở LR≈0 (model gần như
không đổi, loss = loss ban đầu), 100 bước cuối ở LR≈max. **Loss tăng ở đó là đúng theo thiết kế.**

Bằng chứng model đang học tốt trong đúng 500 bước đó: **val acc 0,7300 → 0,7650**.

**Đã vá:** gate bằng **val acc** (`if v5 <= v0: break`) thay vì bằng loss.

> **Bài học ghi vào quy ước:** cổng đặt trước phải đo **đúng thứ mình quan tâm**. Một cổng đo
> sai thứ còn **tệ hơn không có cổng** — nó giết lượt chạy đang tốt và làm cả nhóm tưởng hướng
> đã chết. Nếu tin guard cũ thì hôm đó đã đóng oan hướng này.

Chạy lại xác nhận chẩn đoán: loss sau warmup tụt từ ~1,1 xuống **0,41–0,63** và giữ ở đó hết epoch.

---

## 5. Kết quả huấn luyện (hết 1 epoch, 47 phút)

| | bộ âm 10–20 (cũ) | bộ âm 2–10 (mới) |
|---|---|---|
| val acc **trước** huấn luyện | 0,8300 | **0,7300** |
| val acc **sau** huấn luyện | 0,8975 | **0,8150** |

Val acc trước huấn luyện thấp hơn 10 điểm ⇒ **thiết kế đạt mục tiêu: bài khó hơn thật.**

---

## 6. Kết quả trên dev300 — lưới richharness

Lưới có đối chứng model GỐC chạy cùng harness (điều kiện để so ghép cặp).

**Cửa kiểm harness QUA:** GỐC tại N=3,k=10 = **0,6933** · N=10,k=10 = **0,6900** — khớp **đúng**
bảng đã đo ngày 08/09. Harness tái hiện được ⇒ phép so tin được.

### Δ của FT-hard so với FT-easy (model đang nộp)

| | k=1 | k=3 | k=5 | k=10 |
|---|---|---|---|---|
| **N=3** | −0,0034 | −0,0033 | −0,0100 | **0** |
| **N=5** | −0,0100 | +0,0033 | +0,0067 | +0,0066 |
| **N=10** | **0** | **0** | +0,0067 | **0** |

**Thắng 4 · thua 4 · hoà 4.** Lệch lớn nhất ±0,01 = **±3 câu trên 300**.

### Đối chiếu ngưỡng

| điều kiện | cần | thực tế | |
|---|---|---|---|
| số ô vượt FT-easy | ≥ 9/12 | **4/12** | ❌ |
| N=10,k=10 | > 0,7433 | **0,7433** (bằng đúng) | ❌ |
| McNemar so sản xuất tại N=10,k=10 | p < 0,05 | **p = 0,1934** | ❌ |

*(FT-easy ở ô cuối đạt p = 0,0113 ⇒ FT-hard còn **kém hơn về ý nghĩa thống kê**.)*

### ⚠️ Cảnh báo về khuyến nghị tự động của notebook
Notebook in ra `TANG +0.0333 -> CHAY PUBLIC bang mo hinh FT roi NOP`. **Không được theo.**
Nó so với **sản xuất 0,7100** vì được viết từ thời chưa có FT-easy. Baseline đúng hiện nay là
**FT-easy 0,711**. Đây chính là cái bẫy mà việc khoá ngưỡng trước được dựng ra để chặn.

> **Quy tắc mới:** mọi ngưỡng in sẵn trong notebook phải được đối chiếu lại với **bài ĐANG NỘP**,
> không phải với mốc lúc notebook được viết.

---

## 7. Kết luận

**Dải hạng của negative không phải nút thắt.** Hai model — một học trên âm hạng 10–20, một trên
âm hạng 2–10 — **gần như không phân biệt được** trên dev300 (4-4-4, lệch tối đa 3 câu/300).

Giả thuyết *"model đang học sai biên quyết định"* đã được trả lời: **không phải.**

**Và một quy luật lặp lại lần thứ ba:** val acc nội bộ tăng đẹp (0,7300 → 0,8150) mà **không
chuyển thành điểm** trên thước thật. Cùng dạng với hai lần trước (cộng RRF, `replace`): dương
trên bộ đo phụ, phẳng hoặc âm trên bộ đo thật.

---

## 8. Chi phí và sản phẩm

| | |
|---|---|
| GPU | **~1,4 giờ T4** (5 phút lượt hỏng + 47 phút train + 25 phút lưới) |
| CPU | ~10 phút dựng tập + kiểm ruột |
| lượt nộp | **0** — không nộp bài nào, bài đang nộp không bị ảnh hưởng |

**File sinh ra:**

| file | nội dung |
|---|---|
| `trainset_listwise_hard.jsonl` · `_hard_clean.jsonl` | tập âm hạng 2–10 (5.521 / 5.507 nhóm) |
| `trainset_listwise_v2_clean.jsonl` | bản cũ đã lọc nhãn mâu thuẫn, để ghép cặp được |
| `finetune_hard_run.ipynb` | notebook thí nghiệm, đã vá guard + seed torch/CUDA |
| `rich_harness_dev300.json` | bộ điểm lưới 12 ô (trên Kaggle output) |

**Hai bản vá kỹ thuật giữ lại được, giá trị vượt ngoài thí nghiệm này:**

1. **Guard 500 bước** giờ gate bằng val acc, không bằng loss — không còn cắt oan lượt chạy trong warmup.
2. **Lỗ tái lập đã vá:** notebook cũ seed thứ tự dữ liệu nhưng **không seed torch/CUDA**, nên
   huấn luyện lại ra model khác. Với hiệu ứng chỉ +0,9 điểm và sai số lớn hơn thế, lượt train
   lại có thể trả về 0,705 hoặc 0,715 mà không có gì sai. Đã thêm:
   ```python
   torch.manual_seed(0); torch.cuda.manual_seed_all(0); random.seed(0); np.random.seed(0)
   torch.use_deterministic_algorithms(True, warn_only=True)
   ```
   **Đây là mục phải ghi vào báo cáo tái lập cho BTC.**

---

## 9. Việc tiếp theo

| # | việc | chi phí | ghi chú |
|---|---|---|---|
| 1 | **Gói tái lập** — review + commit | 0 GPU | BTC **bắt buộc**, hạn **18/09**, bản đầu đã xong |
| 2 | Bộ phân xử cặp (pairwise judge) | ~1h GPU | hướng lớn nhất còn lại: trần **+13,7 điểm**, hoà vốn **70,1%** |
| 3 | ~~Khớp phạm vi pháp lý~~ | — | **đã đóng 11/09**: trần dev1000 chỉ **1,60 điểm**, dưới sàn nhiễu LB 1,45 |

Về (2): với `N=3` chỉ có 3 cặp mỗi câu nên **chưa cần thang Elo** — bước đầu chỉ cần judge trả
lời đúng cặp hạng 1 vs hạng 2 **trên 70,1%**. Dưới ngưỡng đó thì đóng, không cần chạy đề thi.
