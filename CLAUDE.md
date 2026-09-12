# project_DSC — DSC2026 Task 1 (LegalIR) · thành viên E

> **Bản CỐT LÕI, gọn lại 28/08.** Toàn bộ nhật ký chi tiết 12–28/08 nằm ở
> `CLAUDE_LUUTRU_den_28-08.md` (4.009 dòng). Chỉ mở file đó khi cần dựng lại lý do
> của một kết luận cụ thể — mọi thứ cần để **làm việc** đều có ở đây.

## 🎯 TRẠNG THÁI

| | |
|---|---|
| **BÀI CHỐT** | `Ketqua_E/submission_matchEmb_K50_n2.zip` — **public LB 0.9124** (30/08) |
| cấu hình | rổ `_matchEmbedded` của D · `M=20` · **`K=50`** · `MERGE_CHARS=1800` · **`blend n_bm25=2`** |
| model | `AITeamVN/Vietnamese_Reranker` (0,568B) — tốt nhất trong 10 model đã đối chứng |
| hạn chót | **15/09** · quota GPU 60h/tuần (dư gấp ~3 lần kế hoạch) |
| mục tiêu hiện tại | **tối đa điểm public** — phải lọt top mới vào vòng private |

**Đang chạy / chờ chạy:**

1. ~~`fusion_k50_run.ipynb` — nâng `K` 20→50~~ **✅ XONG 30/08. ĐÓNG — xem mục K50 dưới.**
   Cả 1000 câu đã có `ce_deep` (đúng 20 vb/câu). Kỳ vọng ròng **+0,06 câu = +0,006 điểm LB**.
   Đừng nộp; đừng chạy `K` cao hơn.

2. `fusion_dev1000_run.ipynb` — kiểm `n=3` trên 1000 câu dev (~3,8h + 1,7h). **Phòng thủ cho vòng private, hoãn được** nếu đang gấp điểm public.

## 🏆 08/09 — **FINE-TUNE LISTWISE ĂN THẬT. Kết quả dương có ý nghĩa đầu tiên của cả dự án.**

Huấn luyện 5121 nhóm (1 dương + 4 âm hạng 10–20), softmax listwise, 45 phút GPU T4.
Kiểm tra nội bộ **0.8300 → 0.8975**. Không overfit (bước 500 đã 0.87, cuối epoch 0.8975).

### Bằng chứng sạch nhất: XẾP LẠI top-N làm mô hình GỐC tệ đi, làm mô hình FT tốt lên

So với **0.7100 = không xếp lại gì** (chỉ lấy top-1 của bản sản xuất):

| harness | mô hình GỐC | mô hình FT |
|---|---|---|
| N=2, k=10 | **−1,33** | **+3,33** |
| N=3, k=10 | **−1,67** | **+3,67** |
| N=5, k=10 | **−2,00** | **+2,67** |
| N=10, k=10 | **−2,00** | **+3,33** |

Cùng ứng viên, cùng số đoạn, cùng mã — **chỉ khác trọng số. Ngược dấu ở mọi cấu hình.**
FT thắng GỐC ở **12/12 ô** của bảng N×k. McNemar tại N=10,k=10: **thắng 26 thua 10, p=0.0113**.

⇒ Câu *"chấm lại 50 ứng viên bằng cross-encoder ra kém hơn không chấm"* (mục 📝 BÁO CÁO #3)
**đúng với mô hình gốc và sai với mô hình đã học trong miền.** Sửa lại khi viết báo cáo.

### Bảng N×k (dev300, FT) — đọc hình dạng, không chọn ô đẹp

| | k=1 | k=3 | k=5 | k=8 | k=10 |
|---|---|---|---|---|---|
| N=2 | 0.6867 | 0.7300 | 0.7333 | 0.7367 | **0.7433** |
| N=3 | 0.6667 | 0.7300 | 0.7300 | 0.7367 | **0.7467** |
| N=5 | 0.6633 | 0.7100 | 0.7200 | 0.7267 | 0.7367 |
| N=10 | 0.6567 | 0.7133 | 0.7233 | 0.7333 | 0.7433 |

- **Trục k tăng đơn điệu ở CẢ HAI mô hình** ⇒ cơ chế thật, không phải nhiễu.
- **Trục N phẳng** (N=2/3/4 chênh nhau 1 câu) ⇒ đừng chọn kỹ, đừng tin chênh lệch nhỏ.
- **Ít ứng viên hơn KHÔNG tệ hơn**, dù trần top-3 (0.8933) thấp hơn hẳn top-10 (0.9633):
  lỗi của bộ chấm khi phải chọn giữa 10 văn bản lớn hơn phần trần nó mua được.
- **93% văn bản chạm trần k=10** ⇒ k=10 CHƯA đọc hết văn bản (kho trung vị ~16 đoạn).
  ⚠️ **SỬA 10/09: câu "k=20 còn đất" ĐÃ LẠC HẬU.** Bản chạy public đặt `N_DOC, K_CHUNK = 3, 50`
  (ô 1 `public_ft_run.ipynb`) — tức **đã đọc trọn văn bản** rồi. Trục k đã đóng, xem mục 10-09 cuối file.

FT tại N=3,k=10 so với sản xuất: **+3,67**, McNemar thắng 26 thua 15, **p=0.1173** — chưa đạt
ý nghĩa trên 300 câu, nhưng nhất quán và có cơ chế đỡ lưng.

### 🎯 CHỐT CHO PUBLIC: `N_DOC=3, K_CHUNK=20`
`public_ft_run.ipynb` đã đặt sẵn. ~55.000 cặp ≈ **1,7h GPU**. Ô 3 xuất 5 bài nộp từ cùng bộ điểm
(3×20, 2×20, 3×10, 2×10, 3×15) — 0 giây GPU thêm. **Mốc phải vượt: recall 0.6712 (= precision 0.702).**

### ⚙️ Ghi chú vận hành đã học
- `deepen_all` **không ghi đệm** — mọi vòng lặp GPU dài phải tự lưu theo lô.
- Kaggle: Accelerator để None ⇒ image CPU ⇒ `Torch not compiled with CUDA`. Đã thêm assert vào ô 1.
- T4 dư 10,3/14,56 GB với `gradient_checkpointing` + `GROUPS=1` — có thể nới nếu cần.
- Huấn luyện 1 epoch chỉ **45 phút**, không phải 3–4h như tôi ước. Thử biến thể là rẻ.

## 🔚 08/09 — **CỘNG RRF: ĐÓNG VĨNH VIỄN. ỨNG VIÊN CUỐI CÙNG ĐÃ CHẾT.**

`J_K50_max_plus_RRF_L03` (λ=0,3, khác bài chốt 141/1000 câu):
**precision 0.693 · recall 0.6618** so với bài chốt **0.702 / 0.6712** ⇒ **−0,9 điểm.**
Ngưỡng khoá trước khi nộp: *">0.6835 thì nhận · ≤0.6712 thì ĐÓNG"*. → **ĐÓNG.**

### Lần thứ hai tín hiệu dương trên dev không chuyển sang tập thi

| | dev300 | dev1000 | **LB thật** |
|---|---|---|---|
| cộng RRF | +1,3 … +2,3 (p=0.34–0.50) | +0,6 … +1,6 (p=0.109) | **−0,9** |

Dương ở cả hai tập dev, dương ở **mọi** λ, thắng>thua ở mọi λ — và vẫn âm trên tập thi.
**Đây là định nghĩa của nhiễu.** Ghi lại: "dương nhất quán nhưng p>0.05" KHÔNG phải bằng chứng yếu,
nó là **không có bằng chứng**. Đừng để bảng toàn dấu + đánh lừa lần nữa.

### 📕 MỌI GIẢ THUYẾT CÒN SỐNG ĐỀU ĐÃ ĐÓNG
13 hướng đo trong 07–08/09. **Đúng MỘT hướng ăn điểm: đọc đúng độ đo và nộp 1 id (+0,51).**
Hai hướng âm rõ (`replace` −3,1 · RRF −0,9 · năm mới −17). Mười hướng dưới sàn nhiễu.
Thứ duy nhất chưa thử: **bộ phân xử cặp**, hoà vốn ở **70,1%**, không có bằng chứng nào nói nó vượt được.

### 🎯 TRẠNG THÁI CHỐT
**precision 0.702 · hạng 3/84.** Cách CMTT (0.7060) **4 câu/1000** · cách GoGo (0.7210) 19 câu.
Hạn 18/09. Quota nộp còn ~100 lượt, GPU còn ~20h/tuần.

⚠️ **CẢNH BÁO CUỐI: có vòng Private Test riêng.** Còn ~100 lượt nộp là đủ để dò ra +0,4 điểm
trên public bằng may rủi — và đó chính xác là cách **mất hạng ở vòng private**. Sàn nhiễu LB
~1,45 điểm; khoảng cách tới hạng 2 là 0,4 điểm, tức **nằm gọn trong nhiễu**.
Dò LB để lấy 0,4 điểm là fit vào nhiễu, không phải cải tiến.

### ✅ VIỆC CÒN LẠI, THEO THỨ TỰ GIÁ TRỊ
1. **Nộp lại `probe_top1/A_K50_max_DANGNOP.zip`** — dòng công khai đang là 0.693, phải về 0.702.
2. **Gói tái lập** — BTC bắt buộc, hạn 18/09, **chưa ai đụng**, 0 giờ GPU. Giữ được hạng 3 mà
   BTC không chạy lại được thì hạng đó vô nghĩa. Cấu hình thắng hiện nằm rải rác trong nhiều
   notebook với đường dẫn Kaggle cứng — **không ai dựng lại được từ đầu tới cuối.**
3. Bộ phân xử cặp — chỉ nếu còn dư thời gian sau (2).

## 📊 08/09 — **dev1000 CHẾT Ở TẦNG 2. Nhưng tầng 1 sống sót và lật một kết luận.**

Phiên Kaggle vượt trần 12h ⇒ mất toàn bộ tầng 2 (`deepen_all` gom vào RAM, không ghi đệm).
Giữ được `tang1_scores_dev1000_fusion_M10_K50_matchEmbedded.json` — 1000 câu × 50 văn bản, `ce` + `rrf`.

### ⚠️ LỖI ƯỚC CHI PHÍ CỦA TÔI — ghi lại để không lặp

| | ước | thật |
|---|---|---|
| đoạn/văn bản tầng 2 (K=50) | 20,9 | **34,8** |
| tầng 2 M=10 | 209.000 đoạn | **348.234** |
| nhịp GPU | 12,9 đoạn/s | **9,35** |
| lượt A | ~6,6h | **~13,1h** |

Nguyên nhân: lấy phân bố độ dài trên **toàn kho** (trung vị 16) để ước, nhưng **văn bản được
truy hồi dài hơn hẳn** — dài thì nhiều cơ hội trùng câu hỏi nên dễ vào rổ. Đã nghĩ tới thiên
lệch này, ghi là "có thể đẩy ước lượng lên", rồi **không hiệu chỉnh**. Cộng nhịp chậm 27% ⇒ gấp đôi.
**Quy tắc mới: ước chi phí trên phân bố của VĂN BẢN ĐƯỢC TRUY HỒI, không phải toàn kho.**

### ✅ ① dev300 KHÔNG hề dễ hơn dev1000 — rút lại nhận định 07/09

| | dev300 | dev1000 |
|---|---|---|
| `base` (chỉ `ce`) top-1 | 0.6100 | **0.6110** |

**Lệch 0,10 điểm.** Nhận định "dev300 là mẫu dễ, lệch 3,16 điểm" hôm qua đo trên **recall@5 của
rổ**, không phải trên độ chính xác hạng 1. Ở đúng thước đang dùng, **hai tập tương đương.**
⇒ Mọi số dev300 trong file này đáng tin về mức tuyệt đối. dev1000 chỉ mua **độ phân giải**, không sửa thiên lệch.

### ❌ ② CỘNG RRF — KHÔNG ĐẠT NGƯỠNG ĐÃ KHOÁ (p<0.05 và Δ>+0,010)

λ = 0 → 0,8 trên 1000 câu, mức `ce`: Δ **+0,60 … +1,60**, **tất cả đều dương**, thắng > thua ở
mọi λ — nhưng p tốt nhất chỉ **0.109**. Không đạt.

⚠️ Nhưng đây là **phép thử THAY THẾ**: đo ở mức `ce`, còn bản chạy thật là `max(ce, ce_deep)`.
Phép thử thật chưa từng chạy vì tầng 2 chết. Chạy lại tầng 2 mất **~9,2h GPU** để có lẽ vẫn
không qua p<0.05 trên hiệu ứng ~1,5 điểm ⇒ **không đáng**.
Thay bằng **1 lượt nộp** trên LB — cùng cỡ 1000 câu, đúng cấu hình thật, 0 giờ GPU.
`Ketqua_E/probe_top1/J_K50_max_plus_RRF_L03.zip` (λ=0,3 — giá trị GIỮA, không phải đỉnh của
đường cong nào; khác bài đang nộp **141/1000 câu**).
**Ngưỡng: > 0.6835 recall thì nhận; ≤ 0.6712 thì ĐÓNG VĨNH VIỄN.**

### ✅ ③ NGƯỠNG HOÀ VỐN CỦA BỘ PHÂN XỬ CẶP — xác nhận trên 1000 câu
`70,1%` (dev300 cho 70,8%). Sai 389/1000 câu · gold hạng 2: 33% · hạng 2–3: 49%. Trần rổ 0.9870.
Con số này giờ chắc chắn. **Bộ phân xử phải đúng >70% trên đúng những cặp mà bộ chấm hiện tại
không phân biệt nổi** — chưa có bằng chứng nào nói nó làm được.

## 🔒 07/09 — **DANH SÁCH PHÉP ĐO CHO dev1000 ĐÃ KHOÁ.** Script: `dev1000_doc.py`

Viết TRƯỚC khi số về, để lúc đọc kết quả không có chỗ dò nhiều cấu hình rồi lấy cái đẹp nhất —
đúng cái bẫy đã làm hỏng con số 0.7467 hồi chiều. Chạy: `python dev1000_doc.py <file điểm>`.
Đã chạy khô bằng file dev300 đổi tên, ba mục ra đúng.

### ① Hiệu chuẩn cái cân — **mục quan trọng nhất, quan trọng hơn cả kết quả**
LB đã cho ta một sự thật cứng: `max` 0.702 vs `replace` 0.671 = **−3,10**.
dev1000 phải tái tạo được con số đó thì mới tin được.

| chênh `replace − max` trên dev1000 | kết luận |
|---|---|
| lệch < 1,5 điểm so với −3,10 | **dev1000 THAY được LB** ⇒ mọi thí nghiệm sau quyết trên dev1000, khỏi tốn lượt nộp |
| lệch > 1,5 điểm | dev1000 không thay được LB ⇒ vẫn phải nộp mới quyết được |

(dev300@K20 cho −2,00 — lệch 1,1 so với LB, ngay sát ngưỡng. dev1000@K50 nên sát hơn.)

### ② Cộng RRF — ứng viên dương yếu DUY NHẤT còn lại
Quét λ ∈ {0 … 0,5}. **NGƯỠNG ĐÃ KHOÁ: chỉ nhận λ nào đạt p<0.05 VÀ Δ>+0,010.**
Không đạt ⇒ **ĐÓNG, không nộp.** (dev300 cho +1,33…+2,33 nhưng p=0.34–0.50 = không đọc được.)

### ③ Cấu trúc lỗi — để quyết có làm bộ phân xử cặp không
In lại tỉ lệ gold ở hạng 2 / 2–3 và **ngưỡng hoà vốn** ở dải chênh < 0,005.
dev300 cho 70,8%. Nếu dev1000 cũng quanh đó thì cược này vẫn khó, cân nhắc bỏ.

### ⛔ KHÔNG thêm phép đo nào ngoài ba mục trên.
Muốn thêm thì phải ghi vào đây **trước** khi mở file điểm.

## 🪞 07/09 — BÀI HỌC QUY TRÌNH: **TÔI ĐÃ LÀM ĐÚNG LỖI MÀ QUY TẮC 7 CẢNH BÁO.**

Đề xuất `headview_run` (12 phút GPU) hoá ra **đã có sẵn kết luận trong file này**, ở hai chỗ:

- **Hướng đã đóng #11:** *"ghép tên văn bản — tiêu đề có dấu **+1,00** nhưng **83% trùng tầng 2**"*
- **Quy tắc 7:** *"**Đọc sâu, tiêu đề**, rổ tốt hơn, chấm lại: tất cả sửa **cùng một nhóm câu**…
  **Kiểm chồng lấn TRƯỚC khi cộng.**"*

Quy tắc 7 gọi đích danh hai thứ tôi đem so — "đọc sâu" (`ce_deep`) và "tiêu đề" (`ce_head`) —
và dự báo đúng kết quả. **Phải đọc danh sách đóng + 10 quy tắc TRƯỚC khi đề xuất bất kỳ thí
nghiệm nào.** Phần mới duy nhất: #11 đo trên recall@5 thấy trùng 83%; đo trên hạng 1 có đối
chứng thì phần dư **âm có ý nghĩa** (p<0.001) — bị bao trùm hoàn toàn, không phải chỉ thừa.

## ❌ 07/09 khuya — **GÓC NHÌN `head` ĐÃ CHẠY. TÍN HIỆU THẬT NHƯNG KHÔNG CHUYỂN ĐƯỢC. ĐÓNG.**

`headview_run.ipynb`, 300 câu × 5 văn bản × 2–3 đoạn × 2 nhánh, mốc dựng lại đúng 0.7100.

### Tín hiệu head ĐÃ NHÂN BẢN — nhưng chỉ khi đứng riêng

| đứng riêng (không có điểm cũ) | top-1 |
|---|---|
| `ce_head` (head + đoạn) | **0.6400** |
| `ce_plain` (chỉ đoạn) | 0.6033 |
| **chênh** | **+3,67** |

Khớp `enrich` 23/08 (+4,00). **Tín hiệu head là thật, đã xác nhận hai lần độc lập.**

### Nhưng ghép vào pipeline thì KHÔNG ĂN — thử ba phép kết hợp, hỏng cả ba

| phép | tốt nhất | McNemar |
|---|---|---|
| `max(ce, ce_deep, ce_head)` | 0.7133 (+0,33) | thắng 2 thua 1, **p=1.000** |
| đối chứng `max(…, ce_plain)` | 0.7100 (0) | 1–1, p=1.000 |
| cộng thẳng `+ λ·ce_head` | 0.7233 (+1,33) @λ=0,2–0,5 | 20–16, **p=0.618** |
| **tách riêng `+ λ·(ce_head − ce_plain)`** | **0.6533 → 0.5200** | 10–27 … 18–75, **p=0.0076 → 0.0000** |

**Phép cuối là kết quả sạch nhất và nó ÂM MẠNH.** Tách riêng phần "head đóng góp" rồi cộng vào
làm điểm tụt tới −19. ⇒ +3,67 kia **không phải** tín hiệu nhận diện văn bản. Nó chỉ là "cho
cross-encoder thêm ngữ cảnh để chấm đoạn" — mà `ce_deep` đã làm việc đó tốt hơn bằng cách đọc
nhiều đoạn hơn. **`ce_deep` bao trùm head.** Đóng hướng, đừng quay lại.

### 🧮 KIỂM KÊ 12 HƯỚNG NGÀY 07/09
✅ nộp 1 id **+0,51** (hạng 49 → **hạng 3/84**) · ❌ `replace` −3,1 (p rõ) · ❌ head (3 phép, p=1.0/0.62/0.000)
· ❌ ưu tiên năm mới (p=0.000) · ❌ model to hơn · K20↔K50 (14/1000) · max-pool đa pipeline (5/300)
· hoà z-score (p=0.49) · khớp tiêu đề (p=0.21) · cộng RRF (không nhân bản) · mở rộng M (+1,7)
· chọn đoạn (87,7% đã đọc hết)

**Một hướng ăn điểm. Hai hướng cho tín hiệu âm rõ ràng. Chín hướng dưới sàn nhiễu.**

### 🎯 ĐIỀU QUAN TRỌNG NHẤT RÚT RA: có BỐN ứng viên "dương yếu" mà dev300 không phân giải nổi

| hướng | Δ trên dev300 | p |
|---|---|---|
| cộng `λ·ce_head`, λ≈0,2–0,5 | **+1,33** | 0.618 |
| max-pool thêm `deep_M20_K20` | **+1,00** | 0.375 |
| khớp tiêu đề khi chênh < 0,15 | **+2,00** | 0.210 |
| cộng RRF λ≈0,15 | **+1,0…+1,7** | cùng dấu 3/3 file |

Cả bốn đều DƯƠNG, đều không đạt p<0.05, và đều nằm trong khoảng 1–2 điểm — **đúng vùng mù của
dev300**. Khoảng cách tới hạng 1 chỉ **1,9 điểm**.

⚠️ **RÚT LẠI 07/09 khuya — ĐÃ KIỂM CHỒNG LẤN, BỐN CẦN GẠT KHÔNG CỘNG ĐƯỢC.**

| | cứu | hỏng | NET |
|---|---|---|---|
| cộng `λ·ce_head` (λ=0,3) | 21 | 17 | **+4 câu** |
| cộng RRF (λ=0,15) | 5 | 2 | **+3 câu** |
| **gộp cả hai** | 23 | 19 | **+4 câu** |

Cộng dồn ngây thơ = **+2,33 điểm**. Gộp thật = **+1,33 điểm** — đúng bằng cần gạt tốt nhất đứng
một mình. Cái thứ hai đóng góp **0**. Câu được cứu chỉ trùng 13%, nhưng câu bị HỎNG thì không
bù trừ, nên NET không cộng. **Quy tắc 7 đúng lần thứ n.**

⇒ Kế hoạch "xếp chồng 2–3 cần gạt nhỏ để lấy 1,9 điểm" **SAI, đã rút.** Kể cả lấy nguyên ước
lượng dev300 (vốn đều p>0.2, tức đều có thể là nhiễu) thì chúng vẫn không cộng.

⇒ Trần thực tế của kiến trúc hiện tại trên độ đo này là khoảng **0,71–0,72**. Vượt GoGo (0,7210)
gần như chắc chắn **cần một thứ khác về bản chất**, không phải tinh chỉnh.
`fusion_dev1000` (đang chạy) hạ sàn nhiễu ~1,8 lần — đó chính xác là thứ biến bốn ứng viên này
từ "không biết" thành "biết". **Chạy xong dev1000, việc đầu tiên là đo lại đúng bốn dòng trên.**

## 🟩🟩 07/09 — **`enrich` KHÔNG HỎNG. NHÓM ĐÃ ĐỌC SAI KẾT QUẢ CỦA CHÍNH MÌNH.**

Kết luận cũ: *"nhồi thêm chữ vào đoạn làm GIẢM chất lượng"* — rút ra vì cả ba nhánh (0.5533 /
0.5133 / 0.5000) đều thấp hơn mốc sản xuất 0.6100. **Nhưng ba nhánh đó dùng `pick_chunks(k=1)`
— MỘT đoạn duy nhất**, còn bản sản xuất dùng 3 đoạn của D. So với mốc sản xuất là so nhầm.

So sánh ĐÚNG là giữa ba nhánh với nhau: cùng 300 câu, cùng ứng viên, cùng model,
**chỉ khác duy nhất văn bản đầu vào.**

| so sánh | top-1 | Δ | McNemar |
|---|---|---|---|
| `front` vs `plain` (có phần đầu văn bản vs không) | 0.5533 vs 0.5133 | **+4,00** | 27–15, p=0.088 |
| **`front` vs `back` (phần đầu ĐẶT TRƯỚC vs đặt sau)** | 0.5533 vs 0.5000 | **+5,33** | 29–13, **p=0.0195** |
| `plain` vs `back` | 0.5133 vs 0.5000 | +1,33 | 12–8, p=0.503 |

**`front` vs `back` là bằng chứng sạch nhất:** cùng y hệt lượng chữ, chỉ khác VỊ TRÍ, chênh 5,33
điểm, p<0.05. Không phải "nhiều chữ hơn thì tốt hơn" — `back` có đúng bằng đó chữ và không ăn gì.
Là **phần đầu văn bản, đặt trước, mang thông tin thật.**

### Vì sao khớp với kiểu lỗi đã quan sát
Ca [117094]: hỏi *Tập đoàn **Dầu khí***, hệ thống chọn nghị định về Tập đoàn **Điện lực**.
Ca [20110]: hỏi *Quỹ Phát triển vì cộng đồng*, gold có đúng cụm đó ở tiêu đề.
**Phần đầu văn bản chứa tên/phạm vi điều chỉnh — thứ phân biệt hai văn bản gần giống nhau.**

### Vì sao tín hiệu này CHƯA có trong pipeline
`ce` chấm 3 đoạn của D · `ce_deep` chấm K đoạn do `pick_chunks` chọn **theo BM25 với câu hỏi**.
Phần mở đầu văn bản trùng từ với câu hỏi rất ít ⇒ **gần như không bao giờ được chọn.**
Cả hai góc nhìn hiện có đều mù với tiêu đề.

### 🎯 VIỆC TIẾP THEO: thêm góc nhìn `head + SEP + đoạn`, max-pool cùng `ce`/`ce_deep`
- 0 tham số mới (vẫn `AITeamVN/Vietnamese_Reranker` 0,568B) ⇒ **không đụng ngân sách 4B**
- chỉ cần top-5 văn bản × 1000 câu = **5.000 cặp ≈ 7 phút GPU**
- đúng cơ chế "nhiều góc nhìn, lấy max" đã xác nhận HAI lần (dev300 +10, public LB +3,1)

**Ngưỡng đặt trước:** mốc dev300 `max(ce,ce_deep)` = 0.7100.
≥ 0.73 → dựng bài public, nộp · 0.715–0.73 → nộp thăm dò LB cho chắc · < 0.715 → đóng hướng.

### 📐 Dư địa thật của việc lật hạng 1↔2 (dev300)
41/300 câu có gold ở hạng 2 (**13,7 điểm** nếu lật hết). Chênh điểm hạng1−hạng2:
trung vị **0.0108** ở nhóm này so với **0.1175** ở nhóm đang đúng — tách nhau 10 lần.
Nhưng ở dải chênh < 0.005 có 46 câu đang ĐÚNG và 19 câu cứu được ⇒ **bộ phân xử phải đúng
> 70,8% mới hoà vốn.** Thực tế ăn được 1–3 điểm, không phải 13,7.

## ✅ 07/09 — **PHÉP ĐO SẠCH ĐẦU TIÊN CỦA CẢ PHIÊN: `max` THẮNG `replace` 3,1 ĐIỂM.**

Nộp thật, `B_K50_replace` (id riêng): **precision 0.671 · recall 0.6402**
so với bài đang nộp `A_K50_max`: **precision 0.702 · recall 0.6712**.

**Δ = −3,1 điểm precision trên 133 câu bất đồng.** Sàn nhiễu LB ở n=1000 là ~1,45 điểm ⇒ đây là
kết quả **có ý nghĩa**, không phải nhiễu. Cả phiên 07/09 thử ~10 hướng, đây là hướng duy nhất
cho tín hiệu rõ ràng — và nó là tín hiệu ÂM, đóng một hướng.

### Ý nghĩa: KHÔNG chỉ đóng hướng, mà XÁC NHẬN CƠ CHẾ

Giả thuyết là ở K=50 tầng sâu đã đọc gần trọn văn bản nên `max` chỉ còn pha loãng nó. **Sai.**
Điểm nông `ce` mang thông tin ĐỘC LẬP mà điểm sâu không có. Max-pool hai góc nhìn thắng cả hai
góc nhìn đơn lẻ, ở cả K=20 (dev300: 0.71 vs 0.69) lẫn K=50 (public: 0.702 vs 0.671) —
và **khoảng cách RỘNG RA khi K tăng**, ngược hẳn dự đoán.

⇒ "nhiều góc nhìn, lấy max" là cơ chế thật duy nhất đã được xác nhận HAI LẦN. Giữ `max`. Đóng `replace`.

### ⛔ Nhưng thêm góc nhìn NỮA thì hết đất — đã đo, đừng nộp

Max-pool thêm hai pipeline khác hẳn (`deep_M20_K20`, `bm25pick_merge1800`) trên dev300:

| tổ hợp | top-1 | Δ | McNemar |
|---|---|---|---|
| F: `ce`,`ce_deep` (đang nộp) | 0.7100 | — | — |
| F + deep | 0.7200 | +0,0100 | thắng 4 thua 1, **p=0.375** |
| F + bm25merge | 0.7100 | 0 | **0 câu đổi** |
| F + deep + bm25merge (6 góc nhìn) | 0.7200 | +0,0100 | thắng 4 thua 1, p=0.375 |

Chỉ **5/300 câu** đổi kết quả ⇒ quy ra 1000 câu là ~17 câu = tối đa 1,7 điểm, **dưới sàn nhiễu LB**.
Nộp cũng không đọc được gì. **Không nộp.**

Ghi chú kỹ thuật kiểm được: `ce` **giống hệt** giữa lượt K=20 và K=50 (50.000/50.000 cặp — tầng 1
tái dùng đúng như thiết kế). `ce_deep@K50 ≥ ce_deep@K20` ở 19.517/20.000 cặp ⇒ gộp hai K vô nghĩa.

### 📕 KHÔNG GIAN 0-GPU ĐÃ CẠN. Mười một hướng đã đo trong ngày 07/09:
nộp 1 id ✅(+0,51) · `replace` ❌(−3,1) · K20↔K50 (14/1000) · max-pool đa pipeline (5/300) ·
model to hơn ❌ · hoà z-score (p=0.49) · ưu tiên năm mới ❌(p=0.000) · khớp tiêu đề (p=0.21) ·
cộng RRF (không nhân bản) · mở rộng M (+1,7) · chọn đoạn (87,7% văn bản đã đọc hết).

**Chỉ còn một hướng chưa thử: BỘ PHÂN XỬ CẶP.** Không còn gì để thăm dò bằng CPU nữa.

### 🔁 VIỆC NGAY: nộp lại `probe_top1/A_K50_max_DANGNOP.zip`
Bảng hiển thị bài mới nhất ⇒ dòng công khai đang là 0.671. Nộp lại A để về 0.702.

## ⚙️ 07/09 — CƠ CHẾ CODABENCH (soi trực tiếp, đã đăng nhập)

- **Quota: 10 bài/ngày** (đã dùng 1/10). Tổng 35/10000. Rộng rãi, cứ thăm dò.
- **Bảng xếp hạng hiển thị bài NỘP MỚI NHẤT, không phải bài tốt nhất.** Bằng chứng: dòng của
  nhóm đang là 0.6712 (bài top-1, 07/09 20:14) trong khi bài recall cao nhất là 0.9124.
  ⇒ **Nộp bài thăm dò sẽ THAY dòng hiện tại.** Kết thúc mỗi buổi phải nộp lại cấu hình tốt nhất.
- Cột **Score** trong *My Submissions* là **RECALL**, không phải precision. Với bài nộp 1 id thì
  precision = recall / 0,9558 (tỉ số cố định do 1,047 gold/câu) ⇒ **so recall giữa hai bài 1-id
  là tương đương so precision.** Mốc hiện tại: **recall 0.6712 = precision 0.702**.
- Pha hiện tại kết thúc **18/09/2026 23:59 GMT+7**. Có pha **Private Test** riêng.

⚠️ **Trình duyệt của Claude không tải file lên được** (không có công cụ chọn file). Mọi bài nộp
phải do người bấm nút "Submission upload". Claude dựng file, người nộp.

## 🟡 07/09 — **LỆCH K=20 vs K=50 CHỈ ĐỔI 14/1000 CÂU. Lo lắng trước đó đã gỡ.**

Dựng bài top-1 từ cả hai file điểm public rồi so trực tiếp:

| bài top-1 dựng từ | khác bài đang nộp |
|---|---|
| `fusion_M20_K50_matchEmbedded` `max` (= bài đang nộp) | 0/1000 ← guard khớp |
| **`fusion_M20_K20_matchEmbedded` `max`** | **14/1000** |
| `fusion_M10_K20` `max` | 43/1000 |
| `fusion_M20_K20` (rổ cũ) | 59/1000 |
| `bm25merge_M20_K20` | 82/1000 |
| `fusion_M20_K50` **`replace`** | **133/1000** |
| `fusion_M20_K20` `replace` | 145/1000 |
| `deep_M20_K20` `max` | 165/1000 |
| `fusion_M20_K50` `base` | 217/1000 |

**K=20 và K=50 chọn CÙNG một văn bản ở 986/1000 câu.** Hệ quả:
1. Mốc dev300 **0.7100 (K=20)** và public **0.702 (K=50)** **so được với nhau** — cảnh báo lệch
   cấu hình viết trước đó là quá lo. K ảnh hưởng tối đa 1,4 điểm.
2. **Chạy dev1000 ở K=20 thay vì K=50: 8,2h thay vì 11,1h, VỪA MỘT PHIÊN Kaggle** thay vì hai
   phiên phải tải xuống/tải lên giữa chừng. Đổi lấy sai lệch ≤1,4% số câu. **Nên đổi.**

### 📊 Bộ thăm dò 0 GPU: `Ketqua_E/probe_top1/` — 9 bài nộp đã dựng sẵn
Số câu khác nhau = trần thông tin của phép thử. Bài chỉ khác 14 câu thì không đo được gì
(nhiễu LB ~1,45 điểm ở n=1000). **Chỉ nộp bài khác ≥100 câu.**

Ứng viên đáng nộp, xếp theo giá trị:
- **`B_K50_replace`** (khác 133) — dev300@K20 nói `replace` thua `max` (0.69 vs 0.71), nhưng ở
  K=50 tầng sâu đọc ~21 đoạn/văn bản thay vì ~14, nên `max` có thể đang **pha loãng** điểm sâu
  bằng điểm nông. **Chưa ai biết. Đây là phép thử có giá trị nhất.**
- `G_deep_M20K20_max` (165) — rổ khác hẳn; dev300 dự báo thua (0.6867)
- `H_bm25merge_M20` (82) — dev300 dự báo suýt soát (0.7067)

⛔ **KHÔNG nộp cả 9 bài rồi lấy max.** n=1000 cho sai số ~1,45 điểm; dò 9 lần lấy đỉnh là
overfit public LB, mà **vòng chấm cuối là private test**. Nộp tối đa 2–3 bài đã đặt giả thuyết trước.

## ❌ 07/09 cuối ngày — **HUỶ VIỆC CHỌN ĐOẠN CỦA D. LANE CỦA D ĐÃ CẠN.**

Tôi đề xuất việc "chọn đoạn" cho D rồi **tự bác bỏ nó sau khi đọc kỹ `deep_chunk.py`**. Ghi lại
đầy đủ để không ai đề xuất lại.

### Vì sao sai: tầng chấm sâu ĐÃ đọc lại văn bản gốc rồi

`deepen_one()` gọi `pick_chunks(question, ctx_dir, doc_id, k)` — nó **đọc thẳng từ `ctx_dir`**,
tự băm lại, **không dùng 3 đoạn trong rổ của D**. Và trong `pick_chunks`:

```python
if len(parts) <= k:
    return list(parts)        # văn bản ít hơn K đoạn -> chấm HẾT, không chọn lọc gì
```

### Đếm thật trên kho (3.000 văn bản, `MERGE_CHARS=1800`)

số đoạn/văn bản: **trung vị 16** · trung bình 26,3 · p90 = 59 · p99 = 177 · max 559

| | văn bản đã được chấm HẾT đoạn | bị cắt bớt |
|---|---|---|
| **K=20** (file điểm dev300) | 61,4% | 38,6% |
| **K=50** (bài đang nộp) | **87,7%** | **12,3%** |

→ Ở cấu hình đang nộp, **87,7% văn bản đã được đọc trọn vẹn.** "Chọn đoạn thông minh" chỉ có đất
ở 12,3% còn lại ⇒ trần thực tế 1–2 điểm, **dưới sàn nhiễu của dev300.** Huỷ.

`chondoan_tran_run_HUY_xem_CLAUDE_07-09.ipynb` — giữ lại làm bằng chứng, **đừng chạy.**

### ⚠️ LỆCH CẤU HÌNH VỪA PHÁT HIỆN — ảnh hưởng MỌI số đo ngày 07/09

| | K | nguồn |
|---|---|---|
| mọi thí nghiệm dev300 hôm nay (mốc 0.7100) | **K=20** | `scores_dev300_fusion_M20_K20.json` |
| bài đã nộp (precision 0.702) | **K=50** | `scores_public_fusion_M20_K50_matchEmbedded.json` |

**Chưa từng có file điểm dev300 ở K=50.** Hai con số 0.7100 và 0.702 không cùng cấu hình —
trùng nhau có phần là may. Lượt GPU tới phải sinh dev1000 ở **đúng K=50**.

### 📉 TỔNG KẾT LANE CỦA D: HẾT VIỆC

| việc | trần còn lại |
|---|---|
| thêm văn bản vào rổ (recall@50) | +1,7 |
| mở rộng M | +1,7 |
| chọn đoạn / đọc sâu hơn | +1–2 (chỉ 12,3% văn bản bị cắt) |
| thứ tự trong rổ | 0 — CE xếp lại hết |

Cả bốn đều dưới sàn nhiễu và **không cái nào cộng dồn được** (quy tắc 7).

### ✅ VIỆC MỚI CHO D: **CHẠY `fusion_dev1000_run.ipynb` Ở K=50**
Không phải việc phụ — đây là thứ đang chặn toàn bộ phần còn lại của dự án. Là việc tính toán
thuần, uỷ quyền được, và D có GPU rảnh. Toàn bộ GPU còn lại sau đó dồn cho **bộ phân xử cặp** của E.

## 🔵 07/09 — **VIỆC CỦA D ĐỔI LẦN THỨ HAI. KHÔNG CÒN LÀ LẤY VĂN BẢN, MÀ LÀ CHỌN ĐOẠN.**

### Ba việc cũ của D đều đã cạn hoặc đã chết

| việc cũ của D | trạng thái đo được |
|---|---|
| đưa thêm văn bản vào rổ (recall@50) | 0.9832 trên dev1000 → **còn tối đa +1,7**, gần cạn |
| **thứ tự trong rổ** (RRF) | **CHẾT.** CE xếp lại toàn bộ; RRF top-1 = 0.5933 vs CE 0.7100. Cộng RRF vào CE không nhân bản (p = 0.337/1.000/1.000) |
| mở rộng M cho tầng sâu | gold đã nằm trong top-M ở 290/295 câu → **+1,7** |

### Việc mới, và là hiệu ứng LỚN NHẤT đo được cả phiên

```
kho:  296.070 đoạn / 8.532 văn bản = 34,7 đoạn mỗi văn bản
rổ D bàn giao cho E:  tối đa 3 đoạn/văn bản  (top_chunks, d3/d4)
=> tầng chấm NÔNG chỉ đọc 9% mỗi văn bản
```

`ce` (đọc ~3 đoạn) = **0.6100** → `ce_deep` (đọc nhiều hơn) = **0.6900**. **+8 điểm chỉ vì cho
bộ chấm đọc nhiều hơn.** Đây là hiệu ứng duy nhất trong 8 hướng thử ngày 07/09 vượt hẳn sàn nhiễu.

→ **D không quyết định văn bản nào vào rổ nữa. D quyết định bộ chấm được ĐỌC GÌ.**
Chọn sai 3 đoạn trong 35 đoạn ⇒ E chấm văn bản đúng bằng bằng chứng sai, và không có cách nào cứu.

Đây đúng là việc **D4** mà lưu trữ nhắc đi nhắc lại từ 17/08 ("bi-encoder mức đoạn, chọn đúng 20
đoạn trong 125"), bị đẩy qua đẩy lại giữa D và E rồi **chưa ai làm**.

### ⚠️ VIỆC ĐẦU TIÊN CỦA D LÀ ĐO TRẦN, KHÔNG PHẢI XÂY (quy tắc 9)

Chấm **TẤT CẢ ~35 đoạn** của top-5 văn bản trên dev300, max-pool theo văn bản, xếp lại, đo đúng
ở hạng 1. Đó là trần của việc chọn đoạn hoàn hảo. Chi phí ~5×35 = 175 đoạn/câu × 300 câu.

| trần đo được | kết luận |
|---|---|
| **≥ 0,80** | chọn đoạn là cần gạt lớn nhất còn lại → D làm tiếp, ưu tiên số 1 |
| **0,74 – 0,79** | có thật nhưng vừa phải → làm sau bộ phân xử cặp |
| **≤ 0,73** | chọn đoạn đã cạn → **D dừng**, dồn toàn bộ GPU cho E |

**Notebook đã soạn sẵn: `chondoan_tran_run.ipynb`** (4 ô, tái dùng `rerank.load_reranker` +
`make_candidates_fallback.chunks_of/read_passage`, không chép code). Có guard dựng lại mốc 0.7100
trước khi đọc bất kỳ Δ nào, lưu dần theo lô 50 câu, chạy lại là nối tiếp.
`chondoan_dryrun.py` chạy khô trên CPU bằng model giả — đã xác nhận logic đo đúng ở cả hai cực
(model giả trung tính ra đúng 0.7100, model giả hoàn hảo ra đúng trần 0.9333).

Không được bỏ qua bước này. Ngày 07/09 đã có 3 giả thuyết nhìn rất thuyết phục chết khi đem đo.

### Ghi chú: `enrich` (thêm ngữ cảnh vào đoạn) ĐÃ THỬ VÀ HỎNG
`enrich_front` ce = 0.5533 · `enrich_plain` 0.5133 · `enrich_back` 0.5000, so với `fusion` ce = 0.6100.
Nhồi thêm chữ vào đoạn làm **giảm** chất lượng. Việc của D là chọn ĐÚNG đoạn, không phải nhồi thêm.

## 🧭 07/09 khuya — GIẢI PHẪU 82 CÂU SAI. **BÀI TOÁN LÀ PHÂN BIỆT HẠNG 1 vs HẠNG 2.**

### Cấu trúc lỗi (dev300, mốc `max(ce,ce_deep)` = 0.7100 → 82 câu sai)

| gold thực sự nằm ở hạng | số câu | % số câu sai |
|---|---|---|
| **2** | **41** | **50,0%** |
| 3 | 14 | 17,1% |
| 4–5 | 12 | 14,6% |
| 6–10 | 9 | 11,0% |
| 11–50 | 6 | 7,3% |

**67% số câu sai có gold ở hạng 2–3.** Đây KHÔNG phải bài toán truy hồi, cũng không phải bài
toán xếp hạng 50 văn bản. Đây là bài toán **phân biệt hai văn bản gần giống nhau**.
Phân biệt hoàn hảo hạng 1 vs 2 = **+13,7 điểm** (0.702 → ~0.84).

### Độ tin cậy phân tách rất mạnh — dùng được để lọc câu cần can thiệp

| nhóm theo chênh điểm hạng1−hạng2 | tỉ lệ đúng |
|---|---|
| 1/5 (chênh 0.000–0.002) | 0.600 |
| 2/5 (0.002–0.021) | 0.600 |
| 3/5 (0.021–0.126) | 0.617 |
| 4/5 (0.127–0.504) | 0.817 |
| 5/5 (0.509–0.986) | **0.917** |

→ 60% số câu có chênh nhỏ và chỉ đúng ~0.61. **Chỉ cần can thiệp vào 60% đó, và chỉ vào 2–3 ứng
viên đầu** ⇒ rẻ hơn lượt chấm hiện tại (50 văn bản × 1000 câu) khoảng **28 lần**.

### ⛔ BỐN HƯỚNG NỮA ĐO XONG, BÁC BỎ (07/09) — đừng đào lại

| hướng | kết quả | McNemar |
|---|---|---|
| **mở rộng M** (chấm sâu nhiều văn bản hơn) | gold đã nằm trong top-M ở **290/295** câu → trần chỉ **+1,7** | — |
| **ưu tiên văn bản năm mới hơn** | **−0,1700** (0.7100 → 0.5400) | thắng 19 **thua 70**, p=0.000 |
| **khớp tiêu đề với câu hỏi** (chỉ khi chênh < 0.15) | +0,0200 | thắng 11 thua 5, **p=0.210** |
| **cộng RRF vào CE** | λ tối ưu không nhân bản giữa 3 file | p = 0.337 / 1.000 / 1.000 |

Ghi chú: đọc tay 10 ca sai gợi ra 2 giả thuyết (lỗi tiêu đề, lỗi cũ/mới). **Đo xong cả hai đều
chết.** Đọc ví dụ để sinh giả thuyết thì được, để kết luận thì không.

### 🚧 SÀN NHIỄU: mọi cần gạt còn lại đáng 1–2 điểm, dev300 phân giải ~1,5–2,6 điểm.
Trong lượt làm việc 07/09 đã thử **8 hướng**, không hướng nào đạt p < 0.05. **Không phải hết ý
tưởng — là hết khả năng đo.** Chạy `fusion_dev1000_run.ipynb` là việc chặn tất cả.

### 💡 Ý TƯỞNG KIẾN TRÚC MỚI: **BỘ PHÂN XỬ CẶP (pairwise judge)**

CE hiện tại chấm từng cặp (câu hỏi, văn bản) **độc lập** — nó chưa bao giờ nhìn hai ứng viên
cạnh nhau. Đưa cả hai vào cùng một lượt: *"câu hỏi này, A hay B trả lời đúng?"* là **phép tính
khác hẳn**, và là việc LLM mạnh nhất.

Lưu ý phân biệt với kết quả âm "model to không giỏi hơn": phép thử đó cho model to làm đúng
việc của CE — **chấm điểm độc lập** rồi xếp hạng 5 ứng viên. Chưa ai thử nó ở vai **so sánh cặp**.
Đây là giả thuyết, chưa phải kết luận.

- áp dụng cho ~60% câu chênh điểm thấp × 2–3 ứng viên ⇒ rẻ hơn ~28 lần lượt hiện tại
- ngân sách tham số: 4B trần − (bi-encoder 0,568B + CE 0,568B) = **còn ~2,8B chưa dùng**
- trần của hướng: +13,7 điểm nếu phân xử hoàn hảo hạng 1 vs 2

### 📊 VỊ TRÍ THỰC (bảng 07/09, xếp theo Precision)
**Hạng 3/84.** GoGo 0.7210 · CMTT 0.7060 · **mình 0.7020** · kế tiếp 0.5152.
Cách hạng 2 đúng **4 câu/1000**, cách hạng 1 **19 câu/1000**. Ba đội đầu đều nộp 1 id (P/R = 0,95).
GoGo chốt bài từ **10/08** và đứng yên 4 tuần.

## 🟩 07/09 tối — **XÁC NHẬN: PRECISION = 0.702. ĐỘ ĐO CHIA CHO SỐ ID THỰC NỘP.**

Bài `submission_matchEmb_K50_TOP1.zip` (1 id/câu): **Recall 0.6712 · Precision 0.702**, ID 917878.
Ngưỡng đặt trước là 0.60–0.70 → trúng. dev300 dự báo 0.7100, thực tế 0.702, **lệch 0.8 điểm**.

> **dev300 là proxy TỐT cho precision@1** (lệch −0,8), khác hẳn với recall@5 (lệch −3,4).

**Trên cột Precision nhóm đang đứng #1 toàn giải:** 0.702 · UIT-Reik 0.4764 · phần còn lại ~0.2486.

### ⚖️ SỐ ID NỘP: **LUÔN LUÔN 1.** Đã chứng minh, đóng vĩnh viễn.
`precision@m` trên dev300: m=1 → **0.7100** · m=2 → 0.4300 · m=3 → 0.3056 · m=5 → 0.1933.
Toán học: nộp thêm id thứ m+1 chỉ tăng precision nếu p(m+1) > trung bình hiện tại — không bao
giờ đúng với danh sách đã sắp. **Mọi cần gạt `n`/`blend` chết theo.**

### 🎯 CẤU TRÚC DƯ ĐỊA MỚI (dev300, thước = đúng ở hạng 1)

| mốc | điểm | ghi chú |
|---|---|---|
| đang có: `max(ce, ce_deep)` | **0.7100** | = bài vừa nộp |
| trần nếu CE thu hẹp còn 3 ứng viên | 0.8933 | |
| trần nếu CE thu hẹp còn 5 ứng viên | 0.9333 | |
| trần nếu chọn đúng nhất trong 5 bộ chấm đã có | 0.8000 | |
| **trần của rổ (50 ứng viên)** | **0.9833** | còn **27,3 điểm** |

**Toàn bộ dư địa nằm ở khâu CHỌN, không ở khâu lấy rổ.** Rổ đã chứa đáp án 98,3% số câu.

### ⛔ BỐN HƯỚNG ĐÃ ĐO VÀ BÁC BỎ BẰNG DỮ LIỆU CỦA CHÍNH NHÓM (07/09)

| hướng | bằng chứng | kết luận |
|---|---|---|
| **model to hơn** | 15 câu khó, đúng ở **hạng 1**: CE 0.568B = **5/15** · Qwen3-rr-4B 4/15 · **Qwen3-rr-8B 4/15** · Qwen2.5-7B 1/15 | quy mô mua RECALL (8B top-5 = 10/15 vs CE 6/15) **chứ không mua PRECISION**. Bỏ |
| **hoà nhiều bộ chấm** | z-score 5 bộ tốt nhất → 0.7267 (+1,67) nhưng **McNemar 19–14, p≈0.49**; đã dò 26 tổ hợp lấy max | dưới sàn nhiễu. Bỏ |
| **fine-tune kiểu cũ** | `ftv2_deep_M20_K20` max = **0.6233** vs bản gốc `deep_M20_K20` max = **0.6867** | hỏng ở cả thước mới. Cần 3 chỗ sửa 19/08, không phải chạy lại |
| **cộng RRF vào điểm CE** | λ tối ưu: file A 0.8–1.3 · file B 0.2 · file C 0.2. **Không nhân bản.** McNemar p = 0.337 / 1.000 / 1.000 | chỉ λ≈0.15 là cùng dấu ở cả 3 file (+1,0…+1,7). Dưới sàn nhiễu, chờ dev1000 |

### 🔬 HIỆU ỨNG DUY NHẤT ĐỦ LỚN ĐỂ TIN: **NHIỀU GÓC NHÌN / VĂN BẢN, LẤY MAX**

`ce` = 0.6100 → `ce_deep` = 0.6900 → **`max(ce, ce_deep)` = 0.7100**. Và `M10` → `M20`: 0.6767 → 0.6867.
Cho bộ chấm nhìn nhiều phần văn bản hơn rồi max-pool là thứ **+10 điểm** đã thấy rõ.
→ Hướng rẻ và chắc nhất: tăng M (30/40) và thêm kiểu góc nhìn mới (tiêu đề+đoạn, đoạn đầu…), max hết.

### 🚧 NÚT CHẶN: **dev300 HẾT ĐỘ PHÂN GIẢI. GPU ĐẦU TIÊN PHẢI TIÊU CHO CÁI CÂN, KHÔNG PHẢI CHO Ý TƯỞNG.**

Mọi cần gạt còn lại đáng 1–2 điểm; sai số ghép cặp của dev300 ~1,5 điểm. **Không đo được.**
Đó chính xác là cái bẫy đã nuốt cả tháng 8. `fusion_dev1000_run.ipynb` **đã viết sẵn** — chạy nó
lấy điểm CE cho dev1000 (~3,3 lần lượt dev300) là việc GPU số 1, trước mọi ý tưởng khác.

### 📋 THỨ TỰ VIỆC CHỐT
1. **CE trên dev1000** — dựng lại cái cân. Chặn mọi thứ phía sau.
2. **λ≈0.15 cộng RRF** — CPU, 0 GPU, xác nhận trên dev1000 rồi nộp.
3. **Tăng M + thêm góc nhìn, max-pool** — cơ chế đã chứng minh +10 điểm.
4. **Fine-tune LISTWISE** (softmax trên 50 ứng viên = tối ưu thẳng P(hạng 1 đúng)), nhãn dương do
   CE chọn, negative bán khó hạng 10–50. Thứ duy nhất có cửa chạm 0.80+. 6000 câu train sạch.

### ⏳ Lợi thế này có hạn dùng
82/83 đội đang nộp 5 id (precision ~0.20). `UIT-Reik` đã nộp ~2 id (0.4764) — có đội đang mò ra.
Ngày nào còn một mình biết, ngày đó còn cách biệt 0,23. **Chốt cải tiến sớm.**

## 🔴🔴 07/09 — MÂU THUẪN ĐỘ ĐO. **CHƯA GIẢI QUYẾT. ĐỌC TRƯỚC KHI NỘP BẤT KỲ BÀI NÀO.**

**Ba nguồn, hai câu trả lời trái ngược nhau:**

| nguồn | ngày | nói gì |
|---|---|---|
| **Email BTC** (`dsc@uit.edu.vn`) | **02/08** | *"**Precision là độ đo chính** và Recall là độ đo được sử dụng trong trường hợp các nhóm có điểm Precision bằng nhau."* |
| `Input/DSC2026_Task1_LegalIR_Data_Overview.docx` (tải về **07/08**, tức SAU email) | 07/08 | *"Điểm xếp hạng sử dụng **Recall làm độ đo chính** và Precision làm độ đo phụ."* |
| **Bảng xếp hạng Codabench** (soi trực tiếp 07/09) | nay | **sắp xếp theo Recall giảm dần.** Precision là cột 2, không ảnh hưởng thứ hạng |

**Bằng chứng thực nghiệm nghiêng hẳn về RECALL:**
- LB sắp đúng theo Recall: 0,9591 → 0,9556 → 0,9548 → … → 0,8990.
- **`UIT-Reik`: Recall 0,9091 · Precision 0,4764 → xếp hạng 42.** Đội này nộp ít id (precision gấp 2,4 lần mọi đội) mà vẫn bị xếp theo recall. **Đây là bằng chứng mạnh nhất.**
- 82/83 đội có precision ≈ 0,20 = ai cũng nộp đủ 5 id. Nếu precision là chính thì LB đã đầy bài nộp 1 id với precision 0,6+.

### ✅ QUYẾT ĐỊNH 07/09 (Khim): **LẤY EMAIL BTC 02/08 LÀM CHUẨN. ALL-IN PRECISION.**

Nộp `submission_matchEmb_K50_TOP1.zip` để đọc precision thật từ bộ chấm. Đây đồng thời là
**thí nghiệm phân biệt** cho câu hỏi công thức, ngưỡng đặt TRƯỚC khi nộp (quy tắc 9):

| bộ chấm chia cho | precision dự kiến trả về | kết luận |
|---|---|---|
| `len(predicted)` — số id thực nộp | **≈ 0,60 – 0,70** | công thức đúng như `metrics.py` → hướng precision sống, giữ 1 id |
| `5` cố định | **≈ 0,12 – 0,14** | nộp ít id KHÔNG tăng precision → quay lại 5 id ngay |

Recall của bài này sẽ tụt về ~0,69. **Đó là dự kiến, không phải lỗi.**

⚠️ Rủi ro đã ghi nhận và chấp nhận: bảng xếp hạng Codabench đang sắp theo Recall, và
`UIT-Reik` (precision 0,4764) vẫn nằm hạng 42. Vẫn nên email BTC hỏi cho dứt điểm. Nếu LB thật sự chấm theo recall,
nộp 1 id kéo recall 0,9124 → ~0,69 = **rơi xuống cuối bảng**.

✅ **VIỆC PHẢI LÀM HÔM NAY:** email thẳng `dsc@uit.edu.vn` hỏi một câu — *"độ đo xếp hạng chính
thức của Task 1 là Precision (theo email 02/08) hay Recall (theo tài liệu mô tả và bảng xếp hạng
Codabench)?"* Trưởng nhóm không đọc mail → **Khim tự gửi.**

### 📦 Đã dựng sẵn, chờ câu trả lời: `Ketqua_E/submission_TOP1_KHOAN_NOP_chua_xac_minh_dodo.zip`

1000 câu, mỗi câu **đúng 1 id**, lấy `argmax max(ce, ce_deep)` từ `scores_public_fusion_M20_K50_matchEmbedded.json`.
Guard trap ⑧ đã chạy: dựng lại bài `n=2` khớp **1000/1000** trước khi đọc bất kỳ số nào.
Khác bài `n=2` ở slot 1 tại **439/1000** câu.
→ Nếu BTC trả lời "Precision": nộp file này, điểm chính nhảy **0,196 → ~0,70**, từ hạng ~40 lên hạng 1.
→ Nếu BTC trả lời "Recall": **xoá file, quên hướng này đi.**

### 🔑 NHƯNG CÓ MỘT KẾT QUẢ SỐNG BẤT KỂ CÂU TRẢ LỜI LÀ GÌ

Đo trên `scores_dev300_fusion_M20_K20.json`, độ chính xác **hạng 1**:

| bộ xếp hạng | đúng ở hạng 1 |
|---|---|
| rổ RRF (thứ tự của D) | 0,5933 |
| CE `ce` | 0,6100 |
| **CE `max(ce, ce_deep)`** | **0,7100** ← hơn rổ **+11,67 điểm** |

**Cross-encoder KHÔNG vô dụng — nó chỉ vô dụng khi đo ở k=5.** Câu "rổ trần 0,9117 hơn tầng 1
đầy đủ 0,9100 → chấm lại kém hơn không chấm" (mục 📝 BÁO CÁO #3, vẫn đang là "mục mạnh nhất")
**chỉ đúng ở k=5 và sai hẳn ở k=1.** Ở hạng 1 bộ chấm là cần gạt mạnh nhất trong cả hệ thống.
→ Mọi hướng đã đóng đều bị đóng bằng thước recall@5. **Nếu độ đo là precision, phải mở lại cả 16 dòng.**

### 📅 SỬA HẠN CHÓT: Codabench ghi **CURRENT PHASE ENDS 18/09/2026 23:59 GMT+7**, không phải 15/09.
### 📊 MỐC ĐỐI THỦ (07/09): đỉnh LB **0,9591** · nhóm mình 0,9124 · **hạng ~40/83**. Chênh 4,67 điểm recall.

## 🔴 07/09 — ĐO LẠI TRÊN dev1000. BA ĐIỀU LÀM ĐỔI THỨ TỰ ƯU TIÊN.

### ① dev300 LÀ MẪU DỄ. Phần lớn "độ lệch dev↔LB" của bảng E7 là nhiễu lấy mẫu, không phải dịch chuyển phân phối.

Đo trên chính rổ `_matchEmbedded` đang dùng, CPU, 0 giờ GPU:

| | dev300 | **dev1000** |
|---|---|---|
| recall@1 của rổ | 0,6217 | **0,5721** |
| recall@5 của rổ | 0,9117 | **0,8801** ← thấp hơn 3,16 điểm |
| recall@50 của rổ | 0,9883 | **0,9832** |

Hệ thống đầy đủ đạt 0,9467 trên dev300 nhưng LB chỉ 0,9124 — chênh 3,43. **Rổ trên dev1000
thấp hơn rổ trên dev300 đúng 3,16 điểm.** Hai con số này gần trùng nhau: độ lệch dev↔LB
gần như bằng độ lệch dev300↔dev1000. dev300 chỉ là mẫu dễ.

→ **Đổi bàn thử hàng ngày sang dev1000.** Với mọi thí nghiệm mức rổ (fusion, trộn, thứ tự)
chi phí vẫn là **0 giờ GPU** — file rổ đã có sẵn trên máy. Chỉ thí nghiệm chạy cross-encoder
mới đắt gấp 3,3 lần. Bài toán "dev300 không đủ độ phân giải" mà cả tháng 8 vật lộn **giải
được bằng file đã nằm sẵn trên ổ cứng.**

### ② HƯỚNG TRÍCH DẪN / SỐ HIỆU VĂN BẢN: **CHẾT.** Đo 07/09, đừng thử.

| đo trên dev300 | kết quả |
|---|---|
| câu hỏi chứa số hiệu kiểu `100/2019` | **3 / 300** |
| câu hỏi chứa năm (19xx/20xx) | 14 / 300 |
| trong đó gold đúng năm được nhắc | **1 / 14** |

Câu hỏi của bộ đề là **ngôn ngữ đời thường, không trích dẫn**. Mọi mẹo từ vựng (token hoá số
hiệu, bonus khớp số hiệu, ưu tiên năm) đều không có gì để bám. Khớp với hướng đã đóng #10 và #11.
→ **Trận này thuần ngữ nghĩa.** Chỉ model học được dữ liệu trong miền mới ăn được.

### ③ BA LỖ HỔNG CẤU TRÚC ĐẶT RA 19/08 — **CHƯA CÁI NÀO ĐƯỢC LÀM.**

Lưu trữ 19/08 (dòng 2124–2131) đối chiếu với các giải pháp mạnh:

| thành phần | giải pháp mạnh | nhóm mình — **tới hôm nay 07/09** |
|---|---|---|
| truy hồi | bi-encoder **fine-tune** | ❌ vẫn **zero-shot** (D dựng bản gốc, chưa từng huấn luyện) |
| xếp hạng | cross-encoder **fine-tune** | ❌ vẫn bản gốc; 2 lượt hỏng đều TRƯỚC chẩn đoán |
| tách từ tiếng Việt | có | ❌ chưa từng làm — BM25 vẫn `\b\w+\b` |

Cùng lưu trữ đó viết: *"**BỎ HẲN, đừng quay lại:** nâng K · vặn n_bm25 · tinh chỉnh chọn mảnh."*
**Toàn bộ 25–30/08 làm đúng ba thứ đó** — bảng 2×2 `K`×`n`, 14,8 giờ GPU, đổi lấy +0,06.

### 📐 DƯ ĐỊA THẬT, đo trên dev1000

| khoản | điểm |
|---|---|
| gold **ngoài** rổ-50 (việc truy hồi) | **1,68** ← lớn hơn ước lượng 1,17 của dev300 |
| gold **trong** rổ nhưng không vào top-5 (việc chọn) | phần còn lại |
| đuôi rổ hạng 20→50 mua thêm | +0,026 — xác nhận `K`/`n` đã cạn |

Ba câu ngoài rổ trên dev300 thực ra là **17 câu trên dev1000**. Trần truy hồi rộng hơn 40%
so với con số vẫn dùng để lập luận "recall gần cạn".

## ⛔⛔ RÀNG BUỘC CỨNG — ĐỌC TRƯỚC KHI CHỌN MODEL

> **Ngân sách BTC: cả đội 4B tham số. D lấy 1B (truy hồi). E CÒN 3B.**
> **Lượng tử hoá KHÔNG nới được** — 4 bit đổi chỗ chứa, không đổi số tham số.

| model | tham số thật | E dùng được? |
|---|---|---|
| **AITeamVN/Vietnamese_Reranker** ← đang dùng | 0,568B | ✅ |
| Qwen3-Reranker-0.6B | 0,596B | ✅ |
| Qwen3-Reranker-**4B** | **4,02B** | ❌ tên "4B" nhưng thật 4,02B |
| Qwen3-Reranker-**8B** | **8,19B** | ❌ vượt ngân sách **và** ngoài danh sách trắng |

**Danh sách trắng BTC** kịch trần ở ~4B, không model nào 7B/8B. **Mọi LLM thương mại
(GPT/Gemini/Claude) không được chấm điểm.** Cấm gán nhãn tay, cấm dữ liệu ngoài.

⚠️ **Dưới NF4, `sum(p.numel())` báo chưa tới một nửa số thật** (bitsandbytes gói 2 trọng số
vào 1 byte `uint8`). Qwen3-Reranker-4B báo 2,205B cho model 4,02B. Dùng `_real_params`
trong `rerank_qwen.py`. **Tên repo không đáng tin, phải đếm.**

🔑 **Có cửa mở:** thể lệ cho phép đề xuất bổ sung model mã nguồn mở **trước 10 ngày so với
hạn private-test**. Muốn model ngoài danh sách thì đây là đường duy nhất.

## 🗺️ BẢN ĐỒ DƯ ĐỊA (đo lại 28/08 trên rổ `_matchEmbedded`, dev300)

**300 câu đang nằm đâu trong rổ:**

| hạng gold trong rổ | số câu | ai lo |
|---|---|---|
| 1 | 192 | — xong |
| 2–5 | 84 | — xong (cộng dồn **276 câu = 0,9117**, không cần chấm gì) |
| 6–10 · 11–20 · 21–50 | 11 · 4 · 6 | E |
| **ngoài rổ 50** | **3** | **D** |

| | dev300 |
|---|---|
| rổ trần @5 (không chấm lại gì) | **0,9117** |
| tầng 1 đầy đủ (k=3, MAX) | 0,9100 ← **kém hơn không chấm** |
| `blend n=3` (cấu hình đang nộp) | **0,9467** |
| **TRẦN của E = recall@50 của rổ** | **0,9883** |

**13 câu còn sai:** 3 ngoài rổ (D) · 1 gold ở rổ hạng 5 bị CE đẩy ra · 9 cả rổ lẫn CE đều vùi.

**Số mạnh nhất cho báo cáo:** rổ trần 0,9117 **hơn** tầng 1 đầy đủ 0,9100. Chấm lại 50 ứng
viên bằng cross-encoder 568 triệu tham số ra **kém hơn không chấm**. Reranker không yếu —
rổ đã giỏi tới mức không còn gì để sửa. Toàn bộ giá trị còn lại nằm ở tầng 2.

**Việc của D đã đổi chỗ:** recall@50 = 0,9883, gần cạn. Nhưng `blend n=3` đưa **3 slot đầu
của rổ THẲNG vào đáp án**, không qua reranker → **recall@1 của rổ (đang 0,6217) đi thẳng vào
kết quả cuối**. Câu hỏi cho D không còn là "lấy thêm văn bản" mà là "xếp đúng hơn ở hạng 1–5".

## 📉 E7 — ĐỘ LỆCH dev ↔ public LB. **BẢNG QUAN TRỌNG NHẤT FILE NÀY.**

| ngày | cấu hình | dev300 | public LB |
|---|---|---|---|
| 12/08 | candidate D, n=2 | 0.8883 | 0.8573 |
| 17/08 | deepchunk M=20/K=20, n=2 | 0.9083 | 0.8840 |
| 19/08 | BM25 chọn đoạn + gộp 1800, n=2 | 0.9183 | 0.8871 |
| 22/08 | rổ fusion M=10, **n=1** | **0.9350** ← đỉnh dev | 0.8943 ← **thấp nhất** |
| 22/08 | rổ fusion M=10, n=2 | 0.9283 | 0.9033 |
| 22/08 | rổ fusion M=10, **n=3** | 0.9233 ← thấp nhất dev | **0.9063** ← **đỉnh LB** |
| 23/08 | rổ fusion M=20, n=2 | — | 0.9109 |
| 25/08 | **rổ mới M=20, n=3** | — | **0.9118** ← BÀI CHỐT |
| 25/08 | rổ mới M=20, n=1 · n=2 · n=4 | — | 0.9031 · 0.9104 · 0.9056 |
| 30/08 | **rổ mới M=20, `K=50`, n=2** | — | **0.9124** ← BÀI CHỐT |
| 30/08 | rổ mới M=20, `K=50`, n=3 | — | 0.9118 |

**⛔ KHÔNG CÓ HẰNG SỐ QUY ĐỔI.** Độ lệch thay đổi theo `n`: −5,08 (n=0) · −4,07 (n=1) ·
−2,50 (n=2). Và **dev đã từng ĐẢO DẤU**: chênh dev −1,17 ứng với chênh LB **+1,20**.

> **dev300 dự báo được THỨ TỰ khi hiệu ứng LỚN, KHÔNG dự báo được mức tuyệt đối.**

⚠️ **SỬA 30/08 — quy tắc "dưới 1,5 điểm không đo được" chỉ đúng cho so sánh KHÔNG ghép cặp.**
Sai số không ghép cặp thật ra là **1,30 điểm** (√(p(1−p)/300)). Nhưng **mọi phép so trong dự án
này đều ghép cặp** — cùng 300 câu, cùng rổ, chỉ đổi một tham số — nên chỉ câu **bất đồng** mới
mang thông tin. Dùng McNemar trên rổ `_matchEmbedded`, K=20:

| cặp | A thắng | B thắng | bất đồng | Δ điểm | p |
|---|---|---|---|---|---|
| n=2 vs **n=3** | 1 | 6 | 7 | +1,67 | 0,125 |
| n=1 vs **n=2** | 1 | 8 | 9 | +2,33 | **0,039** |
| n=0 vs **n=3** | 2 | 23 | 25 | +7,00 | **<0,0001** |

**dev300 mạnh hơn ta tưởng ~3 lần, miễn là so ĐÚNG CÁCH. 0 giờ GPU.**
→ Từ nay báo cáo mọi Δ dev kèm **(thắng / thua / bất đồng)**, không chỉ hiệu hai số trung bình.

Rổ `_matchEmbedded` là ví dụ đắt nhất: **dev +3,83 → public +0,11.**

## 📈 CHUỖI TĂNG TIẾN — BASELINE

**Mọi thí nghiệm mới phải báo cáo dạng Δ so với hai con số này:**
> **dev300 = 0.8883** · **public LB = 0.8573** (AITeamVN gốc + `blend n_bm25=2`, candidate D)

| bước | public LB | Δ |
|---|---|---|
| rerank AITeamVN, n=0 | 0.8350 | — |
| + `blend_bm25_first(n=2)` | 0.8573 | +2,23 |
| + deepchunk M=20/K=20, `max` | 0.8840 | +2,67 |
| + BM25 chọn đoạn + gộp 1800 | 0.8871 | +0,31 |
| + rổ FUSION (M=10, n=3) | 0.9063 | +1,92 |
| + M=20, n=2 | 0.9109 | +0,46 |
| + rổ `_matchEmbedded`, n=3 | **0.9118** | +0,09 |

**Đọc bảng:** hai đòn lớn nhất (reranker +11 trên dev, rổ tốt hơn +2,4) đều là **đổi thứ
nạp vào**, không phải tinh chỉnh cái đang có.

## ⛔ HƯỚNG ĐÃ ĐÓNG — ĐỪNG THỬ LẠI. Mỗi dòng là một phép đo đã trả tiền.

| # | hướng | kết quả |
|---|---|---|
| 1 | fine-tune toàn phần (2 lần) | **−0,50** rồi **−6,50** — ⚠️ **DÒNG NÀY SAI, XEM MỤC 07/09.** Lưu trữ 19/08 (dòng 2145–2152) đã **MỞ LẠI** hướng này kèm chẩn đoán nguyên nhân và 3 chỗ sửa. Bản cô đọng 28/08 đánh rơi phần mở lại. Hai lượt thất bại đều chạy TRƯỚC chẩn đoán. |
| 2 | chưng cất từ Qwen3-8B | NET **−16** nhóm/600. Thầy 0,5417 **thua** trò 0,5683. Còn vi phạm danh sách trắng |
| 3 | probe — học lại đầu phân loại (encoder đóng băng) | Δ tốt nhất **+0,67**; **18 câu sai: 5/18 → 5/18, không đổi câu nào** |
| 4 | `M=30` | trần **~0** (3 câu chạm tới, 2 có oracle thấp hơn điểm hiện tại, 1 có 378 đoạn) |
| 5 | ensemble nhiều bộ chấm | âm |
| 6 | trộn hai pipeline (rổ cũ ⊕ rổ mới) | âm |
| 7 | gộp điểm z-score / RRF hai thứ hạng | **thua `blend n=3` ở MỌI tham số** |
| 8 | chọn `n` thích nghi theo câu | trần **oracle +1,17** — dưới ngưỡng |
| 9 | ưu thế theo loại văn bản / thẩm quyền | âm, **kể cả khi ước tham số ngay trên dev300** |
| 10 | ưu tiên văn bản mới / còn hiệu lực | gold là văn bản mới nhất đúng **2,0%** = ngẫu nhiên |
| 11 | ghép tên văn bản | slug không dấu **−2,0**; tiêu đề có dấu **+1,00** nhưng **83% trùng** tầng 2 |
| 12 | Gemini / LLM ngoài | hoà, **và BTC cấm** |
| 13 | "gợi ý liên quan" kiểu Google | thua cả ba biến thể |
| 14 | tăng `top_chunks` 3→5 | đã rút lại |
| 15 | cắt ứng viên 100→50→25 | đòn **chi phí**, không phải đòn điểm |
| 16 | cải tiến `pick_chunks` | `K=20` đã bắt **90%** giá trị oracle → gần cạn |

**Còn sống:** chỉ còn **truy hồi của D** (recall@1 = 0,6217). `K` và `n` đã đóng bằng bảng 2×2 đầy đủ.

## 🟢 30/08 — **BẢNG 2×2 `K` × `n` ĐÃ ĐỦ. CHỐT `K=50, n=2` = 0.9124. ĐÓNG CẢ HAI CẦN GẠT.**

| public LB | **n=2** | **n=3** | hiệu ứng `n` |
|---|---|---|---|
| **K=20** | 0.9104 | 0.9118 | **+0,14** |
| **K=50** | **0.9124** ← chốt | 0.9118 | **−0,06** |
| **hiệu ứng `K`** | **+0,20** | **0,00** | |

**`K` và `n` THAY THẾ NHAU — chúng sửa cùng một chỗ.** Cả hai đều nhắm vào phần bộ chấm làm hỏng
(cứu 14 / hỏng 22). `n` che bằng cách giữ chỗ; `K=50` chữa bằng cách cho bộ chấm đọc kỹ hơn. Làm
một cái rồi thì cái kia hết việc: `K` ăn +0,20 ở `n=2` nhưng **đúng 0,00** ở `n=3`.
Đây là ví dụ sống của quy luật 7 — *"bốn giải pháp hoá ra là một, đừng cộng dồn"*.

**Không nộp tiếp `n=1` hay `n=4` ở K=50.** Ở K=20 chúng cách đỉnh −0,73 và −0,62; mức `K` ăn được
nhiều nhất là +0,20. Số học không cho chúng vượt 0.9124.

### 📏 GIÁ THẬT CỦA CẢ HƯỚNG `K=50`: **14,8 giờ GPU cho +0,06 điểm** (0.9118 → 0.9124 = 0,6 câu).

### 🔮 ƯỚC LƯỢNG TRƯỚC-KHI-NỘP: dùng được, nhưng chỉ ở mức bậc độ lớn

Phương pháp (29/08): với mỗi câu đổi đáp án, lấy hạng-trong-rổ của văn bản bị đẩy ra / đưa vào,
nhân với `P(gold | hạng rổ)` đo trên dev300, cộng lại. Chạy CPU vài giây.

| | ước | thật | lệch |
|---|---|---|---|
| n=3 | +0,006 | **+0,000** | trúng |
| n=2 | +0,021 | **+0,200** | hụt 10× (nhưng chỉ 1,3σ) |

**Kết luận về công cụ:** đúng dấu cả hai lần, đúng độ lớn một lần, và **đúng ở việc quan trọng
nhất — nói rằng đây là cần gạt dưới 0,5 điểm.** Nếu chạy nó TRƯỚC thì đã tiết kiệm 14,8 giờ.
→ **Từ nay: mọi lượt GPU trên 1 giờ phải chạy ước lượng này trước.** Nó chỉ cần một file scores
đã có sẵn và thứ tự rổ.

🚧 **BIÊN GIỚI HIỆU LỰC của công cụ (đo 30/08 — quan trọng):** nó **CHỈ dùng được khi hai phía so
sánh đến từ CÙNG một cơ chế chọn.** Thử áp cho `n=2` vs `n=3`: ước **+3,49 điểm** cho n=3, thật
chỉ **+0,14** — hụt **25 lần**.
**Vì sao:** `P(gold | hạng rổ)` là xác suất tiên nghiệm của một văn bản *bất kỳ* ở hạng đó. Nhưng
slot của `n` được **bộ chấm CHỌN** — điều kiện "CE thích nó" đẩy P(gold) lên cao hơn hẳn tiên
nghiệm theo hạng. So `K=20` vs `K=50` thì cả hai phía đều do CE chọn → thiên lệch **triệt tiêu**,
ước đúng. So `n` thì một phía lấy theo rổ, một phía do CE chọn → thiên lệch **không** triệt tiêu.
Đây đúng là quy tắc 3 ("đừng đánh giá trên mẫu được chọn bằng một cơ chế khác") ở dạng khác.

⚠️ Đừng đọc bảng 2×2 quá mạnh: chênh lệch giữa các ô là **0,6–2 câu**. Cơ chế "thay thế nhau"
khớp với mọi ô và khớp với cơ chế đã biết của `n`, nhưng nó tựa trên 2 câu.

## 🧠 QUY LUẬT ĐÃ TRẢ GIÁ ĐỂ HỌC

1. **Ngưỡng phải TƯƠNG ĐỐI so với mốc hiện có, không bao giờ là con số tuyệt đối bốc ra.**
   Đã sai 3 lần (pre-register +2,0 cho `rescore8b`; cổng ≥0,60 cho nhãn thầy; cổng probe).
2. **Mọi phép đo bộ chấm phải in kèm dòng "rổ trần, không reranker".** Cấu hình đang đo còn
   thua dòng đó thì DỪNG, đừng đọc Δ. Một dòng code — đã cứu 3h GPU + cả nhánh LoRA.
3. **Không đánh giá model B trên mẫu được chọn bằng LỖI của model A.** Hồi quy về trung bình.
   Suýt tốn 25h GPU. So thì so trên mẫu ngẫu nhiên, hoặc đếm cả hai chiều cứu/hỏng.
4. **Mọi con số dư địa phải đo ở ĐÚNG cấu hình bài đang nộp**, và ghi kèm cấu hình bên cạnh
   con số. Đã sai 2 lần trong một ngày (trần 0,80 của *chọn đoạn* áp cho *sửa model*;
   đếm "22 câu hỏng" ở `n=1` trong khi bài nộp chạy `n=3` — thật ra chỉ hỏng 1 câu).
5. **"Có tín hiệu thô" ≠ "cộng vào được".** Một ưu thế TOÀN CỤC không thắng nổi bộ chấm đã
   đọc nội dung, trừ khi nó nói được điều gì đó **riêng cho từng câu**.
6. **"Không thấy hiệu ứng ở MỘT điểm đo" ≠ "hiệu ứng không tồn tại".**
7. **Bốn "giải pháp" hoá ra là một — đừng cộng dồn chúng.** Đọc sâu, tiêu đề, rổ tốt hơn,
   chấm lại: tất cả sửa **cùng một nhóm câu**. Đo riêng thì cái nào cũng dương, gộp lại thì
   không cộng được. Kiểm chồng lấn **trước** khi cộng.
8. **Chỉ chạy thí nghiệm kỳ vọng đổi ≥2 điểm.** Dưới ~1,5 điểm là dưới sàn nhiễu dev300.
9. **Đo trần TRƯỚC khi chạy**, đừng đoán. Đã cứu M=30 (~4h), chưng cất (~18h), thích nghi `n`.
10. **Quy tắc 4 áp cho CẢ CHI PHÍ, không chỉ dư địa.** 28/08: tôi đo mẫu 240 văn bản ra
    37,7 đoạn/văn bản ở `K=50` (→ 754/câu, đúng), rồi lại **quy đổi qua con số "157.008 đoạn"**
    trong quy tắc 6 — vốn là của một cấu hình KHÁC (157/câu). Ra 6,9h, thật là **14,8h**.
    Sai gấp đôi. **Có mẫu đo trực tiếp thì dùng thẳng nó, đừng bắc cầu qua số cũ.**
    *(Số đúng cho M=20/K=20 trên đề thi là ~338/câu, không phải 157/câu. Quy tắc 6 cần đo lại.)*

## 📋 QUY ƯỚC LÀM VIỆC

- **Câu đầu tiên luôn là kết luận** — ngắn, rõ, trực tiếp. Chi tiết để sau.
- **MẶC ĐỊNH LÀ NGẮN (Khim chốt 10/09).** Trả lời gọn, dễ hiểu, không giải thích dài.
  Đưa kết luận + số quyết định + việc cần làm. **Khim sẽ tự hỏi khi cần bóc chi tiết.**
  - đừng dựng bảng/mục lồng nhiều tầng cho một câu hỏi đơn giản
  - đừng liệt kê hết mọi phép đo đã chạy; chỉ nêu cái đổi quyết định
  - đừng viết đoạn biện hộ cho lựa chọn — nói lựa chọn là gì, xong
  - vẫn giữ: nói thẳng khi số liệu yếu, và nói rõ khi mình nói quá ở lượt trước
- **CLAUDE.md cập nhật liên tục, không cần hỏi.** `BaoCao_E.md` **CHỈ sửa khi Khim yêu cầu**.
- ⚠️ `BaoCao_E.md` **đang CŨ, dừng ở 12/08** (còn ghi `n_bm25=1`, LB 0.8440). Khi cập nhật thì
  lấy số từ file này — **đừng tự làm trước**.

### BẮT BUỘC: gọi skill `ponytail` mức `full` TRƯỚC MỌI VIỆC CODE

Gọi skill thật, trước dòng code đầu tiên. Áp dụng cho: viết/sửa file, notebook, refactor,
review, chọn thư viện. **Không** áp dụng cho: phân tích số liệu, đọc log, viết CLAUDE.md.

Vì sao gắt: repo đã có sẵn `chunks_of`, `tok`, `read_passage`, `blend_bm25_first`,
`evaluate`, `score_all_from_d`, `load_reranker`, `pick_chunks`, `deepen_all`. Gần như mọi
việc mới là **ghép lại đồ có sẵn**.

### NHẮC MỞ CHAT MỚI khi ngữ cảnh phồng

Nhắc Khim mở chat mới khi: đã đọc ≥5 file lớn · hội thoại >25 lượt · đổi việc · vừa đóng một
hạng mục và đã ghi kết luận. Một câu ở cuối câu trả lời, nhắc xong thì thôi.
**Điều kiện bắt buộc trước khi nhắc: đã cập nhật CLAUDE.md.**

### QUOTA GPU — 6 quy tắc

**Quota KHÔNG còn là nút thắt** (60h/tuần, ~240h tới 15/09, kế hoạch ăn ~78h). Chỗ chật thật
là **trần cứng 12h/lượt commit**, **số lượt nộp/ngày**, và **độ phân giải dev300**.

1. **Làm hết phần CPU trước khi chạm GPU.** Kiểm đường dẫn, key qid, dry-run, đếm chunk.
2. **Mỗi lượt GPU BẮT BUỘC sinh `scores_*.json` và tải về trước khi đóng phiên.** Không có
   scores = mọi thí nghiệm hậu kỳ phải chạy lại GPU. Lỗi đắt nhất đã mắc.
   *(Hệ quả mới 28/08: probe hai lượt đầu viết `MOC, _ = cham(...)` — vứt điểm đầu gốc, nên
   không phân tích từng câu được. Lượt k3 giữ lại → mọi phân tích sau đó miễn phí trên CPU.)*
3. **Mỗi lượt chỉ đổi MỘT biến.**
4. **Chỉ chạy thí nghiệm kỳ vọng đổi ≥2 điểm.**
5. **Gộp việc vào một phiên** — một lần khởi động, một lần tải model.
6. **Ước chi phí bằng SỐ CHUNK**, đừng ước bằng cảm giác — và **đếm cho ĐÚNG cấu hình sắp chạy**.
   Mốc đã kiểm 28/08: **đề thi M=20/K=50 = 685.196 đoạn = 14,8h @12,9 đoạn/s.**
   ⚠️ Con số cũ "đề thi = 157.008 chunk ≈ 1h45m" **không phải** của M=20/K=20 — đừng bắc cầu
   qua nó. `DC.count_deep_chunks` chạy CPU 3–4 phút và cho số thật; luôn đọc nó trước khi chấm.
7. **Trước MỌI lượt chạy trên 1 giờ, hỏi thành viên kia có đang làm việc đó không.** 19/08 mất
   4h dựng bi-encoder trong khi D đã làm xong. Chi phí 2 phút, cứu cả lượt GPU.

## 🪤 BẪY ĐÃ DÍNH, ĐỪNG DÍNH LẠI

**① ĐƯỜNG DẪN KAGGLE — tự dò, đừng hardcode:**

```python
INPUT_DIR = next(p for p in ("/kaggle/input/project-ir",
                             "/kaggle/input/datasets/locdovan211/project-ir")
                 if os.path.isdir(p))
CTX = next(p for p in (f"{INPUT_DIR}/selected-contexts/selected-contexts",
                       f"{INPUT_DIR}/selected-contexts")
           if os.path.isdir(p) and any(f.startswith("context_") for f in os.listdir(p)))
```
Kiểm bằng **có file `context_*.json` bên trong**, không phải `isdir`. Bản LỒNG phải để trước.

**② GUARD KIỂM BẰNG TEXT TỰ BẮN VÀO CHÂN.** `inspect.getsource` chứa cả docstring — docstring
bản mới trích code cũ là assert nổ oan, giết một lượt GPU.
→ **Kiểm bằng CHỮ KÝ HÀM hoặc hành vi:** `assert list(inspect.signature(f).parameters) == [...]`

**③ CACHE VECTOR KIỂM BẰNG SỐ HÀNG LÀ KIỂM HỜ.** Vector đoạn 900 và 1800 ký tự có **cùng số
hàng** → `nap()` nạp nhầm dữ liệu hỏng mà không báo gì. **Đổi TÊN FILE theo cấu hình.**

**④ `deepen_all` CHỈ trả về câu được truyền vào.** Gán đè `scores = deepen_all(lát, ...)` là
**mất tầng 1 của các câu ngoài lát**. Phải `scores.update(...)`.

**⑤ "TRA BẢNG NHÚNG NGOÀI BIÊN"** — device-side assert trên T4, đã dính 3 lần với model
`trust_remote_code`. Không phải lỗi phần cứng.

**⑥ NỘP NHẦM ĐỀ.** Bài 09/08 bị từ chối vì nộp dự đoán 150 câu dev. Guard `expected_qids`
không tự biết bạn nộp nhầm đề. → **Mọi file dev phải giữ hậu tố `_dev` + số câu trong tên.**

**⑦ Vượt 5 id ở một câu → CHỈ câu đó bị Recall/Precision = 0**, không phải cả bài.

**⑧ KHOÁ XẾP HẠNG CUỐI LÀ `max(ce, ce_deep)`, KHÔNG PHẢI `ce_deep`.** 30/08 tôi phân tích K50
bằng `ce_deep` và ra kết luận **ngược dấu** (K50 kéo top-5 ra XA thứ tự rổ). Dùng đúng khoá thì
ngược lại — kéo **về gần** rổ. → **Mọi phân tích CPU trên `scores_*.json` phải dựng lại bài nộp
và kiểm khớp `1000/1000` TRƯỚC khi đọc bất kỳ Δ nào.** Phép kiểm mất 5 giây và đã cứu một kết
luận sai hoàn toàn.

## 📁 DỮ LIỆU

| file | nội dung |
|---|---|
| `Input/public-official.json` | **1000 câu đề thi**, `answer: null`, giao với train = 0 |
| `Input/train.json` | 7000 câu có nhãn |
| `Input/selected-contexts/` | corpus **8.532** document · `context_<id>.json` → `{link, passage, id}` |
| `dev_1000_locked.json` | toà án cuối. Bao trùm dev300 + dev150 |
| `dev_300_locked.json` | thử nhanh hàng ngày (1,05 gold/câu) |
| `dev_150_locked.json` | **ĐÃ KHAI TỬ** — 256/300 câu giờ nằm trong tập huấn luyện |
| `fusion_rrf_top50_{dev_1000,public}_matchEmbedded.json` | **rổ đang dùng** (207MB mỗi file) |
| `bm25_ids_train_FALLBACK.json` | hard negative, 7000 câu × 20 doc_id |

`train.json 7000 ⊃ dev1000 ⊃ dev300`. Loại dev1000 khỏi huấn luyện là loại hết mọi tập dev.

**Tài sản phân tích (Ketqua_E/) — cho phép đo dev300 trên CPU trong vài giây, không cần GPU:**

| file | nội dung |
|---|---|
| `order_dev300_matchEmb.json` · `rrf_dev300_matchEmb.json` | thứ tự + điểm rổ, tách sẵn từ file 207MB |
| `scores_dev300_{moc,probe}_k3.json` | điểm từng văn bản của **cả đầu gốc lẫn đầu học lại** |
| `vanban_meta.json` | 5.244 văn bản: loại · năm ban hành · có phải cấp địa phương |
| `oracle_chunks_dev300.json` | CE chấm **toàn bộ đoạn** của 23 văn bản gold (7.362 cặp) |
| `vec_{train,dev}_1800.npy` | vector CLS đã cache — huấn luyện lại đầu phân loại mất 15s CPU |
| `bang_ablation.md` | bảng đối chứng 10 bộ chấm, **dán thẳng vào báo cáo** |
| `scores_public_fusion_M20_K50_matchEmbedded.json` | **điểm đề thi ĐẦY ĐỦ NHẤT** (1000 câu × 50 vb, 20 vb có `ce_deep` ở K=50). `ce` tầng 1 khớp bit-perfect với bản K=20; `ce_deep` chỉ tăng. Dùng file này thay bản K=20 cho mọi thí nghiệm CPU trên đề thi |
| `submission_matchEmb_K50_n{0..4}.zip` | 5 bài nộp K=50, **đã dựng lại từ scores khớp 1000/1000**. Hợp lệ nhưng **không đáng nộp** |

## 👥 VAI TRÒ

Khim = **thành viên E** — Xếp hạng & Chốt top-5. Sở hữu `recall@5`.
D lo hạ tầng + sinh ứng viên, E tiêu thụ và chốt submission.

## 📝 BÁO CÁO — bốn mục có số liệu sẵn, không cần thêm giờ GPU

1. **Bảng ablation 10 bộ chấm** (`bang_ablation.md`) — số tham số KHÔNG dự đoán chất lượng:
   `mMiniLMv2` 0,118B hơn `ViRanker` 0,568B tới +3,50 điểm.
   ⚠️ cả bảng đo ở `EXC=900` (đoạn bị cắt đôi) — thứ hạng tin được vì cùng giao thức, con số
   tuyệt đối thấp hơn thực tế.
2. **Vì sao chưng cất không ăn** — 600 nhóm, thầy 8B thua trò 0,568B, NET −16.
3. **Vì sao reranker teo khi rổ mạnh lên** — rổ trần 0,9117 vs tầng 1 0,9100. **Mục mạnh nhất.**
4. **Hệ thống cổng đặt trước đã cứu ~21h GPU** — `congkiem` (18h) + `assert MOC >= SAN` (3h + nhánh LoRA).

**Về nhóm câu không cứu được, viết cho đúng:** đọc thật 2 ca cho thấy model tối ưu **độ khớp
câu chữ**, còn đáp án đúng đòi biết **văn bản nào có thẩm quyền** (ca `138214`: model chọn QĐ
UBND Hà Nội thay vì Nghị định toàn quốc — trùng chữ nhiều hơn nhưng sai phạm vi). Cross-encoder
chấm tương đồng câu hỏi–đoạn **không có chỗ biểu diễn thứ bậc pháp lý**. Đó là lý do thêm tham
số (8B) cũng không cứu được. *(Mới đọc 2/13 ca — giả thuyết có ví dụ, chưa phải số liệu.)*

**Câu KHÔNG được viết:** "chúng tôi chứng minh model không còn tín hiệu để khai thác" — không
có bằng chứng cho câu đó. **Câu viết được:** "chúng tôi đo được đóng góp biên của khâu xếp hạng
đã tụt xuống dưới ngưỡng phát hiện của tập dev, nên đóng hướng".

---

## 08-09 · Bản chạy public FT đầu tiên HỎNG một nửa — chẩn đoán và cứu

**Triệu chứng.** `sub_FT_N1_k50.zip` lệch bài đang nộp **104/1000** câu. Với `N=1`
chỉ `order[q][0]` được xét nên nó **phải** trùng tuyệt đối. Ví dụ câu `1392`:
zip chọn `263207`, `order[0]` là `53190`, và `53190` **không có mặt** trong 3 văn
bản đã chấm.

**Chẩn đoán.** Xếp các câu theo đúng thứ tự `Q` rồi đếm số câu lệch theo khối 100:

```
theo khoi 100 cau: [0, 0, 0, 0, 0, 56, 53, 43, 53, 45]
```

Ranh giới sạch ở **câu 500** — đúng bước checkpoint. Đây là dấu vết của một phiên
**resume**, không phải lỗi ngẫu nhiên. Dò lại rổ đã chấm với mọi bộ điểm có trong máy:

| bộ điểm | 500 câu đầu | 500 câu sau |
|---|---:|---:|
| `scores_public_fusion_M20_K50_matchEmbedded.json` | **500/500** | 250/500 |
| `tang1_scores_public_fusion_M10_K20_matchEmbedded.json` | 223/500 | **500/500** |

Khớp tuyệt đối cả hai đầu. Phiên 1 dùng bộ điểm đúng, phiên 2 `find()` bắt phải một
file **trùng tên nhưng khác ruột** — thực chất là bộ điểm **tầng 1, M10/K20, không có
`ce_deep`**. Nửa sau của bài chấm trên một rổ yếu hơn hẳn: **64/500 câu rổ thậm chí
không chứa đáp án đang nộp**, 40 câu khác có nhưng nằm ở hạng 2–3.

**Quy tắc rút ra (số 8).** *Nhận diện dữ liệu đầu vào bằng RUỘT, không bằng TÊN.*
`find()` đi bộ `/kaggle/input` và trả về **kết quả đầu tiên**; thứ tự đó đổi khi thêm/bớt
dataset giữa các phiên. Một `assert` trên tên file không bảo vệ được gì. Từ nay mọi
notebook đọc bộ điểm phải chốt **md5 + hình dạng** (số ứng viên/câu, số bản ghi có
`ce_deep`) trước khi chạy, và `res` nối tiếp chỉ được dùng lại nếu md5 khớp.

**Quy tắc số 9.** *`N=1` là dây tín hiệu.* Nếu bài `N=1` không trùng khít bài đang nộp
thì rổ sai, dừng ngay — không cần biết `N=2`, `N=3` ra sao. Đã đưa `assert dif==0`
vào ô 3.

**Đã sửa trong `public_ft_run.ipynb`:**
- ô 1: `find()` gom **mọi** bản trùng tên, băm md5, báo lỗi nếu chúng khác ruột; thêm
  kiểm vân tay `SIG_MD5 / 50 ứng viên mỗi câu / ≥20 000 bản ghi có ce_deep`.
- ô 2: ghi `public_ft_meta.json` cạnh điểm; khi nối tiếp, **vứt** điểm cũ nếu md5 hoặc
  `N_DOC/K_CHUNK` lệch, và vứt riêng những câu có rổ không khớp `order[:N]`.
- ô 2: tự nạp `public_ft_scores_SEED500.json` nếu có trong input → chỉ chạy lại 500 câu
  sau, **~1,5h** thay vì ~3h.
- ô 3: chặn dựng bài nộp nếu bất kỳ câu nào có rổ lệch `order[:N_DOC]`.

**Cứu được ngay, 0 giây GPU.** 500 câu đầu chấm trên rổ đúng nên dùng được nguyên vẹn.
Bài lai: FT chọn trên 500 câu đầu, giữ nguyên bài 0.702 trên 500 câu sau.
- `sub_LAI_FT3_nua_dau.zip` — 97/1000 câu đổi
- `sub_LAI_FT2_nua_dau.zip` — 84/1000 câu đổi

Đây là một **phép thử ghép cặp một nửa**: nếu FT thật sự tốt thì nó phải thắng ở đây với
khoảng một nửa biên độ. Mốc phải vượt vẫn là **recall 0,6712**. Thua thì nộp lại
`A_K50_max_DANGNOP.zip` ngay trong ngày.

### 08-09 · Bài lai THẮNG: 0,702 → 0,712

`sub_LAI_FT3_nua_dau.zip` → **precision 0,712 · recall 0,67975** (mốc cũ 0,702 / 0,6712).

**+10 câu đúng trên 1000**, đổi 97 câu, tất cả nằm trong 500 câu có rổ đúng.
Kiểm tính nhất quán: recall tăng 0,00855 / 10 câu = 0,855 mỗi câu → phần lớn câu được
cứu chỉ có **1 văn bản vàng**. Khớp với định nghĩa recall macro, không có dấu hiệu bất thường.

**Sức mạnh bằng chứng — nói thẳng.** Chỉ biết `c − b = 10` trên 97 câu đổi, không biết
`b`, `c` riêng lẻ (bảng không trả nhãn). McNemar do đó chỉ chặn được hai đầu:
`b+c=97` → p≈0,31; `b+c=20` → p≈0,025. **Một mình con số này chưa đủ kết luận.**
Nhưng nó cộng vào một chuỗi đã có: dev300 McNemar 22–8 (p=0,0161) và lưới richharness
FT thắng gốc **20/20 ô**. Ba nguồn độc lập, cùng dấu, cùng cỡ.

**Điểm quan trọng nhất:** đây là hiệu ứng ĐẦU TIÊN sống sót khi ra bảng thật. RRF và
`replace` đều dương trên dev300 rồi âm trên bảng. FT thì không — dev300 dự đoán +1,4…+1,9,
thực nhận +1,0, cùng chiều và cùng cỡ.

**Hệ quả về vị thế:** bảng hiển thị bài MỚI NHẤT, và bài mới nhất giờ là 0,712 > 0,702.
**Không cần nộp lại `A_K50_max_DANGNOP.zip` nữa.** Nó lùi về vai trò lưới an toàn.

**Việc tiếp theo:** chạy 500 câu sau bằng seed. Nếu hiệu ứng giữ nguyên biên độ,
dự kiến ≈ **0,722**. Đây cũng là phép kiểm tra lặp lại độc lập trên nửa tập chưa đụng tới.

### 08-09 · Guard bắt được thủ phạm thật, ở giây thứ 43

Chạy lại `public_ft_run.ipynb`, ô 1 dừng ngay:

```
bo diem md5=7682dc56dbc03e4c8ff9791ea6eeebef  ung vien/cau=[50]  ban ghi co ce_deep=10,000
AssertionError: chi 10,000 ban ghi co ce_deep (<20,000) — DAY LA BO DIEM TANG 1, SAI FILE
```

| | trong máy | trên Kaggle `project-ir` |
|---|---|---|
| md5 | `90e09359…` | `7682dc56…` |
| bản ghi có `ce_deep` | 20 000 | **10 000** |
| ứng viên/câu | 50 | 50 |

File trên Kaggle mang **đúng cái tên** `scores_public_fusion_M20_K50_matchEmbedded.json`
nhưng ruột là **M10** — chỉ 10 văn bản đầu được chấm sâu, không phải 20. Rổ sai.

**Đây là lời giải cuối cùng cho vụ hỏng nửa bài.** Phiên 1 `find()` bắt được bản đúng ở một
dataset khác; phiên 2 dataset đó không còn/đổi thứ tự nên nó rơi vào bản M10 của `project-ir`.
Không phải lỗi logic, không phải lỗi resume — chỉ là **một cái tên trỏ vào hai thứ khác nhau**.
Quy tắc 8 được xác nhận bằng thực nghiệm chứ không phải bằng suy luận.

**Chốt hạ (quy tắc 10).** *Đặt vân tay vào TÊN file.* Tên trung tính thì bản cũ trà trộn được;
tên `scores_public_M20K50_90e09359.json` thì không bản nào giả dạng nổi. Ô 1 nay tìm tên có
vân tay trước, chỉ lui về tên cũ khi không thấy, và vẫn kiểm md5 ở cả hai đường.

Đã đặt sẵn `Ketqua_E/lai_ft/scores_public_M20K50_90e09359.json` (md5 `90e09359…`) để upload.

### 08-09 · Chạy lại sạch. `sub_FT_N3_k50.zip` sẵn sàng nộp

26 phút, 54 082 cặp cho 500 câu sau (tổng 108 326 cặp). Guard qua hết:

```
van tay bo diem: DAT          md5 90e09359 · 50 ứng viên/câu · ce_deep 20 000
nhan 500/500 cau tu 'seed'    seed không bị vứt oan
kiem ro: 1000/1000 khop order[:3]
N=1 -> 0/1000                 dây tín hiệu: rổ đúng
```

Kiểm lại 5 cửa ở máy, độc lập với notebook:

| | |
|---|---|
| số câu | 1000/1000 |
| rổ == `order[:3]` | **1000/1000** |
| 500 câu đầu == seed | 500/500 (không chấm lại) |
| `CUR` == bài 0.702 | 1000/1000 |
| zip khớp tính lại (N=1/2/3) | 1000 · 1000 · 1000 |

**Cấu trúc đẹp hơn mong đợi — đây là phép thử tăng dần hoàn hảo.**
97 câu bài lai đã đổi nằm **trọn vẹn** trong 192 câu của N=3, và N=3 giữ **y nguyên** lựa chọn
của bài lai ở cả 500/500 câu đầu. Nên `N=3` = **bài 0,712 + đúng 95 câu mới**, tất cả nằm ở
500 câu sau. Đối xứng: nửa đầu đổi 97/500, nửa sau đổi 95/500.

Suy ra: 97 câu đầu đã được bảng chấm là **+10**. Nếu 95 câu sau hành xử giống hệt thì
N=3 ≈ **0,722**. Bảng chỉ cần trả về > 0,712 là hiệu ứng FT được xác nhận lần thứ hai,
trên nửa tập chưa đụng tới — cỡ mẫu ghép cặp tăng gấp đôi, McNemar ra khỏi vùng mập mờ.

**Thông lượng thật (sửa quy tắc 6).** 54 082 cặp / 26 phút = **34,7 cặp/s** trên T4,
không phải 9,35 như tôi ước từ lần dev1000. Ước sai 3,7× theo chiều ngược lại.
Bài học không đổi: **đừng mượn thông lượng đo ở cấu hình khác** — hoặc đo 50 câu trước
rồi mới ngoại suy, hoặc đừng ước.

### 08-09 · `sub_FT_N3_k50` = **0,711**. Nửa sau KHÔNG lặp lại nửa đầu.

| | số câu đổi | NET |
|---|---:|---:|
| nửa đầu (bài lai, đã nộp) | 97 | **+10** |
| nửa sau (mới) | 95 | **−1** |
| **gộp** | **192** | **+9** → 0,711 |

**Tôi dự đoán ≈0,722 và sai.** Sai ở đâu thì rõ: tôi lấy tỉ lệ thắng của nửa đã-thắng làm
tỉ lệ nền cho nửa chưa đo. Bài lai được nộp vì nó là thứ duy nhất cứu được, rồi kết quả của
nó bị tôi dùng làm mốc ngoại suy — đúng kiểu chọn mẫu mà quy tắc 7 cảnh báo, chỉ khác dạng.

**Đọc đúng con số:**
- Chênh lệch giữa hai nửa (+10 vs −1) = 11 câu, sd ≈ √192 ≈ 13,9 → z ≈ 0,79. **Hai nửa
  hoàn toàn tương thích với nhau.** Không phải nửa sau "hỏng", mà nửa đầu **may**.
- Gộp: +9 trên 192 câu đổi. Nếu cả 192 đều phân định thì z = 9/√192 = 0,65 (p≈0,52);
  kể cả chỉ 40 câu phân định thì z = 1,42 (p≈0,16). **Không đạt ý nghĩa thống kê ở mọi giả định.**
- Ước lượng điểm tốt nhất cho hiệu ứng FT trên public: **≈ +0,9 điểm**, không phải +2.

**0,712 và 0,711 lệch nhau ĐÚNG 1 CÂU.** Chọn cái cao hơn là chọn nhiễu. Bài lai còn là một
phương pháp không nhất quán (FT nửa này, gốc nửa kia) — nó cao hơn do ngẫu nhiên, không do tốt hơn.

**Về vị trí hiện tại:** ghi chú 07/09 dòng 263 đã viết *"trần thực tế của kiến trúc hiện tại
trên độ đo này là khoảng 0,71–0,72; vượt GoGo (0,7210) gần như chắc chắn cần một thứ khác về
bản chất"*. Đang ở **0,711**. **Đã chạm trần đó.** FT listwise là cú đấm mạnh nhất còn lại
trong kiến trúc này và nó trả về đúng +0,9 điểm. Mọi tinh chỉnh tiếp theo sẽ nằm dưới sàn nhiễu.


---

## 10-09 · TRỤC `k`: ĐÓNG. Đo trần trên CPU, tiết kiệm 16 phút GPU + 2 lượt nộp.

**Giả thuyết đem đo:** bài đã nộp chạy `K_CHUNK=50` (đọc trọn văn bản, trung vị 47 đoạn/vb)
nhưng bảng N×k trên dev300 **chỉ đo tới k=10**. `max` trên 47 đoạn có 4,7 lần nhiều cơ hội
ăn phải đỉnh giả ở văn bản sai so với `max` trên 10 đoạn ⇒ có khi `k` đang QUÁ CAO.
Đây cũng là lệch cấu hình duy nhất còn lại giữa ô đẹp nhất của dev (0.7467 @ N=3,k=10) và
thứ thực sự đã nộp — đúng quy tắc 4.

### ⛔ KHÔNG dựng được bài k=10 từ bộ điểm đã có — ô 1 đã cảnh báo, tôi vẫn đề xuất

`pick_chunks` có hai đường trả khác nhau:

```python
if len(parts) <= k: return list(parts)     # TRON van ban, THU TU VAN BAN
...                                        # len(parts) > k -> top-k BM25, THU TU DIEM
```

nên `v[:10]` chỉ bằng `pick_chunks(k=10)` ở cặp có `len(v)==50`. Đếm thật: **1448/3000
(48,3%) cặp suy được · 1552/3000 (51,7%) KHÔNG**. Bài nộp dựng bằng `max(v[:10])` trên cả
bộ là một cấu hình lai vô nghĩa, không đo được gì.

**Bài học quy trình (lần thứ hai trong hai ngày):** ô 1 của `public_ft_run.ipynb` có sẵn
comment nói đúng điều này. Tôi đề xuất thí nghiệm mà không đọc ô 1. Giống hệt vụ 07/09
đề xuất `headview_run` khi kết luận đã nằm trong file. **Đọc mã của lượt chạy trước khi
đề xuất thí nghiệm về lượt chạy đó.**

### 📐 TRẦN ĐO ĐƯỢC (`k_tran.py`, CPU, vài giây)

Trên 1448 cặp suy được, đoạn thắng nằm ở hạng BM25 nào:

| | tỉ lệ |
|---|---|
| trong top-10 BM25 | **83,4%** |
| trong top-20 | 91,0% |
| trong top-35 | 96,9% |

Nhưng đổi điểm max **rất ít khi đổi lựa chọn văn bản** — trên 235 câu có cả 3 vb suy được:

| hạ k từ 50 xuống | số câu đổi | quy ra 1000 câu |
|---|---|---|
| k=35 | 2/235 | ~9 |
| **k=20** | **4/235** | **~17** |
| k=10 | 20/235 | ~85 |

⇒ `k=20` vs `k=50` đáng **~17 câu/1000 = 1,7 điểm trần**, dưới sàn nhiễu LB 1,45 và đó là
số câu ĐỔI, không phải NET. Cộng thêm trục k **đơn điệu TĂNG** trên dev300 (k=1 0.6667 →
k=10 0.7467), tức bằng chứng chỉ hướng "k cao hơn thì tốt hơn", ngược giả thuyết.
**Kỳ vọng ròng ≈ 0. ĐÓNG TRỤC k. Không chấm lại dev300, không nộp.**

### 🔎 Phụ phẩm: xác nhận lại tín hiệu `enrich_front` bằng đường độc lập
1264 cặp trọn văn bản, vị trí tương đối của đoạn thắng: trung bình **0,383** · nằm ở 20%
đầu văn bản **33,4%** (nếu đều thì phải là 20%) ⇒ đoạn đầu văn bản được chọn **1,67 lần**
nhiều hơn mức ngẫu nhiên. Khớp `front` vs `back` (+5,33, p=0.0195) của 07/09. Không mở lại
hướng head — `ce_deep` đã bao trùm nó — chỉ ghi là phép kiểm nhất quán.

## 10-09 · Tập huấn luyện âm hạng 2–10 ĐÃ XONG. Và một nhãn tự mâu thuẫn chưa ai thấy.

`build_trainset_hard.py` viết từ 08/09 nhưng **chỉ chạy được 1193/5521 nhóm rồi ngắt, và
chưa bao giờ được train** (`finetune_listwise_run.ipynb` đang trỏ `trainset_listwise_v2.jsonl`).
Đã build nốt: **5521 nhóm**, khớp đúng số nhóm của bộ dễ.

| | nhóm | dải hạng của âm |
|---|---|---|
| `trainset_listwise_v2.jsonl` (đang dùng) | 5521 | 10–20 |
| `trainset_listwise_hard.jsonl` | 5521 | **2–10** |

Kiểm ruột: cùng tập qid · cùng nhãn dương 5521/5521 · 4 âm/nhóm · **0% nhóm có âm trùng
hoàn toàn với bản dễ** ⇒ phép so ghép cặp sạch, chỉ đổi một biến.

### 🟥 PHÁT HIỆN: 13 nhóm có đoạn dương TRÙNG Y HỆT một đoạn âm

Văn bản pháp luật sao chép nguyên điều/khoản sang văn bản khác, nên hai `doc_id` khác nhau
có thể chứa cùng một đoạn 1800 ký tự. Softmax listwise khi đó bị bảo *"đẩy chuỗi X lên và
đẩy chuỗi X xuống"* — gradient tự triệt tiêu, nhãn tự mâu thuẫn.

| | số nhóm rò rỉ |
|---|---|
| bộ dễ (hạng 10–20) | **1** |
| bộ khó (hạng 2–10) | **13** |

Gấp 13 lần, đúng như dự đoán: càng gần hạng 1 càng nhiều văn bản trùng ruột. Đây là dạng
cực đoan nhất của chẩn đoán 19/08 *"top-20 đầy văn bản trả lời được mà không được gán nhãn"* —
lần này không phải "trả lời được", mà là **cùng một chữ**.

- đã thêm guard `if ck[pos] in [ck[d] for d in negs]: continue` vào **cả hai** script build
- đã lọc sẵn `trainset_listwise_v2_clean.jsonl` và `trainset_listwise_hard_clean.jsonl`
  — **5507 nhóm mỗi bên**, bỏ hợp của 14 qid rò rỉ để hai bộ vẫn ghép cặp được

⚠️ Bài đã nộp 0,711 huấn luyện trên bản **chưa lọc** (`trainset_listwise_v2.jsonl`, md5
`492b6ae6b654`). Đừng sửa lại lịch sử — bản `_clean` là để dùng cho lượt sau.

### 🎯 VIỆC GPU TIẾP THEO (45 phút): train trên `trainset_listwise_hard_clean.jsonl`
Lý do: 50% câu sai có gold ở **hạng 2**, 67% ở hạng 2–3, nhưng mô hình đang được dạy trên
âm hạng 10–20 — **một biên quyết định nó không bao giờ phải đối mặt**. Kiểm tra nội bộ
TRƯỚC huấn luyện trên bộ dễ đã là 0,83 = bài quá dễ.

**Ngưỡng khoá TRƯỚC khi chạy:** đo trên dev300 bằng đúng lưới `richharness` của bản FT hiện
tại. Nhận nếu **thắng bản FT hiện tại ở ≥ 15/20 ô** VÀ McNemar tại N=3,k=10 cho p<0.05.
Không đạt ⇒ đóng, không nộp. Chỉ đổi MỘT biến: giữ nguyên loss, LR, EPOCHS, HOLDOUT.

### 📌 `margin` — hai nghĩa, đừng trộn vào cùng một lượt
1. **margin = chênh điểm hạng 1 − hạng 2.** Đã đo (mục "Độ tin cậy phân tách"): ngũ phân vị
   thấp nhất đúng 0.600, cao nhất 0.917. Đây là thước LỌC câu cần can thiệp, và ngưỡng hoà
   vốn 70,1% của bộ phân xử cặp tính trên đúng dải này.
2. **margin trong hàm mất mát.** Hiện đang là `Fn.cross_entropy(logits, zeros)` — softmax
   listwise thuần: một khi dương đã thắng rõ thì **gradient gần như tắt**, không đẩy tiếp cho
   khoảng cách rộng ra. Hinge/RankNet `max(0, m − (s⁺ − s⁻))` thì chỉ tắt khi khoảng cách đạt
   `m`, nên dồn toàn bộ sức học vào các cặp sát nhau = đúng dải (1) = đúng 67% số câu sai.

**Nhưng (2) và "âm hạng 2–10" tấn công CÙNG một chỗ (quy tắc 7), và làm chung là đổi hai
biến cùng lúc (quy tắc 3).** Thứ tự: âm hạng 2–10 trước (rẻ hơn, dữ liệu đã có, lập luận đã
viết trong docstring), margin loss chỉ chạy nếu lượt đầu ăn.

## 10-09 · GÓI TÁI LẬP: XONG. Dựng trên `repo_github` đã có, không làm lại từ đầu.

`repo_github` (commit `b1a3bf8`, 30/08) đã có README/LICENSE/requirements/notebooks/results
nhưng **đóng băng ở thời recall 0.9124** — không có gì về đổi độ đo, nộp 1 id, hay fine-tune.

Đã thêm:

| | |
|---|---|
| **`REPRODUCE.md`** (218 dòng) | đường chạy 5 bước cho bài 0,711, kèm md5 mọi tạo phẩm, tham số phải đặt tay, 3 cổng kiểm và lý do, **và mục "những chỗ KHÔNG tái lập được"** |
| `src/` +4 | `build_trainset.py` · `build_trainset_hard.py` · `dev1000_doc.py` · `k_tran.py` |
| `notebooks/` +4 | `finetune_listwise_run` · `public_ft_run` · `richharness_run` · `headview_run` |
| `README.md` | vá 3 chỗ: khối cảnh báo độ đo ở đầu, dòng LB, bảng điểm vào chính |

Đã kiểm: `deep_chunk.py`/`rerank.py`/`metrics.py`/`make_candidates_fallback.py` trong repo
**khớp md5** với bản gốc ở thư mục làm việc — repo không bị trôi.
`k_tran.py` nay nhận tham số thư mục dự án (`python src/k_tran.py <duong-dan>`), thiếu file
thì dừng bằng thông báo rõ chứ không traceback. Đã chạy thử từ trong repo: qua đủ 5 cửa.

### 🔴 LỖ TÁI LẬP PHẢI GHI VÀO BÁO CÁO BTC
`finetune_listwise_run.ipynb` seed thứ tự dữ liệu (`random.Random(0).shuffle`) nhưng **không
seed torch/CUDA**. Huấn luyện lại bước 4 ra một mô hình KHÁC. Hiệu ứng FT chỉ +0,9 điểm với
sai số lớn hơn thế ⇒ lượt train lại có thể trả về 0,705 hoặc 0,715 mà không có gì sai.
**Thêm vào ô 1 cho mọi lượt sau:**

```python
torch.manual_seed(0); torch.cuda.manual_seed_all(0); random.seed(0); np.random.seed(0)
torch.use_deterministic_algorithms(True, warn_only=True)
```

### ⚠️ `repo_github/.git` có `index.lock` + `HEAD.lock` bỏ lại từ một lệnh git chết giữa đường
Chưa commit gì (chờ Khim). Xoá hai file lock đó trước khi commit, nếu không git sẽ báo repo đang bị khoá.

## 10-09 · CE_BM25CAT (Askari, ECIR 2023) — ĐO TRẦN XONG. **KHÔNG KHẢ THI Ở ĐÂY.** Đừng chạy.

Bài báo: [arXiv 2301.09728](https://arxiv.org/abs/2301.09728). Nhét điểm tầng 1 vào **input dưới dạng
text** rồi fine-tune: `[CLS] query [SEP] <điểm> [SEP] passage [SEP]`. Biểu diễn tốt nhất là
min-max **toàn cục** → số nguyên (0–196) → chuỗi. Kết quả MSMARCO: BERT-Base nDCG@10
.399 → **.422**, và **thắng hẳn interpolation (.422 vs .353)**. Bốn model: BERT-Base/Large,
DistilBERT, MiniLM. **Bắt buộc fine-tune với điểm có mặt lúc train.** 0 tham số mới.

### Vì sao ĐÁNG đọc: nó không bị phép cộng RRF đã đóng của nhóm phủ định
Nhóm đã đóng hướng *"cộng λ·RRF vào điểm CE"* (LB −0,9). Đó là **late fusion**. Bài báo
chính là lập luận rằng late fusion yếu và **early fusion (nhét text) mạnh hơn nhiều** —
.353 vs .422 trên đúng phép so đó. Nên kết quả âm của nhóm KHÔNG phải bằng chứng chống
lại bài báo. Đây là lý do phải đo chứ không được bác bỏ bằng trực giác.

### ⛔ NHƯNG cơ chế mà bài báo dựa vào KHÔNG CÓ trong dữ liệu của nhóm

`bm25cat_tran.py` (CPU, dev300, guard dựng lại đúng mốc 0.7100 trước khi đọc số).
Trường `bm25` trong `scores_dev300_fusion_M20_K20.json` chính là điểm rổ hoà RRF.

**① Phân giải KHÔNG phải vấn đề** (giả thuyết của tôi sai): sau min-max toàn cục → int
0..196, hạng 1 và hạng 2 nhận cùng một số nguyên ở **chỉ 13/300 = 4,3%** câu.

**② Nhưng sức phân giải ở ĐÚNG CHỖ CẦN thì bằng tung xu:**

| tập | điểm tầng 1 trỏ đúng ứng viên |
|---|---|
| **cứu được (41 câu, gold ở hạng 2)** | **22/41 = 53,7%** |
| đang đúng (213 câu, gold ở hạng 1) | 183/213 = 85,9% |

Điểm tầng 1 **đồng ý với CE ở nơi CE đã đúng** (không mua thêm gì) và **mù ở nơi CE sai**
(chỗ chứa toàn bộ dư địa). Đi theo nó trên top-2: cứu 22 · hỏng 24 · **NET −2 câu = −0,67 điểm.**

⚠️ **Bẫy tỉ lệ nền đã tránh được (quy tắc 3).** Đo thô ra "gold có điểm tầng 1 cao hơn ở
205/254 = 80,7%", nhìn như vượt xa ngưỡng hoà vốn 70,8%. **Sai.** 84% câu top-2 đã đúng sẵn
và điểm tầng 1 chỉ đang đồng ý với CE ở đó. Tách tỉ lệ nền ra thì còn 53,7%. Ngưỡng 70,8%
tính trên dải chênh thấp, không phải trên toàn top-2 — so hai số đó là so lệch mẫu.

**③ Dải margin thấp** (60% câu chênh CE nhỏ nhất): cứu 20 · hỏng 15 · NET **+5 câu = +1,67
điểm**, độ chính xác bộ phân xử **57,1%** — vẫn dưới hoà vốn 70,8%, và +1,67 nằm dưới sàn
nhiễu dev300. Trùng khít dấu vết của phép cộng RRF: dương yếu trên dev, âm trên LB.

**④ Trần tuyệt đối** (oracle chỉ dùng điểm tầng 1 khi nó giúp): **+22 câu = +7,33 điểm**
(0.7100 → 0.7833). Sàn (đi theo mù quáng): −0,67. Toàn bộ giá trị nằm ở việc mô hình **học
được KHI NÀO nên tin** — và bài báo học điều đó bằng **~1 triệu query MSMARCO**. Nhóm có
**5.507 nhóm**. Lệch **180 lần**.

### 🔩 Chi tiết kiến trúc làm hỏng phép áp dụng trực tiếp
Trong bài báo, điểm tầng 1 là một scalar **mỗi cặp (query, passage)** và passage **là đơn vị
xếp hạng**. Trong pipeline này đơn vị xếp hạng là **văn bản** còn đơn vị chấm là **đoạn**, nên
điểm muc văn bản sẽ **không đổi trên mọi đoạn của cùng một văn bản** ⇒ lượng thông tin
**y hệt** phép cộng RRF đã đóng, chỉ khác dạng hàm.

Biến thể thật sự mới: **BM25 theo từng đoạn** — `pick_chunks` đã tính rồi **ném đi**
(`score(i)` là closure, chỉ dùng để sort). Đo luôn (`bm25cat_tran.py --chunk`):

| | cứu được | đang đúng |
|---|---|---|
| BM25 max theo đoạn | 22/41 = 53,7% | **70/120 = 58,3%** |
| BM25 tb 3 đoạn cao nhất | 19/41 = 46,3% | 67/120 = 55,8% |
| *(điểm RRF mức văn bản)* | *53,7%* | *85,9%* |

**BM25 mức đoạn KÉM HƠN HẲN.** Nó bất đồng với CE ở gần một nửa số câu CE đang làm đúng ⇒
đi theo nó là phá hệ thống. Không mua thêm gì ở tập cứu được (vẫn 53,7% = tung xu).

### 🎯 KẾT LUẬN: ĐÓNG. Không tiêu GPU.
Ba lý do độc lập, mỗi lý do tự đủ:
1. Tín hiệu tầng 1 trỏ đúng **53,7%** trên đúng tập cần cứu = tung xu. Bài báo cần tín hiệu
   tầng 1 **bổ sung** cho CE; ở đây nó **dư thừa** nơi CE đúng và **mù** nơi CE sai.
2. Cần học "khi nào tin" từ ~1M query; nhóm có 5,5k. Lệch 180×.
3. Kiểu lỗi của nhóm là **thẩm quyền/phạm vi pháp lý** (ca `138214`: chọn QĐ UBND Hà Nội thay
   vì Nghị định toàn quốc — trùng chữ NHIỀU HƠN nhưng sai phạm vi). Nhét thêm một điểm **từ
   vựng** vào input là bơm thêm chính cái tín hiệu đã gây ra lỗi đó.

**Vẫn giữ được một thứ từ bài báo:** biểu diễn min-max **toàn cục → số nguyên → chuỗi** thắng
float thô và min-max cục bộ (bảng 1). Nếu sau này có hướng nào cần nhét scalar vào input thì
dùng đúng biểu diễn đó, đừng dò lại.

## 10-09 · Đọc 2 nguồn nữa: NOWJ@COLIEE 2026 + ZeroEntropy. Không có cần gạt mới, nhưng bộ phân xử cặp có công thức.

**NOWJ@COLIEE 2026** ([arXiv 2607.16603](https://arxiv.org/html/2607.16603)) — 5 task COLIEE, Task 1 truy hồi án lệ Canada.
- ✅ **Xác nhận độc lập hướng đã đóng:** *"fine-tuned generative rerankers (Qwen3-4B/8B) underperformed
  hand-crafted feature-based MLP"* — khớp kết quả 07/09 của nhóm (8B mua recall, không mua precision).
- ❌ **Cutoff thích nghi mỗi câu** (XGBoost đoán trả bao nhiêu văn bản): vô dụng ở đây, số id đã chốt = 1.
- 🟡 **MLP phân xử cặp trên đặc trưng thủ công** (cosine + BM25 + rank + metadata), hard negative từ top-200.
  Đây là bản RẺ NHẤT của bộ phân xử cặp — CPU, 0 GPU, 0 tham số. **Nhưng gần hết đặc trưng đã đo chết
  riêng lẻ:** BM25/RRF = 53,7% trên tập cứu được (mục CE_BM25CAT) · năm ban hành = 2,0% ≈ ngẫu nhiên ·
  loại/thẩm quyền văn bản = âm. Đặc trưng DUY NHẤT chưa dùng là **chênh điểm hạng 1−hạng 2** (0.600→0.917
  theo ngũ phân vị). Quy tắc 7: đừng kỳ vọng chúng cộng dồn.
- Task 3 tăng 89%→95% bằng QRHead nhưng kho chỉ ~800 điều Bộ luật Dân sự Nhật, và cần LLM decoder → quá ngân sách 3B.

**ZeroEntropy** — đối chứng 17 benchmark: cross-encoder chuyên dụng **thắng mọi LLM reranker**
(nDCG@10 0.777 vs GPT-5-mini 0.698 · Cohere 0.719), nhanh hơn 17×, rẻ hơn 10×. Pointwise LLM
"uncalibrated", listwise LLM chỉ khả thi ở top 5–10. ⇒ **Xác nhận giữ CE 0,568B là đúng, và
"fine-tune LLM cho việc xếp hạng" chính là đang làm reranker — nhóm đã làm rồi (FT listwise).**

### 🎯 Thứ DUY NHẤT lấy được: công thức cho bộ phân xử cặp
`zerank-1` bỏ điểm tuyệt đối pointwise, thay bằng **sở thích theo cặp** → huấn luyện một **comparator
nhỏ** → gộp nhiều lượt đối đầu thành một thang toàn cục bằng **mô hình kiểu Elo**, kèm học **độ lệch
riêng theo từng câu**. Đây đúng là thứ nhóm còn thiếu: hoà vốn 70,1%, trần +13,7 điểm, và trước giờ
chưa có cách GỘP các phán quyết cặp thành thứ hạng. Elo trả lời phần đó.
⚠️ Vẫn là hướng SAU `trainset_listwise_hard_clean`. Và nhớ: comparator phải **học trong miền** —
bằng chứng là FT listwise đã lật dấu từ âm sang dương ở đúng model đó.

## 10-09 · THỨ BẬC / PHẠM VI PHÁP LÝ: ĐÓNG. Ca `138214` là giai thoại, không phải quy luật.

`phamvi_tran.py` (CPU, dev300, guard dựng lại 0.7100). Suy thứ bậc từ `slug` trong
`vanban_meta.json` — phủ độ **90,7%** văn bản trong top-2, nên phép đo đủ tin.

| đặc trưng | cứu được (41 câu) | đang đúng (213) | NET nếu đi theo |
|---|---|---|---|
| **[A] thứ bậc loại vb** (Luật>NĐ>TT>QĐ) | 12/41 = **29,3%** | 63/213 = 29,6% | **−51 câu = −17,00 điểm** |
| [B] không phải vb địa phương | 2/41 = 4,9% (hoà **39**) | 0/213 (hoà 212) | +1 câu = +0,33 |
| [C] thứ bậc, chỉ khi một bên là địa phương | 29,3% | 29,6% | −17,00 |

**[A] không phải yếu — nó ÂM MẠNH và ngược dấu:** gold thường là văn bản bậc **THẤP hơn**.
Hợp lý — câu trả lời cụ thể nằm ở Thông tư/Quyết định hướng dẫn, không nằm ở Luật khung.
Đây là **prior toàn cục**, và CE đã xử lý nó rồi (29,6% ở tập đang đúng = cùng phân bố).

**[B] trục địa phương gần như RỖNG:** `dp=True` chỉ **98/5244** văn bản (1,9%), và trên 41 câu
cứu được thì **39/41 hoà** (cả hai ứng viên đều không phải vb địa phương).

Phân bố thứ bậc gold vs ứng viên sai (tập cứu được) — **không tách được**:
bộ luật 11/9 · nghị định 10/12 · thông tư liên tịch 11/7 · quyết định 6/5 · không rõ 2/6.

### 🎯 Hệ quả
- **Ca `138214` (QĐ UBND Hà Nội thay vì Nghị định toàn quốc) là giai thoại.** Log 19/08 đã tự
  cảnh báo: *"Mới đọc 2/13 ca — giả thuyết có ví dụ, chưa phải số liệu."* Nay có số liệu: không
  phải quy luật. **Đừng viết vào báo cáo như một phát hiện.**
- Đóng luôn hướng **BGE-M3 multi-vector / ColBERT MaxSim** theo ngưỡng đặt trước (>70,8% mới mở):
  MaxSim chỉ được đề xuất như cách **mở rộng tín hiệu phạm vi**, mà tín hiệu đó nay đo được là
  **không tồn tại**. Còn sót một biến thể CHƯA đo: MaxSim như **độ che phủ token tổng quát**
  (không riêng token phạm vi) — nhưng nó không còn động lực nào đo được, nên xuống cuối hàng đợi.
- Xác nhận quy tắc 5 lần thứ n: ưu thế **toàn cục** không thắng nổi bộ chấm. Và lần này nó còn
  không sống nổi cả ở dạng **có điều kiện** trên đúng quyết định hạng 1 vs hạng 2.

### ✅ Thứ giữ lại được cho BÁO CÁO (không phải cần gạt)
Gold lệch về văn bản **bậc thấp** (Thông tư/Quyết định hướng dẫn) chứ không phải Luật/Bộ luật.
Đó là đặc trưng của bộ đề: câu hỏi đời thường cần **quy định thi hành cụ thể**, không cần
văn bản khung. Dùng để giải thích vì sao mọi mẹo "ưu tiên văn bản có thẩm quyền cao" đều âm.

## 10-09 · Lượt train âm hạng 2–10: **BỊ DỪNG OAN Ở BƯỚC 500.** Guard sai, không phải model sai.

Guard vân tay qua đúng (md5 `f51f73ef`, 5507 nhóm → 5107 train / 400 val).

### 🔴 LỖI GUARD — `d<0.02` gate bằng LOSS là sai ở mốc 500 bước
```
>>> CHOT 500 BUOC: loss giam -0.1208 · kiem tra 0.7650
!!! LOSS KHONG GIAM -> DUNG, dung ngoi cho het epoch.
```
Chỉ chạy **500/5107 bước** (~5 phút) rồi tự dừng.

**Vì sao guard sai:** `ACC=16` ⇒ 500 bước batch = **~31 bước tối ưu**. `OneCycleLR(pct_start=0.1)`
trên `total_steps = 5107//16+1 = 320` ⇒ **warmup = 32 bước tối ưu = 512 bước batch**.
Tức cửa sổ đo loss nằm **TRỌN trong warmup**: 100 bước đầu chạy ở LR≈0 (model gần như không
đổi), 100 bước cuối ở LR≈max. **Loss tăng ở đó là đúng theo thiết kế.**

**Bằng chứng model đang học tốt trong đúng 500 bước đó:**
- val acc **0.7300 → 0.7650** (+3,5 điểm)
- val acc trước huấn luyện trên bộ **khó** là 0.7300 vs bộ **dễ** 0.8300 ⇒ **thiết kế âm hạng
  2–10 đã đạt mục tiêu: bài khó hơn thật.**

### 📊 Số dev300 của bản 500-bước (chưa train xong, đừng đọc như kết quả)
| | harness 3 đoạn |
|---|---|
| mô hình GỐC (đối chứng) | 0.6667 |
| mô hình FT-hard | **0.6933 (+2,67)** |
| McNemar | thắng 12 thua 4, **p=0.0768** |

⚠️ **NGƯỠNG KHOÁ CHƯA ĐƯỢC KIỂM.** Ngưỡng là *"thắng bản FT hiện tại ≥15/20 ô lưới
richharness VÀ McNemar N=3,k=10 p<0.05"*. Lượt này so với **GỐC**, không so với **FT-easy**,
và **không chạy lưới richharness**. Con số 0.6933 trên harness 3 đoạn **không so được** với
0.7100 (sản xuất, 2 góc nhìn/50 đoạn) — khác harness.

### ✅ ĐÃ SỬA: gate bằng **val acc**, không bằng loss
`if v5 <= v0: break` thay cho `if d<0.02: break`. Chạy lại hết epoch **~48 phút**.
Đây là quy tắc 2 ở dạng khác: **cổng đặt trước phải đo đúng thứ mình quan tâm.** Một cổng
đo sai thứ còn tệ hơn không có cổng — nó giết lượt chạy đang tốt và làm tưởng hướng đã chết.

## 11-09 · FT âm hạng 2–10 chạy HẾT EPOCH. Train ăn rõ. Chẩn đoán guard được xác nhận.

Chạy lại sau khi vá guard (gate bằng val acc thay vì loss): **5107/5107 bước, 47 phút.**

| | lần 500 bước (dừng oan) | hết epoch |
|---|---|---|
| val acc | 0.7300 → 0.7675 | 0.7300 → **0.8150** |
| dev300 harness 3 đoạn, GỐC 0.6667 | 0.6933 (+2,67) p=0.0768 | **0.7167 (+5,00)** thắng 25 thua 10 **p=0.0167** |

**Chẩn đoán guard ĐÚNG:** loss trong warmup 1.0–1.25, sau warmup tụt xuống **0.41–0.63** và giữ
ở đó tới hết epoch. Cửa sổ `[100 đầu] − [100 cuối]` ở bước 500 đo trọn trong warmup nên vô nghĩa.
Nếu tin guant cũ thì đã đóng một hướng đang ăn điểm. **Cổng đo sai thứ còn tệ hơn không có cổng.**

Checkpoint: `/kaggle/working/ft_listwise` (val 0.8150). Phải tải về trước khi đóng phiên.

### ⚠️ SỬA QUY CÁCH NGƯỠNG — làm TRƯỚC khi chạy richharness, không phải sau khi thấy số
Ngưỡng cũ ghi *"≥15/20 ô"*. **Sai quy cách:** `richharness_run.ipynb` hiện dùng
`NS=(3,5,10) × KS=(1,3,5,10)` = **12 ô**, không phải 20. (Bảng 4×5 trong mục 08/09 là bảng
N×k của lượt cũ, không phải lưới notebook.) Giữ nguyên tỉ lệ 15/20 = 75% ⇒ **≥9/12 ô**.

### 🔒 NGƯỠNG KHOÁ (bản sửa quy cách, chưa xem số nào của FT-hard)
So với **FT-easy** (bản đang nộp 0,711), giá trị lấy từ bảng N×k mục 08/09:

| | k=1 | k=3 | k=5 | k=10 |
|---|---|---|---|---|
| N=3 | 0.6667 | 0.7300 | 0.7300 | **0.7467** |
| N=5 | 0.6633 | 0.7100 | 0.7200 | 0.7367 |
| N=10 | 0.6567 | 0.7133 | 0.7233 | **0.7433** |

**NHẬN nếu ĐỒNG THỜI:**
1. FT-hard vượt FT-easy ở **≥ 9/12 ô** của lưới trên.
2. Tại **N=10, k=10** (ô notebook tự in McNemar): FT-hard > **0.7433** VÀ McNemar so với sản
   xuất 0.7100 đạt **p<0.05**. (FT-easy ở ô này đạt 0.7433, thắng 26 thua 10, p=0.0113 —
   nên đây là bar NGANG BẰNG, không nới lỏng.)

**KHÔNG ĐẠT ⇒ ĐÓNG, giữ nguyên bài 0,711, không nộp.** Không được đổi ngưỡng sau khi thấy số.

⚠️ Nhắc: 0.7167 của harness 3 đoạn **KHÔNG so được** với 0.7100 sản xuất (2 góc nhìn / 50 đoạn)
— khác harness. Chỉ lưới richharness mới cho phép so.

## 11-09 · FT âm hạng 2–10: **NGƯỠNG KHÔNG ĐẠT. ĐÓNG.** Giữ nguyên bài 0,711.

Lưới richharness chạy xong (25 phút, có đối chứng GỐC cùng harness).

**Harness tự kiểm QUA:** GỐC tại N=3,k=10 = **0.6933** · N=10,k=10 = **0.6900** — khớp **đúng**
bảng 08/09 (0.7100 −1,67 và −2,00). Nên phép so với FT-easy tin được.

### Δ của FT-hard so với FT-easy, 12 ô
| | k=1 | k=3 | k=5 | k=10 |
|---|---|---|---|---|
| N=3 | −0.0034 | −0.0033 | −0.0100 | **0** |
| N=5 | −0.0100 | +0.0033 | +0.0067 | +0.0066 |
| N=10 | **0** | **0** | +0.0067 | **0** |

**Thắng 4 · thua 4 · hoà 4.** Cần ≥9/12 ⇒ **TRƯỢT.** Lệch lớn nhất ±0,01 = ±3 câu/300.
Điều kiện 2 cũng trượt: N=10,k=10 ra **0.7433 = BẰNG ĐÚNG** FT-easy (cần vượt), và McNemar so
sản xuất **p=0.1934** so với FT-easy **p=0.0113** ⇒ FT-hard còn **kém hơn về ý nghĩa**.

⚠️ **Notebook tự in "TANG +0.0333 -> CHAY PUBLIC roi NOP" — KHÔNG ĐƯỢC THEO.** Nó so với
**sản xuất 0.7100** vì viết từ thời chưa có FT-easy. Baseline đúng là **FT-easy 0,711**.
Đúng cái bẫy mà ngưỡng khoá-trước được dựng ra để chặn. Ghi lại: **mọi ngưỡng in sẵn trong
notebook phải được đối chiếu lại với bài ĐANG NỘP, không phải với mốc lúc notebook được viết.**

**Kết luận cơ chế:** dải âm 10–20 vs 2–10 **không phân biệt được**. Giả thuyết "âm đặt ở sai
biên quyết định" đã trả lời: **không phải nút thắt.** Val acc nội bộ tăng đẹp (0.7300→0.8150)
nhưng **không chuyển thành điểm** — lần thứ ba val nội bộ nói dương mà thước thật nói không.

## 11-09 · TRẦN HƯỚNG "KHỚP PHẠM VI" TRÊN dev1000: **1,60 điểm. ĐÓNG.**

Không cần GPU — câu hỏi trần là thuộc tính của dữ liệu, không của model. Dùng rổ
`fusion_rrf_top50_dev_1000_matchEmbedded.json` + `vanban_meta.json`, 1000 câu có nhãn.

| | dev1000 |
|---|---|
| vb cấp địa phương trong kho | 98/5244 = 1,9% |
| câu có ≥1 vb địa phương trong top-5 của rổ | 40/1000 = 4,0% |
| câu mà **gold** là vb địa phương | 3/1000 = 0,3% |
| **TRẦN: gold trung ương, có vb địa phương xếp TRÊN gold** | **16/1000 = 1,60 điểm** |

**Đóng vì ba lý do:**
1. **1,60 < 2,00 điểm** ⇒ trượt quy tắc 8 (chỉ chạy thí nghiệm kỳ vọng ≥2 điểm).
2. **1,60 ≈ sàn nhiễu LB 1,45** ⇒ kể cả nếu đúng cũng **không đo được trên bảng.**
3. Con số 16 là **trần rất rộng rãi**: nó đếm mọi ca vb địa phương xếp trên gold ở BẤT KỲ đâu
   trong rổ RRF, trong khi bộ chấm CE đã xếp lại rồi. Trên dev300 ở đúng điểm hoạt động sản
   xuất, đặc trưng này chỉ **nói được gì ở 2/41 ca** — quy ra dev1000 là ~6 ca, không phải 16.

⇒ Cổng của Khim ("dưới 8–10 ca thì đóng") **đạt trên giấy nhưng trượt khi tính đúng điểm hoạt
động.** Ghi lại con số 16 để không ai mở lại hướng này.

## 11-09 · BỘ PHÂN XỬ CẶP: đã dựng xong dữ liệu. Ngưỡng khoá trước khi chạy.

Bộ chấm hiện tại chấm **từng cặp (câu hỏi, văn bản) độc lập** — nó chưa bao giờ nhìn hai ứng
viên cạnh nhau. Bộ phân xử nhìn cả hai rồi trả lời "cái nào đúng hơn".

```
input : [CLS] cau hoi [SEP] van ban A [SEP] van ban B [SEP]
nhan  : 1 neu A la gold · mat mat BCE
```

### Dữ liệu — 0 GPU, suy từ tập đã có, không cắt đoạn lại
| file | nội dung |
|---|---|
| `pairset_hard.jsonl` | **22.028 cặp** huấn luyện, suy từ `trainset_listwise_hard_clean` (4 cặp/nhóm) |
| `pairset_dev300.jsonl` | **254 cặp** đánh giá = đúng cặp (hạng 1, hạng 2) mà nó phải quyết |

- **Đảo thứ tự ngẫu nhiên:** tỉ lệ nhãn=1 là **0,498**. Không đảo thì model học "luôn chọn A" —
  thiên lệch vị trí là lỗi kinh điển của bộ phân xử cặp.
- **Lúc suy luận phải chấm CẢ HAI CHIỀU rồi lấy trung bình**, cùng lý do.
- Input dài tối đa **3.817 ký tự** ⇒ cần **MAXLEN ≥ 1536** (hiện đang 1024). VRAM còn 10,3 GB nên đủ.

### Cửa kiểm: tập đánh giá tái tạo ĐÚNG số hoà vốn đã ghi
`65 cặp · 46 đang đúng · 19 cứu được · hoà vốn 70,8%` — khớp log 07/09. Tin được.

| dải margin | số cặp | đang đúng | cứu được | hoà vốn |
|---|---|---|---|---|
| **< 0,005** | **65** | 46 | 19 | **70,8%** |
| < 0,02 | 94 | 70 | 24 | 74,5% |
| < 0,10 | 134 | 101 | 33 | 75,4% |

**Hoà vốn TĂNG khi dải rộng ra** ⇒ chỉ can thiệp ở dải hẹp nhất. Đánh giá trên dải < 0,005.

### 🔒 NGƯỠNG KHOÁ (đặt trước, chưa chạy gì)
Hoà vốn là 70,8%, nhưng **n=65 quá nhỏ** — sai số chuẩn ±5,7 điểm. Đúng 71% không phân biệt
được với 70,8%. Để vượt hoà vốn **có ý nghĩa** (1 phía, p<0,05):

> **NHẬN nếu bộ phân xử đúng ≥ 53/65 = 81,5%** trên dải margin < 0,005 của dev300.
> Dưới ⇒ **ĐÓNG, không chạy đề thi, không nộp.**

Chấm cả hai chiều (A,B) và (B,A) rồi lấy trung bình trước khi quyết.

### Dư địa
| | dev300 |
|---|---|
| trần nếu phân xử **hoàn hảo** dải < 0,005 | 46 → 65 = **+19 câu = +6,3 điểm** |
| thực tế nếu đạt đúng ngưỡng 81,5% | 46 → 53 = **+7 câu = +2,3 điểm** |

**+2,3 điểm là con số sống lớn nhất còn lại của dự án** (trên sàn nhiễu LB 1,45).
Chi phí: ~45 phút train + ~10 phút chấm 254 cặp × 2 chiều.

## 11-09 · Bộ phân xử cặp, lượt 1: **KHÔNG HỢP LỆ.** Không phải kết quả âm. Đã vá 2 lỗi.

Ô 3 in `KHONG DAT (39/65 = 60,0%)`. **Đừng đọc số đó.** Lượt chạy bị hỏng vì hai lỗi trong
notebook của tôi, cả hai đều nhìn thấy được từ chính log.

### 🔴 LỖI 1 — dùng lại đầu phân loại cũ (lỗi thiết kế, nghiêm trọng hơn)
`AITeamVN/Vietnamese_Reranker` **đã có sẵn** đầu `num_labels=1`, nhưng đó là đầu chấm
*"đoạn này có liên quan tới câu hỏi không"*, xuất logit biên độ ±10. Nhiệm vụ mới là
*"A hay B đúng hơn"* — **không gian ngữ nghĩa khác hẳn**.

Bằng chứng trong log: **loss khởi đầu 2,57 và 2,36**, trong khi BCE ở điểm trung tính
(logit=0) là `ln2 = 0,693`. **Gấp 3,7 lần.** Model phải **bỏ học** thang đo cũ trước khi học
được việc mới — mà nó chỉ được chạy 2,4% của một epoch.

⇒ Đã thêm: reset đầu phân loại (`normal_(0, 0.02)`, bias=0) + `assert |logit| < 2.0` ở bước đầu.

### 🔴 LỖI 2 — gate đặt trong warmup. **LẦN THỨ HAI.**
| | 09/09 (FT hard) | 11/09 (phân xử cặp) |
|---|---|---|
| gate | bằng **loss** ở bước 500 | bằng **val acc** ở bước 500 |
| warmup | 512 bước batch | **2.112 bước batch** |
| bước 500 nằm ở | ~98% warmup | **24% warmup** |
| hệ quả | dừng oan, phải chạy lại | dừng oan, phải chạy lại |

Hôm 09/09 tôi vá bằng cách đổi *thứ được đo* (loss → val acc) nhưng **không sửa VỊ TRÍ gate**.
Số bước warmup thay đổi theo kích thước tập (`total_steps//ACC × pct_start`), nên mọi mốc
**cố định** đều sai ở tập khác.

⇒ Đã sửa đúng gốc: `WARM_B = (total//ACC+1)*0.1*ACC` rồi `GATE = min(1.5*WARM_B, total//3)`.
**Không bao giờ đặt mốc gate bằng con số cố định nữa.**

### 📌 Quy tắc 11 (mới)
> **Cổng đặt trước phải neo vào LỊCH HỌC, không vào số bước tuyệt đối.** Và khi đổi nhiệm vụ
> (pointwise → listwise → pairwise) thì **đầu phân loại của model nền là tạ, không phải điểm
> khởi đầu** — kiểm loss ở bước 1 so với giá trị lý thuyết trước khi để nó chạy hết epoch.

### Chi phí lượt hỏng: ~5 phút GPU. Ngưỡng khoá GIỮ NGUYÊN: ≥ 53/65 = 81,5%.

## 12-09 · 🔴 BỘ PHÂN XỬ CẶP TRÊN LB: **0,688.** Âm 1,4 điểm so bài nền. ĐÓNG.

`sub_JUDGE_band005.zip` → **precision 0,688 · recall 0,657167**. Dự kiến 0,725–0,732.
So bài nền 0,702 ⇒ **−1,4 điểm = −14 câu/1000.** So bài đang nộp 0,711 ⇒ −2,3 điểm.
109 câu đổi ⇒ độ chính xác các lần đổi chỉ **~40%**, so với **65%** (15/23) trên dev300.
**→ Đã nộp lại `sub_FT_N3_k50.zip`.**

### ❌ Giả thuyết "lệch cấu hình dải margin K=20 vs K=50": BÁC BỎ
Đo trực tiếp, 0 GPU, trên cùng 1000 câu public (`scores_public_fusion_M20_K20_matchEmbedded`
vs `_K50_`):

| | ngưỡng 0,005 rơi vào phân vị |
|---|---|
| dev300 K=20 | 26,3% |
| public K=20 | 28,0% |
| public K=50 | 28,0% |

Dải trên public: K=20 (280 câu) ∩ K=50 (280 câu) = **277**, **Jaccard 0,98**, chỉ 3 câu khác.
**Dải được hiệu chuẩn ĐÚNG.** Không phải lỗi kỹ thuật.

### 🔬 Và cũng KHÔNG giải thích được bằng nhiễu
Dải public có ~230 câu gold ở top-2. Dự báo từ dev300: 163 → 187 = **+25 câu**.
Thực nhận **−14 câu**. Lệch **39 câu = 6,6 SE** (SE của số đếm ≈ 5,9).
Nhiễu phía public **không thể** tạo ra khoảng đó.
Chiều ngược: nếu độ chính xác thật chỉ ~60% thì quan sát ≥53/65 trên dev300 có p≈0,0003.

⇒ **Không có lời giải thích thoả đáng nào trong hai hướng thông thường.** Ghi lại là chưa giải
thích được, đừng ép vào một câu chuyện gọn gàng.

### 🎯 NHƯNG CÓ MỘT QUY LUẬT LỘ RA — 4 điểm dữ liệu, đây là thứ giá trị nhất rút ra được

| can thiệp | bản chất | dev300 | **LB thật** |
|---|---|---|---|
| cộng RRF | **phân xử top-2** | +0,6…+2,3 | **−0,9** |
| `replace` | **phân xử top-2** | −2,00 | **−3,1** |
| bộ phân xử cặp | **phân xử top-2** | **+2,33 (p<0,05)** | **−1,4** |
| FT listwise | **đổi hàm chấm** | +1,4…+1,9 | **+1,0** ✅ |

> **Mọi can thiệp vào QUYẾT ĐỊNH hạng 1 vs hạng 2 đều không chuyển được từ dev300.
> Can thiệp vào HÀM CHẤM thì chuyển được.**
> Ba lần trên ba lần. Kể cả khi vượt ngưỡng ý nghĩa đặt trước.

Cơ chế khả dĩ: dev300 nằm trong `train.json`, cùng quy trình gán nhãn với tập huấn luyện;
đề thi là tập riêng (`giao với train = 0`). Hàm chấm học đặc trưng ngữ nghĩa chung nên chuyển
được; bộ phân xử top-2 học vào đặc thù của cặp gần-hoà, và đặc thù đó **không chung** giữa hai
tập. Đây là **giả thuyết**, chưa có phép đo đứng sau.

### 📌 Quy tắc 12
> **dev300 KHÔNG dùng được để quyết định bất kỳ can thiệp nào chỉ tác động lên quyết định
> hạng 1 vs hạng 2.** Không phải vì cỡ mẫu — mà vì hiệu ứng không tồn tại ngoài dev300.
> Muốn thử loại can thiệp đó thì phải quyết bằng **1 lượt nộp**, không quyết bằng dev300.

### 🏁 TRẠNG THÁI: 0,711 · hạng 3/84 · đã chạm trần kiến trúc (ước 07/09: 0,71–0,72)
Không còn hướng nào có cơ chế đỡ lưng. 6 ngày, gói tái lập BTC **vẫn chưa commit**.
