# project_DSC — DSC2026 Task 1 (LegalIR)

## ▶️ 28/08 — **`fusion_k50_run.ipynb` — NÂNG `K` 20→50 TRÊN ĐỀ THI. VIỆC CHẠY TIẾP THEO.**

**Cần gạt DUY NHẤT còn trần dương vừa túi tiền.** Chạy thẳng đề thi, **không đo dev trước** —
dev300 mù dưới 2 điểm, mà trần của lượt này chỉ ~+0,3. LB mới cho số thật.

### Căn cứ (đo 28/08, CPU)

| | |
|---|---|
| đoạn tốt nhất nằm trong top-20 BM25 | **20/24 cặp** → `K=20` đã bắt **90%** giá trị oracle |
| 4 cặp hở, ở hạng | **23 · 23 · 50 · 109** → `K=50` bắt thêm **3/4** |
| khớp quét K 19/08 | +0,80 ở `K=120` |
| **trần ước** | **~+0,3 điểm dev — và đây là CHẶN TRÊN** (mẫu toàn câu đang sai) |

### Chi phí — ĐẾM THẬT trên 240 văn bản (12 câu × top-20)

| | |
|---|---|
| số đoạn/văn bản | trung vị **50** · TB 85,8 · max 1.469 |
| văn bản có >20 đoạn | **82,5%** → nâng K thật sự chạm được phần lớn |
| **chi phí `K=50` / `K=20`** | **2,03×** |
| → đề thi | 157.008 → **~318.000 đoạn ≈ 6,9h** |

### Ba thứ notebook làm khác `fusion_v3_run`

| # | sửa | vì sao |
|---|---|---|
| 1 | **tái dùng tầng 1 của lượt `K=20`**, bỏ `ce_deep` cũ | tầng 1 không phụ thuộc `K` → tiết kiệm ~2h. Nhưng `ce_deep` cũ chấm ở K=20, đổi K thì **không so được** (cảnh báo có sẵn trong `deepen_one`) |
| 2 | **`scores.update(...)` thay vì gán đè** | `deepen_all` CHỈ trả về câu được truyền vào — gán đè là **mất tầng 1 của các câu ngoài lát**. Bẫy này đã suýt dính khi dựng |
| 3 | **checkpoint mỗi 100 câu** + `QLAT` bỏ câu đã có `ce_deep` | lượt 6,9h không checkpoint mà chết ở giờ thứ 6 là mất trắng. Giờ chạy lại = chạy tiếp |

Thêm: `Q_TU, Q_DEN` để chia đôi lát câu hỏi nếu Bước 3 ước >6h muốn an toàn hơn; assert dừng
nếu ước >9,5h; và **không đóng gói bài nộp khi chưa đủ 1000 câu có `ce_deep`**.

### Upload lên dataset

⚠️ **`Ketqua_E/scores_public_fusion_M20_K20_matchEmbedded.json`** (4,1 MB) — nguồn tầng 1.
Không có nó thì notebook dừng ngay Bước 2 với assert. Mọi thứ khác đã có.

### Đọc kết quả

Sinh `submission_matchEmb_K50_n{0..4}.zip`. **Mốc phải vượt: 0.9118.** Nộp `n=3` trước
(đỉnh hiện tại), rồi `n=2`. Vượt → `K` là cần gạt còn sống, cân nhắc `K=80`. Không vượt →
**cần gạt cuối của E đã đóng**, dồn toàn bộ vào báo cáo.

## 💰 28/08 — **ĐỊNH GIÁ TRỌN MỌI CẦN GẠT CÒN LẠI. TẤT CẢ BẰNG SỐ ĐO, 0 GIỜ GPU.**

Khim đổi mục tiêu: **tối đa điểm public, tăng ít cũng lấy** (phải lọt top mới vào private).
Dưới đây là toàn bộ lựa chọn còn lại, đã định giá — không cái nào là phỏng đoán.

### ⛔ `M=30` — **TRẦN ≈ 0. ĐÓNG.**

Trong 13 câu còn sai, chỉ **3 câu** có gold ở hạng CE 21–30 (`1524`, `16942`, `37542`).
Đối chiếu `oracle13`: `1524` và `37542` nằm nhóm **oracle THẤP HƠN điểm hiện tại** → đọc sâu
làm tệ đi. Còn `16942` có **378 đoạn**, K=20 phủ 5%. → thực nhận ≈ 0,05 câu. **1,7h cho số 0.**

### 📏 CHỌN ĐOẠN — **BM25 CHỌN DỞ THẬT, NHƯNG `K=20` ĐÃ BÙ 90%**

Chấm lại toàn bộ đoạn của 24 cặp (câu, văn-bản-gold) từ `oracle_chunks_dev300.json` (7.362 cặp):

| | |
|---|---|
| BM25 `k=1` chọn trúng đoạn tốt nhất | **8/24** — điểm TB 0,191 vs oracle 0,503 |
| **nhưng đoạn tốt nhất nằm trong top-20 BM25** | **20/24** |
| **giá trị oracle mà `K=20` đã bắt được** | **90%** (0,451 / 0,503) |

→ **Bộ chọn đoạn kém ở `k=1` nhưng pipeline chạy `K=20`, nên gần như không mất gì.**
Cải tiến `pick_chunks` chỉ còn với tới ~10% của một rổ vốn đã nhỏ. **Gần cạn.**

4 cặp còn hở: `92466` (hạng 109), `65498` (50), `156454` (23), `65498` (23).
→ Nâng `K` 20→50 bắt được 3/4. Khớp phép quét K 19/08 (**+0,80 ở K=120**).

### 📋 BẢNG QUYẾT ĐỊNH CUỐI — mọi thứ E còn có thể làm

| cần gạt | trần dev | GPU | đánh giá |
|---|---|---|---|
| `M=30` | ~0 | 1,7h | **đóng** |
| `pick_chunks` tốt hơn | ~+0,05 | 0 | **đóng** — K=20 đã bù |
| **`K` 20→50** | **~+0,3** | **~8h** | cần gạt DUY NHẤT còn trần dương vừa túi |
| `K=120` | +0,80 | ~20h | **vượt trần 12h/lượt** |
| đầu học lại (probe) | +0,67 (tầng 1) | ~6h | dấu trên LB **chưa biết** |
| **D: 3 câu ngoài rổ** | **+1,17** | — | **lớn nhất, không phải việc E** |

**Xếp theo điểm-kỳ-vọng trên giờ máy: (1) hỏi D · (2) `K=50` · (3) đầu học lại.**

⚠️ Cả hai phép đo trên dựa vào **mẫu 24 cặp toàn câu đang SAI** — đúng cái bẫy thiên lệch chọn
mẫu ghi 25/08. Con số "K=20 bù 90%" là **chặn dưới** cho toàn tập (câu đang đúng thì còn tốt hơn),
nên kết luận "chọn đoạn đã cạn" **an toàn**. Nhưng "K=50 ăn +0,3" là **chặn trên**, phải trừ hao.

## ▶️ 28/08 — **`fusion_dev1000_run.ipynb` — KIỂM `n=3` TRÊN MẪU GẤP 3. VIỆC CHẠY TIẾP THEO.**

**Mục đích: PHÒNG THỦ, không phải tìm điểm.** `n=3` được chọn bằng cách quét trên public LB,
mà CLAUDE.md 19/08 đã cảnh báo *"heuristic fit theo public không chuyển được sang private"*.
dev300 sáng nay xác nhận `n=3` độc lập (0,9467, đỉnh dải 0–5) nhưng chỉ 300 câu. dev1000 xác
nhận thì lựa chọn vững hẳn cho vòng private — **nơi điểm số thật sự được tính.**

### Sửa gì so với `fusion_v3_run.ipynb` — tối thiểu, dùng lại trọn bộ máy sẵn có

| # | sửa | ghi chú |
|---|---|---|
| 1 | thêm `CFG["dev1000_a"]` / `["dev1000_b"]` | câu hỏi `dev_1000_locked.json`, rổ dev_1000 đã có |
| 2 | `M_RUN = 10 if MODE in ("public_a","dev1000_a")` | tách 2 lượt, y hệt cơ chế đề thi |
| 3 | `MODE == "dev"` → `MODE.startswith("dev")` | 3 chỗ: nạp gold, in trần rổ, bảng đo |
| 4 | `MODE == "public_b"` → `MODE.endswith("_b")` + `BASE` | lượt B nạp lại tầng 1 của lượt A |
| 5 | khối kết luận riêng cho dev1000 | in đỉnh `(biến thể, n)` và so với `max n=3` |

### Chi phí — ĐẾM THẬT, không ước

Đếm trên mẫu 40 câu của file rổ: **98 đoạn tầng 1/câu** (không phải 150 như tôi đoán).

| lượt | việc | ước |
|---|---|---|
| **`dev1000_a`** | tầng 1 (97.800 cặp ≈ 2,1h) + tầng 2 M=10 (≈1,7h) | **~3,8h** |
| **`dev1000_b`** | nạp lại tầng 1, chỉ chấm hạng 11–20 | **~1,7h** |

Cả hai dưới trần 12h với biên rộng. Tầng 1 **có checkpoint 100 câu** → đứt là chạy tiếp được.

⚠️ **Upload lên dataset: `dev_1000_locked.json`** (197KB) nếu chưa có — rổ `fusion_rrf_top50_dev_1000_matchEmbedded.json`
thì probe đã dùng nên chắc chắn đã ở đó. Lượt `_b` cần upload thêm `outputs/scores_dev1000_fusion_M10_K20_matchEmbedded.json` của lượt `_a`.

### Đọc kết quả — ĐẶT TRƯỚC

| kết quả | nghĩa |
|---|---|
| đỉnh vẫn ở `max, n=3`, hoặc chênh **< 0,3 điểm** | lựa chọn hiện tại **VỮNG** cho private → chốt, dồn báo cáo |
| đỉnh dời sang `n` khác, chênh **≥ 0,3 điểm** | `n=3` là thứ **fit vào public LB** → phải xem lại trước khi chốt bài private |

Notebook lưu `bang_n_dev1000_*.json` (bảng trọn biến thể × n) để phân tích CPU về sau.

## ⛔ 28/08 — **"PHẠM VI THẨM QUYỀN" VÀ "ƯU TIÊN VĂN BẢN CÒN HIỆU LỰC": ĐO XONG, CẢ HAI ÂM. 0 GIỜ GPU.**

Ý tưởng của Khim sau khi đọc ca `138214` (model chọn QĐ UBND Hà Nội thay vì Nghị định toàn quốc).
Trích thuộc tính văn bản từ trường `name` trong file fusion → `Ketqua_E/vanban_meta.json`
(5.244 văn bản: loại · năm ban hành · có phải cấp địa phương).

### ✅ TÍN HIỆU THÔ CÓ THẬT — đúng thứ bậc pháp lý

| loại | % gold | % ứng viên | tỉ lệ |
|---|---|---|---|
| **Luật** | 15,3 | 9,6 | **1,59×** |
| Nghị định | 27,1 | 22,8 | 1,19× |
| Thông tư | 22,3 | 28,3 | 0,79× |
| Quyết định | 17,2 | 21,1 | 0,81× |
| **UBND (địa phương)** | **0,64** | **1,57** | **0,41×** |

Gold **ít khi** là văn bản địa phương, đúng như ca `138214` gợi ý. Thứ bậc Luật > Nghị định >
Thông tư ≈ Quyết định hiện ra sạch sẽ.

### ⛔ NHƯNG CỘNG VÀO ĐIỂM THÌ KHÔNG ĂN — **kể cả khi ăn gian**

Ước tham số ưu thế **ngay trên chính dev300** (tức thiên vị có lợi, cho ra **trần lạc quan**):

| trọng số | R@5 | vs `blend n=3` |
|---|---|---|
| 0,5 | 0,9467 | +0,00 |
| 1 | 0,9433 | −0,33 |
| 2 | 0,9400 | −0,67 |
| 5 | 0,9333 | −1,33 |

**Vì sao:** đây là **ưu thế TOÀN CỤC**. Nó biết "Luật hay là gold hơn Thông tư" nhưng **không
biết CÂU NÀY cần Luật hay cần Thông tư**. Điểm CE đã mang nhiều thông tin hơn thế, nên cộng
một hằng số theo loại chỉ làm nhiễu. Thêm nữa **chỉ 2/300 câu có gold là văn bản UBND** — hình
phạt địa phương gần như không có gì để tác động.

### ⛔ "ƯU TIÊN VĂN BẢN MỚI/CÒN HIỆU LỰC" — **KHÔNG CÓ TÍN HIỆU, ĐÚNG BẰNG NGẪU NHIÊN**

| | |
|---|---|
| gold là văn bản **mới nhất** trong rổ 50 | **6/300 = 2,0%** — ngẫu nhiên cũng đúng 2,0% |
| hạng TB của gold nếu xếp **thuần theo năm** | **20,6/50** (xếp theo CE: **3,9**) |
| năm ban hành TB | gold 2017,0 · ứng viên 2016,6 — lệch **+0,4 năm** |
| cộng ưu thế theo năm, mọi trọng số | **−0,17 → −2,17** |

**Không có "văn bản mới thì hay là đáp án" trong bộ dữ liệu này.** Câu hỏi trải khắp nhiều
lĩnh vực và nhiều thời kỳ; văn bản gold cũ hay mới là ngẫu nhiên.

*(Ghi chú: **hiệu lực thật** — còn/hết hiệu lực — KHÔNG có trong dữ liệu. thuvienphapluat có
trường đó nhưng bộ `selected-contexts` chỉ có `link`/`passage`/`id`, và Kaggle không có mạng.
Năm ban hành là proxy duy nhất, và proxy đó vừa đo là rỗng.)*

### 📌 GHI NHẬN PHƯƠNG PHÁP — **ĐÂY LÀ QUY TRÌNH ĐÚNG**

Từ một quan sát định tính (đọc 1 ca) → giả thuyết → **trích đặc trưng, đo tỉ lệ thô** (thấy tín
hiệu thật!) → **đo trần bằng bản thiên vị có lợi** → âm → đóng. **Tổng: ~15 phút, 0 giờ GPU,
0 lượt nộp.** Nếu làm theo lối cũ thì đây là 3h fine-tune với đặc trưng mới rồi mới biết.

Bài học ghi lại: **"có tín hiệu thô" ≠ "cộng vào được".** Một ưu thế toàn cục không thắng nổi
một bộ chấm đã đọc nội dung, trừ khi nó nói được điều gì đó **riêng cho từng câu**.

## 🔎 28/08 — **ĐỌC THẬT CÁC CÂU "TƯỜNG". KHÔNG PHẢI GIỚI HẠN MODEL — LÀ NHÃN MƠ HỒ + LỖI CHỌN ĐOẠN.**

Lần đầu mở văn bản ra đọc thay vì chỉ nhìn điểm. Hai ca, hai nguyên nhân **khác hẳn** nhau,
và **không ca nào là "model kém"**.

### CA 1 — `138214`: **MODEL TRẢ LỜI ĐÚNG HƠN NHÃN GOLD**

> **Hỏi:** *"Ai có trách nhiệm kiểm tra Phiếu đăng ký dự tuyển công chức?"*

| | văn bản | đoạn lấy được |
|---|---|---|
| **gold** `58662` | Nghị định 138/2020 | nói về **thời hạn** thành lập Ban Kiểm tra, trả lời gián tiếp |
| **CE chọn** `209317` | Quyết định 17/2022 UBND Hà Nội | **"Điều 7. Ban kiểm tra Phiếu đăng ký dự tuyển… Nhiệm vụ, quyền hạn và **trách nhiệm** của Trưởng ban…"** |

**Văn bản model chọn trả lời thẳng câu hỏi hơn văn bản gold.** Model không sai. Đây là câu hỏi
mà **nhiều văn bản cùng trả lời được đúng**, nhưng chỉ một cái được đánh dấu gold.

→ Khớp với `oracle13`: **3 câu (`1524`, `159444`, `37542`) có oracle THẤP HƠN điểm hiện tại** —
tức đoạn hay nhất của chính văn bản gold vẫn thua văn bản khác. Đó không phải model đọc kém.

### CA 2 — `16942`: **LỖI CHỌN ĐOẠN, KHÔNG PHẢI LỖI CHẤM**

> **Hỏi:** *"Người giám định là ai?"*

`pick_chunks` lấy từ văn bản gold `102434` (Bộ luật TTHS) một đoạn về **suy đoán vô tội** —
**không hề nhắc tới "người giám định"**. Trong khi `oracle13` đã đo: đoạn tốt nhất của chính
văn bản đó ăn **0,9998** (điểm hiện tại 0,0002). Bộ chọn đoạn nhìn trượt, rồi vì CE cho điểm
thấp nên gold rơi khỏi cổng `M=20` và **không bao giờ được đọc sâu**.

### 📌 HỆ QUẢ — ĐỔI HẲN CÂU KẾT LUẬN CỦA BÁO CÁO

Trước: *"9 câu này là tường ngữ nghĩa, model 0,568B không với tới."*
**Sai.** Sau khi đọc:

| nguyên nhân | sửa được bằng | ghi chú |
|---|---|---|
| **nhãn gold mơ hồ** — nhiều văn bản cùng đúng | **KHÔNG sửa được bằng bất kỳ model nào** | giải thích vì sao 9 hướng đều âm |
| **chọn đoạn trượt** + cổng `M` | chọn đoạn tốt hơn / nâng M | `oracle13` định giá **+0,80**, dưới ngưỡng |

**Đây mới là lời giải thích đúng cho việc mọi can thiệp đều thất bại.** Không phải "model chạm
trần năng lực" — mà là **một phần đáng kể nhóm câu sai vốn không có đáp án duy nhất**. Không
model nào, không lượng dữ liệu nào dạy được một hệ thống chọn đúng **một** trong nhiều văn bản
cùng hợp lệ.

⚠️ **Đọc mới 2/13 ca.** Đây là **giả thuyết có hai ví dụ**, không phải kết luận định lượng.
Muốn chắc phải đọc hết 13 ca (CPU, ~30 phút người) và đếm bao nhiêu ca thuộc mỗi loại.
**Nhưng dù tỉ lệ là bao nhiêu, kết luận "đóng hướng model" không đổi** — cả hai nguyên nhân
đều KHÔNG sửa được bằng cách đổi hoặc huấn luyện lại bộ chấm.


## ⛔ 28/08 — **"22 CÂU BỊ CE LÀM HỎNG" LÀ LỖI CỦA TÔI. Ở `n=3` CHỈ CÒN **1**. HƯỚNG NÀY KHÔNG TỒN TẠI.**

Toàn bộ mục này CPU, 0 giờ GPU, từ `scores_dev300_moc_k3.json` + `rrf_dev300_matchEmb.json`.

### 🚨 LỖI: TÔI ĐO Ở `n=1`, BÀI NỘP CHẠY `n=3`

| cấu hình `blend` | CỨU | HỎNG | NET |
|---|---|---|---|
| `n_bm25 = 1` (probe dùng) | 14 | **22** | **−8** |
| **`n_bm25 = 3` (BÀI ĐANG NỘP)** | 12 | **1** | **+11** |

Tôi lấy con số 22 từ cấu hình của probe rồi gọi nó là "dư địa +7,3 điểm chưa ai nhắm vào".
**Sai.** `n=3` đã dọn sạch từ lâu — 21/22 câu hỏng có gold ở rổ hạng 1–3, đúng 3 slot mà `n=3`
giữ chỗ. Cần gạt tôi vừa "phát hiện" chính là cần gạt đã bật sẵn trong bài chốt 0.9118.

⛔ **HAI LẦN TRONG MỘT NGÀY tôi tính dư địa ở cấu hình KHÔNG PHẢI cấu hình đang nộp**
(sáng: lấy trần 0,80 của *chọn đoạn* áp cho *sửa model*; chiều: lấy `n=1` của probe làm mốc).

> **QUY TẮC: mọi con số dư địa phải đo ở ĐÚNG cấu hình bài đang nộp. Ghi kèm cấu hình bên cạnh
> con số, luôn luôn.** Dư địa đo ở cấu hình khác là dư địa của một bài toán khác.

### 📊 QUÉT LẠI TRỌN QUY TẮC GỘP ĐIỂM — `n=3` VẪN LÀ ĐỈNH

| quy tắc | R@5 | vs rổ trần |
|---|---|---|
| rổ trần, không reranker | 0,9117 | — |
| blend n=0 | 0,8817 | −3,00 |
| blend n=1 | 0,9100 | −0,17 |
| blend n=2 | 0,9300 | +1,83 |
| **blend n=3** | **0,9467** | **+3,50** (SE 1,18 · P(>0) = 1,00) |
| blend n=4 | 0,9367 | +2,50 |
| gộp điểm z-score, α ∈ {0,1…0,7} | 0,9083–0,9317 | **thua n=3 mọi α** |
| RRF hai thứ hạng, k ∈ {1…60} | 0,9033–0,9333 | **thua n=3 mọi k** |

**Tôi đã đoán rằng kết luận 17/08 ("quét hết cách gộp điểm rồi") sẽ hết hiệu lực vì CE giờ
NET âm. Đoán SAI — nó vẫn đúng nguyên.** `blend` thắng vì nó chỉ **giữ chỗ**, còn gộp điểm thì
bôi ảnh hưởng của CE lên cả 5 slot. Cơ chế đó không phụ thuộc CE đang dương hay âm.

### 🎯 TRẦN CỦA "CHỌN `n` THÍCH NGHI THEO TỪNG CÂU" = **+1,17. DƯỚI NGƯỠNG. ĐÓNG.**

Oracle chọn `n` tốt nhất cho **từng câu**: 0,9583 vs 0,9467 cố định = **+1,17 điểm, 4 câu.**
Đó là **trần tuyệt đối** của mọi quy tắc thích nghi, và nó đã dưới ngưỡng 2,0. Quy tắc thật thử
bằng ngưỡng CE margin: 0,00 hoặc âm.

### 🗺️ 13 CÂU CÒN SAI Ở CẤU HÌNH ĐANG NỘP — BẢN ĐỒ CUỐI CÙNG

| | số câu | ai | trạng thái |
|---|---|---|---|
| gold **ngoài rổ 50** | **3** | **D** | mở — 1,17 điểm |
| gold trong rổ, **cả rổ lẫn CE đều vùi** | **10** | E | "tường" — bác qua 5 hướng |

⚠️ *Cảnh báo phạm vi: các số trên tính bằng CE **tầng 1**, không phải `ce_deep` hai tầng của bài
nộp. Cấu trúc kết luận (n=3 là đỉnh, thích nghi dưới trần) chắc chắn; con số tuyệt đối sẽ lệch.*

### 📌 KẾT: **E KHÔNG CÒN CẦN GẠT NÀO TRÊN NGƯỠNG.** Lần này đã quét trọn, đo trần từng cái.

Cứu thêm câu → tường, 5 hướng âm. Bớt làm hỏng → `n=3` làm xong rồi, còn 1 câu. Gộp điểm →
thua mọi biến thể. Thích nghi theo câu → trần +1,17. **Tất cả đều đo, không cái nào đoán.**

**Việc còn lại của cả đội: (1) D nâng thứ tự đầu bảng — recall@1 đang 0,6217 và `blend` đưa
3 slot đầu của rổ THẲNG vào đáp án; (2) BÁO CÁO.**


## 🗺️ 28/08 — **BẢN ĐỒ DƯ ĐỊA, ĐO LẠI TRÊN RỔ MỚI. `oracle13` ĐÃ LỖI THỜI — D CHỈ CÒN 1,17, KHÔNG PHẢI 1,67.**

Toàn bộ mục này chạy CPU từ `order_dev300_matchEmb.json` + `scores_dev300_moc_k3.json`. 0 giờ GPU.

### ① 300 CÂU ĐANG NẰM ĐÂU TRONG RỔ `_matchEmbedded`

| hạng gold trong rổ | số câu | ai lo |
|---|---|---|
| **1** | **192** | — đã xong |
| 2–5 | 84 | — đã xong (cộng dồn **276 câu = 0,9117** không cần chấm gì) |
| 6–10 | 11 | **E** |
| 11–20 | 4 | **E** |
| 21–50 | 6 | **E** |
| **ngoài rổ 50** | **3** | **D** |

| | dev300 |
|---|---|
| rổ trần @5 (không làm gì) | 0,9117 |
| tầng 1 k=3 (đo 28/08) | 0,9100 |
| **TRẦN của E = recall@50 của rổ** | **0,9883** |
| gold ngoài rổ → **việc của D** | **1,17 điểm · 3 câu** |

⚠️ **`oracle13` (23/08) ghi D còn 1,67 điểm / 5 câu — số đó đo trên RỔ CŨ và đã lỗi thời.**
Rổ `_matchEmbedded` tự nó đã lấy thêm 2 câu. Recall@50: cũ 0,9817 → mới **0,9883**.

### 🔴 ② PHÁT HIỆN LỚN NHẤT: **RERANKER CỨU 14, LÀM HỎNG 22. NET −8.**

Đếm trực tiếp trên 300 câu, tầng 1 k=3 so với rổ trần:

| | số câu |
|---|---|
| rổ xếp gold ngoài top-5, **CE kéo vào được** | **14** |
| rổ xếp gold trong top-5, **CE đẩy ra** | **22** |
| **NET** | **−8 câu** |

**Đây là lời giải thích cơ chế cho việc tầng 1 (0,9100) thua rổ trần (0,9117).** Không phải
reranker "yếu" — nó **đổi chác lỗ**: mỗi câu cứu được thì làm hỏng 1,6 câu.

Và đây là lý do `blend_bm25_first` tồn tại: giữ chỗ `n` slot đầu theo rổ **chặn bớt phần
làm hỏng**. Toàn bộ giá trị của cần gạt `n_bm25` nằm ở đây, không phải ở chỗ "cứu thêm".

### 🎯 ③ VIỆC CỦA E — ĐỔI MỤC TIÊU: **ĐỪNG CỨU THÊM, HÃY BỚT LÀM HỎNG**

Ba ngày qua mọi thí nghiệm của E đều nhắm vào *cứu thêm câu* (model to hơn, chưng cất,
fine-tune, probe). **Nhắm sai vế.** Vế kia lớn hơn:

| cần gạt | quy mô | trạng thái |
|---|---|---|
| **giảm 22 câu bị CE làm hỏng** | trần **+7,3 điểm** | **CHƯA AI NHẮM VÀO** |
| cứu thêm 7 câu cả rổ lẫn CE đều vùi | +2,3 điểm | "tường" — đã bác qua 5 hướng |
| 3 câu ngoài rổ | +1,17 | việc của D |

⛔ **Phản biện đã lường trước:** CLAUDE.md 17/08 ghi *"OPTIMIZE CÁCH GỘP ĐIỂM — ĐÃ QUÉT HẾT,
đừng làm lại"*, và docstring `blend_bm25_first` liệt kê min-max / z-score / RRF đều thua.
**Nhưng phép quét đó chạy trên `dev_150` với rổ BM25 cũ, thời điểm CE còn NET DƯƠNG.** Giờ
CE đã NET ÂM (−8). Quy tắc gộp tối ưu trong hai chế độ đó **không thể giống nhau**.

→ **Việc rẻ nhất còn lại của E: quét lại quy tắc gộp điểm trên rổ mới, CPU, vài giây/cấu hình.**
Cần thêm `rrf_score` của rổ mới (tách từ file 207MB như đã làm với thứ tự). Không tốn GPU.

### 📌 ④ VIỆC CỦA D — ĐỔI CHỖ ĐO

recall@50 của D gần như hết dư địa (**0,9883**, chỉ 3 câu ngoài rổ). Nhưng:

| k | rổ cũ | rổ mới | Δ |
|---|---|---|---|
| **1** | 0,5783 | **0,6217** | **+4,33** |
| 5 | 0,8733 | 0,9117 | +3,83 |
| 10 | 0,9317 | 0,9517 | +2,00 |
| 20 | 0,9633 | 0,9667 | +0,33 |
| 50 | 0,9817 | 0,9883 | +0,67 |

**Đóng góp của D giờ nằm ở THỨ TỰ đầu bảng, không ở recall@50.** `blend` giữ chỗ `n` slot đầu
theo rổ → **recall@1 của rổ đi thẳng vào kết quả cuối**, không qua reranker. Nâng recall@1 từ
0,6217 là cần gạt trực tiếp nhất còn lại của cả đội.

→ **Câu hỏi cho D không còn là "lấy thêm văn bản vào rổ" mà là "xếp đúng hơn ở hạng 1–5".**


## 🏁 28/08 — **`probe_k3` XONG. TÍN HIỆU CÓ THẬT NHƯNG ĐÁNG +0,67. ĐÓNG HƯỚNG FINE-TUNE — LẦN NÀY BẰNG PHÉP ĐO.**

`probe.zip` · 2,3h GPU · 81.000 cặp · **có `scores_dev300_moc_k3.json`** nên mọi phân tích dưới
đây chạy trên CPU, 0 giờ GPU thêm.

| dev300 | MỐC (đầu gốc) | học lại — công thức notebook | học lại — công thức numpy | Δ tốt nhất |
|---|---|---|---|---|
| k=1, 900 ký tự | 0,8267 | 0,8383 | 0,8483 | **+2,16** |
| k=1, 1800 ký tự | 0,8617 | — | 0,8750 | **+1,33** |
| **k=3, 1800 ký tự** | **0,9100** | **0,9100** | **0,9167** | **+0,67** |
| SÀN (rổ trần) | | | | 0,9117 |

**Ngoại suy ghi tối 27/08 — "Δ kỳ vọng dưới +1,0" — ĐÚNG.** Giờ là số đo, không còn là ngoại suy.

### ✅ CÂU HỎI GỐC CỦA PROBE: **CÓ TÍN HIỆU.** Không mơ hồ.

- Đầu học lại đổi **cả 15.000 điểm**, 153/300 câu đổi thứ tự thuần CE → đầu ĐÃ học thật.
- Công thức numpy: **3/3 hạt giống ra đúng 0,9167**, tất định.
- Trong 32 câu gold nằm ngoài top-5 của đầu gốc: **kéo vào 6, làm văng 2 → NET +4 câu.**
- Vượt cả SÀN (0,9167 > 0,9117) — lần đầu một cấu hình tầng 1 làm được.

### ⛔ NHƯNG NÓ ĐÁNG **+0,67 ĐIỂM**, VÀ KHÔNG CHẠM CÂU NÀO ĐANG SAI

| | |
|---|---|
| Δ tốt nhất | **+0,67** (2 câu / 300) |
| ngưỡng quy tắc 4 | **≥ 2,0** |
| nhiễu dev300 | ±1,5 câu |
| **18 câu pipeline ĐANG SAI** | đầu gốc **5/18** → học lại **5/18** — **KHÔNG ĐỔI MỘT CÂU** |

Dòng cuối là dòng quyết định. Đầu học lại cứu được 4 câu ròng, **nhưng không câu nào nằm trong
nhóm pipeline đang thua.** Nó giỏi hơn ở chỗ vốn đã không hỏng. Đây chính là quy luật
"bốn giải pháp hoá ra là một", đo trực tiếp lần đầu.

⚠️ **Và phải nói cho sòng phẳng: công thức ĐẶT TRƯỚC (notebook) cho Δ = 0,0000 chằn chặn.**
Con số +0,67 đến từ một biến thể **hậu kiểm** (khởi tạo ngẫu nhiên, bỏ dropout). Báo cáo +0,67
như "kết quả" mà giấu chuyện nó được chọn sau khi nhìn số là đúng cái bẫy chọn mẫu đã ghi 25/08.
**Ghi cả hai, ghi rõ cái nào đặt trước.**

### 🔑 PHÁT HIỆN PHỤ ĐÁNG GIÁ CHO BÁO CÁO: **KHỞI TẠO TỪ TRỌNG SỐ GỐC LÀ MỘT BẤT LỢI**

| khởi tạo đầu phân loại | R@5 |
|---|---|
| **bằng chính trọng số gốc** (+ dropout) | 0,9100 |
| **ngẫu nhiên** (không dropout) | **0,9167** |

Cùng dữ liệu, cùng hàm mất mát, cùng số epoch. Bắt đầu từ nghiệm cũ thì **không thoát ra được** —
đầu gốc nằm trong một cực tiểu địa phương mà hạ gradient khởi từ đó không rời khỏi. Đây là một
lập luận cơ chế cho **cả hai lần fine-tune đã thua**: huấn luyện tiếp từ trọng số đã hội tụ
mang sẵn một bất lợi, không chỉ là chuyện nhãn hay negative.

### 📊 SỐ MẠNH NHẤT CỦA CẢ DỰ ÁN — DÀNH CHO BÁO CÁO

| dev300 | R@5 |
|---|---|
| rổ `_matchEmbedded` **trần, không chấm lại gì** | **0,9117** |
| tầng 1 đầy đủ (k=3, MAX 3 đoạn), model 0,568B | **0,9100** |

**Tầng 1 chấm lại toàn bộ 50 ứng viên bằng cross-encoder 568 triệu tham số, và ra KÉM HƠN
việc không chấm.** Không phải reranker yếu — mà rổ đã giỏi tới mức không còn gì để sửa.
Đóng góp của reranker đã teo về **âm** ở tầng 1; toàn bộ giá trị còn lại nằm ở tầng 2.

### 📌 CHỐT

**KHÔNG chạy LoRA.** Lần này là phép đo, không phải ngoại suy, và không dùng nhầm con số trần
như sáng 27/08. Năm đường độc lập cùng chỉ một hướng: hai lần fine-tune thua · chưng cất NET −16 ·
thầy 8B thua trò 0,568B · probe Δ ≤ +0,67 · 18 câu sai không nhúc nhích.

**BÀI CHỐT: `Ketqua_E/submission_matchEmb_M20_n3.zip` — 0.9118. Toàn bộ còn lại: BÁO CÁO.**

*Tài sản:* `Ketqua_E/scores_dev300_{moc,probe}_k3.json` — điểm từng văn bản của **cả đầu gốc lẫn
đầu học lại**. Mọi phân tích hậu kỳ từ nay miễn phí trên CPU. Đây là lần đầu quy tắc 2 được
thực thi đủ cho một thí nghiệm chẩn đoán.



### ▶️ `probe_k3_run.ipynb` — DỰNG XONG 27/08. **ĐÂY LÀ VIỆC CHẠY TIẾP THEO.**

**~2,3h GPU · 81.000 cặp** (train 36.000 + dev 45.000). Upload dataset: **không có gì mới**.

| # | sửa gì | vì sao |
|---|---|---|
| 1 | `K_CHUNK = 3`, chấm 3 đoạn rồi **MAX** | đúng tầng 1 thật; k=1 không bao giờ với tới SÀN |
| 2 | `ba_doan()` đệm đủ 3 đoạn | văn bản ít đoạn hơn 3; đệm trùng vô hại vì lấy MAX |
| 3 | cache `vec_*_k3.npy` | `nap()` chỉ kiểm SỐ HÀNG — bẫy đã suýt dính 2 lần |
| 4 | **lưu `scores_dev300_moc_k3.json`** | quy tắc 2: hai lượt trước vứt điểm đầu gốc (`MOC, _ =`) |
| 5 | `assert` → **cảnh báo `HOP_LE`** | vector đã lưu, chạy tiếp tốn 2 phút mà biết thêm Δ |

⚠️ **Sửa 4 là thứ đắt nhất đã bỏ lỡ hai lần.** Không có điểm của đầu gốc thì mọi phân tích
từng câu (câu nào được cứu, câu nào bị hỏng, chồng lấn với 18 câu sai) **không làm được trên
CPU** — phải chạy lại GPU. Có nó rồi thì mọi thí nghiệm hậu kỳ đều miễn phí.

**Vòng huấn luyện phải MAX y hệt lúc đánh giá** (`view(B, K, K_CHUNK).max(-1)`), nếu không thì
huấn luyện một đằng đánh giá một nẻo — đã kiểm hình dạng tensor trên CPU trước khi giao.

**Đọc kết quả:** `meta_probe.json` có `hop_le`. **`hop_le = false` → bỏ `dat`, đừng đọc như cổng.**
Kỳ vọng đặt trước: **~30% cổng qua**. Đây là **lượt kỹ thuật cuối**, qua hay không cũng dồn báo cáo.


## 🔬 27/08 TỐI — **CỨU ĐƯỢC LƯỢT CHẠY HỎNG. Δ CÓ THẬT NHƯNG **TEO KHI ĐẦU VÀO TỐT LÊN**.**

`results (17).zip` **có `vec_train_1800.npy` + `vec_dev_1800.npy`** — Kaggle giữ `/kaggle/working`
kể cả khi notebook lỗi. 46,4 phút mã hoá **không mất**. Toàn bộ mục này chạy trên **CPU máy Khim,
0 giờ GPU**, huấn luyện lại đầu phân loại bằng numpy (~15 giây/lượt).

| dev300, cùng model, cùng rổ | **EXC=900** | **EXC=1800** |
|---|---|---|
| SÀN — rổ trần, không reranker | 0,9117 | 0,9117 |
| MỐC — đầu gốc | 0,8267 | 0,8617 |
| đầu học lại (numpy, 3 hạt giống) | 0,8483 | **0,8750** ± 0,0033 |
| **Δ do học lại đầu** | **+2,16** | **+1,33** |
| còn thua SÀN | −6,34 | −3,67 |

### ✅ ĐIỀU 1: Δ CÓ THẬT, KHÔNG PHẢI NHIỄU

SD giữa 3 hạt giống = 0,0033 (**1 câu**), Δ = 0,0133 (**4 câu**). Ở EXC=900 còn tất định tuyệt đối
(4/4 hạt giống ra 0,8483). Cộng với đối chứng xáo nhãn đã sụp về 0,6683/0,7517 → **biểu diễn
đóng băng CHẮC CHẮN chứa tín hiệu mà đầu gốc đọc chưa hết.** Câu hỏi gốc của probe: **có.**

### 🔴 ĐIỀU 2 — QUAN TRỌNG HƠN: **Δ TEO 38% KHI ĐẦU VÀO TỐT GẤP ĐÔI**

`+2,16 → +1,33`. Đầu vào càng nhiều bằng chứng, việc "đọc lại cho đúng" càng ít chỗ để sửa.
Đây **đúng quy luật "bốn giải pháp hoá ra là một"** ghi 23/08, lần này đo được thành số trên
chính một cần gạt.

→ Ngoại suy sang vùng thật (hai tầng, M=20 × K=20 đoạn/văn bản, max — **nhiều bằng chứng hơn
1800 ký tự rất nhiều**): Δ kỳ vọng **dưới +1,0**, tức **dưới ngưỡng 2,0 và trong sàn nhiễu dev300.**

⚠️ Đây là **ngoại suy từ 2 điểm đo**, không phải phép đo. Ghi rõ để không tự lừa mình.

### ⛔ ĐIỀU 3: VÙNG ĐO **VẪN** CHƯA HỢP LỆ

0,8750 vẫn thua SÀN **3,67 điểm**. Tầng 1 một-đoạn không bao giờ với tới sàn, vì tầng 1 thật
chấm **3 đoạn `top_chunks` của D rồi lấy max**, không phải 1 đoạn. Muốn cổng hợp lệ phải `k=3`.

### 💰 GIÁ CỦA LƯỢT `k=3` — ĐÃ TÍNH, KHÔNG CẮT ĐƯỢC

Mã hoá ×3: dev 45.000 + train 36.000 = 81.000 cặp ≈ **2,3h GPU** (nhịp đo hôm nay: 27.000 / 46,4 phút).

Đã thử cắt tập huấn luyện để rẻ hơn — **không cắt được**:

| số nhóm train | R@5 |
|---|---|
| 400 | 0,8650 |
| 800 | 0,8683 |
| 1500 | **0,8717** |

Đường còn đang lên ở 1500, chưa bão hoà. Giảm `N_CAU` là mất tín hiệu thật, không phải mua rẻ.
(Ngược lại: nó gợi ý **thêm dữ liệu còn ăn** — đáng ghi cho phần bàn luận báo cáo.)

### 📌 TRẠNG THÁI HƯỚNG FINE-TUNE: **TREO, KHÔNG ĐÓNG**

Sửa lại so với kết luận sáng nay — **kết luận sáng nay dùng SAI con số trần**:

> Tôi lấy "+0,80" (trần của *chọn đoạn + cổng M*) áp cho *sửa model*. Sai rổ. Bảng oracle13 ghi
> rõ rổ **"model chấm sai hẳn (9 câu) = 3,00 điểm"** — **trên** ngưỡng 2,0. Quy tắc 4 **không**
> chặn hướng này.

Và "9 câu đó cần model >3B" cũng đã bị chính mình lật: **8B thua 0,568B** (NET −16, 25/08).
Model to hơn không phải câu trả lời → giả thuyết "model nhỏ có sẵn tín hiệu, chỉ đọc lệch"
**đáng kiểm hơn**, không phải kém đi. Hai điều 1 và 2 ở trên vừa cho nó bằng chứng đầu tiên.

**Chưa kết luận được LoRA có hiệu quả hay không.** Đang có: bằng chứng tín hiệu tồn tại (điều 1),
và bằng chứng nó teo dần ở vùng giàu bằng chứng (điều 2). Hai thứ ngược chiều nhau.


## ⛔ 27/08 — **PROBE CHẠY LẠI ĐÚNG VÙNG: `assert` NỔ. MỐC 0,8617 < SÀN 0,9117. ĐÓNG HƯỚNG FINE-TUNE.**

46,4 phút mã hoá, dừng sạch ở Bước 4, đúng nhánh đã đặt trước.

```
SÀN (rổ trần, không reranker)  R@5 = 0.9117
MỐC (đầu gốc, EXC=1800)        R@5 = 0.8617
AssertionError: MỐC 0.8617 < SÀN 0.9117 — tầng 1 còn thua việc KHÔNG chấm.
```

### ✅ CHẨN ĐOÁN CẮT ĐOẠN ĐÚNG CHÍNH XÁC — ĐO ĐƯỢC THÀNH SỐ

| MỐC tầng 1, cùng model, cùng rổ, chỉ khác độ dài đoạn | R@5 |
|---|---|
| `EXC = 900` (bản cũ, cắt đôi đoạn 1800) | 0,8267 |
| `EXC = 1800` (bản sửa) | **0,8617** |
| **giá của một dòng cắt nhầm** | **+3,50 điểm** |

Sửa một hằng số ăn **+3,50 điểm** — lớn hơn mọi thứ đã thử ba ngày qua cộng lại. Nhưng nó chỉ
đưa MỐC từ *thua sàn 8,50* lên *thua sàn 5,00*. **Vẫn thua.**

⚠️ **Bug này CHỈ có trong `probe_run.ipynb`, KHÔNG đụng tới bài nộp.** `deepen_one` đưa đoạn
`pick_chunks` **nguyên vẹn** vào CE, không cắt (đã đọc lại `deep_chunk.py` dòng 199–205). Bài
chốt 0.9118 không bị ảnh hưởng.

### 🔑 SỐ QUAN TRỌNG NHẤT: RỔ MỚI ĐÃ TỰ LÀM XONG VIỆC CỦA RERANKER

| | rổ trần | tầng 1 | Δ tầng 1 mang lại |
|---|---|---|---|
| rổ CŨ (fusion) | 0,8733 | 0,8800 | **+0,67** |
| rổ MỚI (`_matchEmbedded`) | **0,9117** | 0,8617 (một đoạn) | **−5,00** |

Rổ `_matchEmbedded` **một mình** đã đạt 0,9117 — cao hơn cả pipeline hai tầng trên rổ cũ
(0,9233) chỉ kém 1,2 điểm, mà không chấm lại một chữ nào. Đây là bằng chứng định lượng
trực tiếp nhất cho luận điểm ghi 23/08: **phần đóng góp của reranker đang teo đi rất nhanh.**
Nó không teo vì reranker yếu đi — nó teo vì **rổ đã giỏi tới mức không còn gì để sửa.**

### 📌 ĐÓNG HƯỚNG — VÀ NÓI RÕ ĐÓNG VÌ LÝ DO GÌ

**Không chạy LoRA.** Nhưng phải ghi trung thực:

> Probe **không** chứng minh "biểu diễn không chứa tín hiệu". Nó chứng minh **vùng đo một-đoạn
> không kiểm được câu hỏi đó**, vì ngay cả mốc chưa học lại đã nằm dưới sàn.

Đóng hướng vì **chi phí–lợi ích**, không vì đã bác bỏ:
- Quy tắc 4: chỉ chạy thí nghiệm kỳ vọng đổi ≥2 điểm. Tổng đóng góp biên của reranker trên rổ
  mới giờ chỉ còn khoảng +1 điểm (LB 0.9109 rổ cũ → 0.9118 rổ mới, trong khi rổ tự nó +3,84
  trên dev). **Không có cơ chế nào để LoRA lấy ra ≥2 điểm từ một khoản chỉ còn ~1 điểm.**
- Muốn đo cho đủ công bằng thì phải dựng probe trên `top_chunks` của D (3 đoạn/văn bản, đúng
  tầng 1 thật) — thêm ~1,5h GPU để trả lời một câu hỏi mà trần của nó đã biết là dưới 2 điểm.

**Đây là hướng thứ BẢY bị loại.** M=30 · ensemble bộ chấm · trộn hai pipeline · rổ mới của D ·
đổi base model · chưng cất · fine-tune. **BÀI CHỐT: `submission_matchEmb_M20_n3.zip` — 0.9118.**

### 🛡️ CỔNG ĐẶT TRƯỚC ĐÃ CỨU LẦN THỨ HAI

| lần | cổng | tiết kiệm |
|---|---|---|
| `congkiem_run` (25/08) | thầy − học trò ≥ +0,08 | **~18h** |
| `assert MOC >= SAN` (27/08) | tầng 1 phải hơn "không chấm" | **3h + cả nhánh LoRA** |

So với fine-tune: hai lần thua, **10h**, không cổng, chỉ biết thua sau khi chạy hết.
**Ba dòng `assert` rẻ hơn mọi thứ khác trong repo này.**

*Việc tiếp theo: BÁO CÁO.* Bốn mục có số liệu sẵn, không cần thêm giờ GPU nào:
① bảng ablation 10 model · ② vì sao chưng cất không ăn (600 nhóm, NET −16) ·
③ **vì sao reranker teo khi rổ mạnh lên** (bảng ở trên — đây là mục mạnh nhất) ·
④ hệ thống cổng đặt trước đã cứu 21h GPU như thế nào.


## 🔴 27/08 — **CỔNG `probe_run` ĐẠT (+0,0117) NHƯNG **VÔ HIỆU**. MỐC CỦA NÓ THẤP HƠN "KHÔNG LÀM GÌ" 8,5 ĐIỂM.**

`results (16).zip` đã về. `meta_probe.json`: `dat = true`.

| | R@1 | R@5 |
|---|---|---|
| đầu gốc (MỐC) | 0,6217 | **0,8267** |
| đầu học lại | 0,6217 | **0,8383** |
| Δ | 0,0000 | **+0,0117** (cổng ≥ +0,0100) |

Biên vượt cổng = **0,0017 = nửa câu trên 300**. Nhưng đó không phải vấn đề. Vấn đề là **MỐC**.

### ⛔ SỐ GIẾT CỔNG: RỔ TRẦN, KHÔNG RERANKER GÌ CẢ

Lấy thẳng top-5 của rổ `_matchEmbedded`, **không chấm lại một chữ nào**, cùng 300 câu, cùng hàm `blend`:

| cấu hình dev300 | R@5 |
|---|---|
| **rổ `_matchEmbedded` trần, KHÔNG reranker** | **0,9117** |
| probe — đầu gốc (MỐC của cổng) | 0,8267 ← **−8,50** |
| probe — đầu học lại | 0,8383 ← **−7,34** |
| probe — đầu học lại, công thức của tôi (bỏ dropout) | 0,8483 ← **−6,34** |

**Cấu hình probe chấm TỆ HƠN việc không chấm 8,5 điểm.** Cổng đo "cải thiện" bên trong một
vùng hỏng. Nâng một bộ chấm từ *tệ hơn không làm gì rất nhiều* lên *tệ hơn không làm gì hơi
ít hơn* **không nói được gì** về việc LoRA có ăn ở vùng thật (hai tầng, ~0,9350) hay không.

⛔ **Đây là lần thứ BA đặt ngưỡng sai** (1: pre-register ≥+2,0 cho `rescore8b`; 2: cổng ≥0,60
cho nhãn thầy; 3: cổng này). Quy tắc 25/08 — *"ngưỡng phải TƯƠNG ĐỐI so với mốc hiện có"* —
notebook có đo mốc trong cùng file (đúng), nhưng **mốc đó không phải sàn thật**. Sàn thật
luôn là **"không làm gì"**.

> **QUY TẮC BỔ SUNG (dán lên tường): mọi phép đo bộ chấm phải in kèm dòng "rổ trần, không
> reranker". Nếu cấu hình đang đo còn thua dòng đó thì DỪNG, đừng đọc Δ.** Một dòng code.

### 🔍 NGUYÊN NHÂN VÙNG HỎNG — ĐÃ TÌM RA, LÀ MỘT SỐ

`probe_run` cell 1: `DC.MERGE_CHARS = 1800` rồi cell 2/3: `pick_chunks(...)[0][:EXC]`, **`EXC = 900`**.
→ Gộp đoạn ra 1800 ký tự rồi **cắt đôi vứt một nửa**. Mỗi văn bản chỉ được chấm bằng 900 ký tự,
trong khi pipeline thật dùng đủ 1800. `MAXLEN=512` token thừa sức chứa 1800 ký tự, nên việc cắt
này **không đổi lấy được gì**.

Đối chứng trên rổ CŨ (`scores_dev300_fusion_M20_K20.json`, đủ 1800 ký tự):

| dev300, rổ cũ | R@5 |
|---|---|
| rổ trần | 0,8733 |
| tầng 1 `ce` | **0,8800** ← tầng 1 **hơn** rổ +0,67 |
| hai tầng `ce_deep` | 0,9233 |

Tầng 1 làm đúng thì **hơn** rổ. Trong probe nó **thua rổ 8,5 điểm**. Chênh lệch nằm ở nửa
đoạn bị vứt, không ở model.

*(Kiểm chéo mã đo: rổ cũ trần 0,8733 → rổ mới trần 0,9117 = **+3,84**, khớp con số **+3,83**
đã ghi 24/08. Đoạn mã đo dev300 chạy lại trên CPU là đúng.)*

### ✅ HAI ĐIỀU PROBE **CÓ** TRẢ LỜI ĐƯỢC (chạy lại trên CPU từ `vec_*.npy`, 0 giờ GPU)

1. **Δ không phải nhiễu hạt giống.** Huấn luyện lại đầu phân loại bằng numpy với 4 hạt giống
   khác nhau → **R@5 = 0,8483 y hệt cả 4 lần**. Bài toán trên vector đóng băng hội tụ tất định.
2. **Đầu học lại CÓ học tín hiệu thật.** Đối chứng xáo nhãn (gold không còn ở chỉ số 0):
   R@5 tụt xuống **0,6683 / 0,7517** — sụp hẳn dưới mốc. Nếu Δ là ảo thì đối chứng đã không sụp.

→ Biểu diễn của model **có** chứa tín hiệu mà đầu gốc đọc lệch. Điều đó **đúng**, nhưng nó
đúng ở vùng 900 ký tự, nơi đầu gốc bị bỏ đói. Không suy ra được gì cho vùng 1800 × hai tầng.

### 📌 QUYẾT ĐỊNH

**KHÔNG chạy LoRA 3h dựa trên cổng này.** Cổng không hợp lệ.

Muốn mở lại hướng fine-tune thì phải làm lại probe **trong vùng thật**: `EXC = 1800`, chấm trên
rổ `_matchEmbedded`, và cổng là **"vượt 0,9117 (rổ trần)"** rồi mới tới **"vượt hai tầng"** —
không bao giờ là "vượt mốc nội bộ của chính notebook". Chi phí: một lượt mã hoá lại (~30 phút GPU),
vì `vec_dev.npy` hiện tại là vector của đoạn 900 ký tự, dùng lại không được.

Cân nhắc thẳng: kết luận 25/08 (*"dồn toàn bộ vào BÁO CÁO"*) **không đổi**. M=30 · ensemble ·
trộn pipeline · rổ mới của D · đổi base model · chưng cất — tất cả đã âm. Đây là hướng thứ bảy,
và bằng chứng cho nó vừa bốc hơi. **BÀI CHỐT vẫn là `submission_matchEmb_M20_n3.zip` — 0.9118.**

### 🔧 ĐÃ SỬA `probe_run.ipynb` (27/08) — CHẠY LẠI ĐƯỢC. **CHỈ UPLOAD LẠI NOTEBOOK.**

Ba sửa đổi, không viết lại gì:

| # | chỗ | cũ | mới |
|---|---|---|---|
| 1 | `EXC` | **900** — cắt đôi đoạn 1800 | **1800** — `[:EXC]` thành vô hại |
| 2 | tên file cache | `vec_{train,dev}.npy` | `vec_{train,dev}_1800.npy` |
| 3 | Bước 4 | chỉ in MỐC | in **SÀN** + `assert MOC >= SÀN` |

**Sửa 2 là thứ dễ mất nhất nếu bỏ qua.** `nap()` chỉ kiểm **độ dài** vector, không kiểm nội
dung — vector 900 và vector 1800 có **cùng số hàng**. Giữ nguyên tên thì lượt sau nạp lại đúng
vector hỏng của lượt này, in ra một con số trông hợp lý, và không ai biết. Đổi tên là cách rẻ
nhất để bẫy đó không bao giờ nổ.

**Sửa 3 là thứ đáng giữ lâu dài.** `assert MOC[5] >= SAN` — tầng 1 còn thua "không chấm gì"
thì notebook **dừng ngay**, không in Δ. Cổng cũ đọc một mình được; cổng mới phải đọc cùng sàn:
`dat = d5 >= NGUONG and MOI[5] > SAN`.

**Chi phí:** ~35 phút GPU, y như lượt trước (27.000 lượt mã hoá). Upload lên dataset `project-ir`:
**không có gì mới** — mọi file đã ở đó từ lượt trước. Chỉ upload lại `probe_run.ipynb`.
⛔ **Đừng upload `outputs/` của lượt cũ** (dù đã đổi tên nên có upload cũng không nạp nhầm).

**Đọc kết quả:**
- `assert` nổ ở Bước 4 → ngay cả đoạn 1800 ký tự, tầng 1 một-đoạn vẫn thua rổ → **đóng hướng
  fine-tune**, không phải vì model kém mà vì rổ `_matchEmbedded` đã tự làm xong phần việc đó
  (khớp đúng luận điểm "đóng góp của reranker đang teo" ghi 23/08).
- Qua `assert`, `dat = True` → biểu diễn có tín hiệu chưa dùng **trong vùng thật** → LoRA đáng 3h.
- Qua `assert`, `dat = False` → đầu gốc đã đọc hết những gì có → LoRA không có gì để lấy thêm.

*Tài sản mới:* `Ketqua_E/order_dev300_matchEmb.json` (thứ tự rổ mới cho dev300, tách từ file 207MB —
dùng để đo mọi cấu hình dev300 trên CPU trong vài giây, không cần nạp lại file lớn).


## 🔬 25/08 — **`probe_run.ipynb`: CHỈ TRAIN ĐẦU PHÂN LOẠI. CHẨN ĐOÁN, KHÔNG PHẢI ĂN ĐIỂM.**

~35 phút GPU. **Rủi ro làm hỏng model = 0** (encoder đóng băng tuyệt đối).

**Câu hỏi nó trả lời:** 9 câu "tường ngữ nghĩa" — biểu diễn của model **có chứa** tín hiệu
mà chỉ bị chấm lệch, hay **không chứa gì cả**?

- Δ R@5 ≥ +0,0100 → thông tin có sẵn, chỉ đọc sai → **LoRA đáng chạy 3h**.
- Δ < +0,0100 → biểu diễn không chứa tín hiệu → **tường là tường thật, ĐÓNG hướng fine-tune.**

### ⚠️ KỸ THUẬT FINE-TUNE **KHÔNG PHẢI** BIẾN QUAN TRỌNG

Hai lần thua đều dùng full FT, nhưng nguyên nhân đã chẩn là **hàm mất mát** và **negative**.
Đổi LoRA → QLoRA / prefix / adapter mà giữ nguyên hai thứ kia thì **thua lần ba**.

| trục | đã dùng (thua) | phải đổi thành |
|---|---|---|
| **hàm mất mát** | BCE từng cặp, nhãn cứng 0/1 | **softmax listwise trên nhóm** — chỉ đòi gold cao nhất |
| **negative** | BM25 top-20 nguyên xi | **bỏ top-2**, lấy hạng 3–10 |
| kỹ thuật tham số | full FT | LoRA (**không** QLoRA — model 0,568B không cần lượng tử hoá) |

Bằng chứng cho trục 2: đo hôm nay, **29% "negative" được thầy 8B chấm > 0,5** — chúng liên
quan thật. BCE ép chúng về 0 là dạy sai. Softmax listwise thì không.

### Ba chi tiết khiến phép so của `probe_run` chặt chẽ

1. **Đầu phân loại khởi tạo BẰNG CHÍNH trọng số gốc** → bước 0 giống hệt model cũ. Mốc là
   *cùng model, cùng mã, cùng rổ*, không phải số chép từ lượt khác.
2. **Mã hoá 1 lần rồi cache vector** → huấn luyện chạy trên vector, vài giây, quét siêu
   tham số miễn phí.
3. **Encoder `requires_grad = False` tường minh** → vector biểu diễn không đổi một chút nào,
   nên Δ đo được **chỉ** đến từ cách chấm.

## ⛔ 25/08 — **CHƯNG CẤT CHẾT. THẦY KHÔNG GIỎI HƠN HỌC TRÒ. ĐÓNG HƯỚNG.**

`congkiem_run.ipynb`, 600 nhóm ngẫu nhiên, **cùng một rổ, cùng một cách trích đoạn**:

| | gold@1 |
|---|---|
| học trò `AITeamVN` 0,568B | **0,5683** |
| **THẦY** `Qwen3-Reranker-8B` | **0,5417** |
| Δ | **−0,0267** ← thầy **THUA** |

```
học trò SAI  259 nhóm → thầy CỨU  59  = 22,8%
học trò ĐÚNG 341 nhóm → thầy HỎNG 75  = 22,0%
NET −16 nhóm
```

**Thầy lật ~22% theo CẢ HAI CHIỀU.** Đó là dấu vân của một model **mạnh ngang, nhiễu khác
nhau** — không phải model giỏi hơn. Model 8 tỉ tham số không hơn model 0,568 tỉ ở việc này.

### 🚨 SAI LẦM PHƯƠNG PHÁP CỦA TÔI: **THIÊN LỆCH CHỌN MẪU**

Tôi đã dùng `hard15` làm bằng chứng khởi động cả hướng này: *"8B 6/11 vs ce_ours 2/11 →
trần +2,0 điểm"*. **Bằng chứng đó vô giá trị**, và số liệu 600 nhóm chứng minh tại sao:

> **15 câu đó được chọn VÌ pipeline của mình sai.** Chọn mẫu dựa trên lỗi của model A rồi
> so A với B trên chính mẫu đó thì B **luôn** trông giỏi hơn, kể cả khi B mạnh ngang A.
> Đây là hồi quy về trung bình, sách giáo khoa.

Kiểm bằng số: thầy cứu 22,8% số nhóm học trò sai. Trên 11 câu **toàn là câu học trò sai**,
kỳ vọng thầy "cứu" được **2,5 câu** dù nó chỉ mạnh ngang. Thực tế quan sát **4**.
**4 so với 2,5 trên n=11 — không phân biệt được với nhiễu.**

Và phần bị giấu đi: trên tập chọn kiểu đó, **không ai nhìn thấy 75 nhóm thầy làm hỏng**,
vì chúng không nằm trong mẫu.

> **QUY TẮC (dán lên tường): không bao giờ đánh giá model B trên tập mẫu được chọn bằng lỗi
> của model A. Muốn so hai model thì so trên mẫu NGẪU NHIÊN, hoặc đếm cả hai chiều
> cứu/hỏng.** Đây là lỗi đã suýt tốn 25h GPU.

### 💰 TỔNG KẾT CHI PHÍ — HỆ THỐNG CỔNG ĐÃ LÀM ĐÚNG VIỆC

| | |
|---|---|
| đã tiêu | **6,3h** (sinh nhãn) + **5 phút** (cổng kiểm) |
| kế hoạch đầy đủ nếu không có cổng | ~25h |
| **tiết kiệm** | **~18h GPU** |

So với fine-tune: hai lần thua, **10h**, không có cổng, và chỉ biết mình thua sau khi chạy hết.

### 📌 KẾT LUẬN CUỐI VỀ ĐIỂM SỐ

Ba ngày qua đã đo và loại: M=30 · ensemble bộ chấm · trộn hai pipeline · rổ mới của D ·
đổi base model · **chưng cất**. Tất cả đều âm hoặc chồng lấp.

**BÀI CHỐT: `Ketqua_E/submission_matchEmb_M20_n3.zip` — public 0.9118.**
Phần còn thiếu tới 0.95 nằm ở **truy hồi (D)** và ở nhóm câu hỏi lệch ngữ nghĩa mà **không
bộ chấm nào trong 10 model đã thử chạm tới được**. → **Dồn toàn bộ vào BÁO CÁO.**

*Tài sản giữ lại:* `nhan_thay.json` (4.800 nhãn 8B), `diem_tro_600nhom.json`,
`meta_congkiem.json`. Đủ để viết một mục báo cáo có số liệu về việc đã thử chưng cất và vì
sao nó không ăn — đó là nội dung mạnh, không phải thất bại đáng giấu.

## 🟡 25/08 — **NHÃN THẦY XONG (600/600). CỔNG TÔI ĐẶT SAI, PHẢI ĐO LẠI CHO ĐÚNG.**

`nhan_thay.json`: **600 câu × 8 = 4.800 cặp, đủ hết**, không nhóm nào thiếu.

| | |
|---|---|
| thầy xếp gold **hạng 1** | **0,5417** (325/600) |
| gold trong **top-2** | 0,7267 (436/600) |
| điểm gold, trung vị | **0,9627** |
| điểm negative, trung vị | **0,1192** |
| negative được chấm **> 0,5** | **1.216/4.200 = 29,0%** |

### ⚠️ CỔNG CŨ (`≥ 0,60`) LÀ MỘT CON SỐ BỐC RA, KHÔNG CÓ MỐC ĐỐI CHIẾU

Nó đo thầy với **đáp án đúng** trên tập negative BM25 khó. Nhưng thứ quyết định có đáng
chưng cất hay không là **thầy có hơn HỌC TRÒ trên đúng những nhóm đó không**.

Hai con số trong bảng cho thấy 0,5417 không đọc được một mình:
- gold 0,9627 vs negative 0,1192 → thầy phân biệt **rất rõ**, không hề lơ mơ.
- **29% "negative" được chấm > 0,5** → chúng là top-20 BM25 trong kho pháp luật, **liên quan
  thật**. Gold không đứng nhất giữa 8 văn bản cùng chủ đề là bình thường.

→ **Đây chính xác là nhóm mà nhãn cứng ép về 0 và làm hỏng model hai lần trước.** Nhãn mềm
giữ được chúng. Con số 29% là bằng chứng định lượng đầu tiên cho luận điểm đó.

⛔ **Đây là lần thứ hai tôi đặt ngưỡng sai** (lần trước: pre-register ≥+2,0 cho `rescore8b`
khi trần oracle chỉ 2,17). **Quy tắc: ngưỡng phải TƯƠNG ĐỐI so với mốc hiện có, không bao
giờ là con số tuyệt đối bốc ra khi chưa biết mốc.**

### ✅ CỔNG MỚI — `congkiem_run.ipynb`, ~5 phút GPU

Chấm đúng 4.800 cặp đó bằng học trò `AITeamVN` rồi so thẳng:

> **`gold@1` thầy − `gold@1` học trò ≥ +0,08** trên cùng 600 nhóm.

- Đạt → nhãn chứa thông tin học trò chưa có → chạy `chungcat_run.ipynb`.
- Không đạt → thầy chỉ biết đúng thứ học trò đã biết → **chưng cất vô nghĩa, dừng hẳn.**

Notebook còn in hai số quan trọng hơn cả cổng: **thầy CỨU được bao nhiêu nhóm học trò đang
sai**, và **làm HỎNG bao nhiêu nhóm học trò đang đúng**. NET âm thì dù Δ dương cũng đừng làm.

## 🧪 25/08 — **BTC CHO PHÉP CHƯNG CẤT. ĐÂY LÀ HƯỚNG DUY NHẤT CÒN TRẦN > +2 ĐIỂM.**

### Bằng chứng ĐÃ CÓ SẴN, 0 giờ GPU (`teach.py`)

Trên 15 câu khó, **cùng một rổ ứng viên**:

| bộ chấm | R@1 | R@5 | R@10 |
|---|---|---|---|
| `ce_ours` (AITeamVN 0,568B) | 0,333 | 0,400 | 0,533 |
| Qwen3-Reranker-**4B** | 0,267 | 0,467 | 0,733 |
| **Qwen3-Reranker-8B** | 0,267 | **0,667** | **0,867** |

Trên **11 câu dev300 mà pipeline ĐANG SAI**: `ce_ours` **2/11** → **8B 6/11**.
→ Trần suy ra cho cả 18 câu sai ≈ **+2,0 điểm dev300**. Lần đầu sau nhiều ngày có một
hướng với trần trên +2.

**⚠️ Phải dùng 8B, KHÔNG dùng 4B** — 4B chỉ hơn `ce_ours` +0,67 ở R@5, gần như vô ích.
(Đây cũng là lý do bảng trên đáng giá: nó chặn ta chọn nhầm model thầy rẻ hơn.)

### 🔑 VÌ SAO CHƯNG CẤT KHÁC HAI LẦN FINE-TUNE ĐÃ THUA (−0,50 rồi −6,50)

Hai lần trước dùng **nhãn cứng**: gold = 1, mọi thứ khác = 0, trên negative BM25 khó.
CLAUDE.md đã ghi đúng nguyên nhân: *"negative quá khó"* — nhiều "negative" thật ra có liên
quan, ép chúng về 0 là **dạy sai**, và nó đè lên thứ AITeamVN vốn làm tốt.

**Nhãn mềm của thầy không có lỗi đó.** Negative liên quan được thầy cho điểm cao; học trò
không bị phạt vì xếp nó cao. Đây là **lý do cơ chế**, không phải hy vọng — và nó khớp với
chẩn đoán thất bại đã ghi từ 19/08.

### 🔒 CỬA HỢP LỆ TRONG `rerank_qwen.py` — `thay_offline=True`

Trần `BUDGET = 3_000_000_000` **giữ nguyên**. Thêm đúng một cửa cho việc sinh nhãn ngoại
tuyến, có in cảnh báo to khi dùng. `thay_label_run.ipynb` còn có `assert` cuối cùng: nếu
notebook đẻ ra bất kỳ file tên chứa `submission` thì **dừng**.
⛔ **Không bao giờ bật cờ này trong notebook sinh bài nộp.**

### 📋 KẾ HOẠCH — THÍ ĐIỂM TRƯỚC, ĐỪNG DỒN 25h VÀO MỘT VÁN

| bước | việc | GPU | cổng để đi tiếp |
|---|---|---|---|
| 1 | `thay_label_run.ipynb` · 600 câu × 8 ứng viên = 4.800 cặp | **~6,3h** | thầy xếp gold hạng 1 ở **≥ 0,60** nhóm |
| 2 | `chungcat_run.ipynb` · LoRA + KL listwise | ~1h | R@5 dev300 tầng 1 **≥ gốc + 0,0100** |
| 3 | mở rộng 2.000–3.000 câu, train lại | ~15h | dev300 hai tầng vượt **0,9400** |
| 4 | chạy đề thi + nộp | ~6h | vượt **0.9118** |

**Bước 1 tốn 6,3h. Nếu cổng bước 2 không đạt thì dừng, mất 7h chứ không phải 25h.**
Fine-tune đã đốt 10h cho hai lần thua — lần này phải có cổng.

### 🛡️ BƯỚC 2 — BA HÀNG RÀO CHỐNG LẶP LẠI −6,50

| | fine-tune cũ | `chungcat_run.ipynb` |
|---|---|---|
| nhãn | **cứng** (gold=1, còn lại=0) | **mềm** — điểm thật của thầy |
| mất mát | cặp rời (BCE) | **KL trên nhóm 8** — học THỨ TỰ |
| tham số đụng vào | **toàn bộ** model | **chỉ LoRA**, gốc ĐÓNG BĂNG |

Hàng rào thứ ba là quan trọng nhất. Nguyên nhân đã ghi của −6,50 là *"huấn luyện tiếp đè lên
thứ AITeamVN vốn làm tốt hơn ta"*. LoRA đóng băng toàn bộ trọng số gốc → **về mặt cơ chế
không thể xoá mất** thứ model đã biết. Đây là hàng rào, không phải lời hứa cẩn thận.

**Chi tiết đã cân nhắc:**
- Điểm thầy là **xác suất** P("yes"). Đưa về **logit** rồi mới softmax — softmax thẳng trên
  xác suất thì mọi nhóm gần như phẳng, mất sạch tín hiệu thứ tự.
- Mốc so sánh (`R@5` của học trò GỐC) được đo **bằng chính đoạn mã đó, trên chính rổ đó**,
  ngay trong cùng notebook. Không so với số chép từ lượt khác — đã có tiền lệ so sai mốc.
- Không đạt cổng thì **không lưu adapter**. Không giữ thứ không dùng được.

### Thiết kế nhãn (đã chốt, có lý do)

- **600 câu × (1 gold + 7 negative BM25)**. Nhóm 8 để chưng cất **listwise** (KL trên softmax
  của nhóm), không phải cặp rời — thứ ta cần học là **thứ tự**, không phải điểm tuyệt đối.
- Trích đoạn **y hệt lúc suy luận**: `DC.pick_chunks(k=1)`, `MERGE_CHARS=1800`, 900 ký tự.
  Lệch chỗ này là nhãn lệch miền, đúng cái bẫy đã ghi.
- Sắp cặp **theo độ dài** trước khi batch → ít phần đệm → nhanh hơn, không đổi kết quả.
- Checkpoint mỗi 200 cặp + trần 9h → hết giờ chạy lại là **chạy tiếp**.

## 🏆 25/08 — **KỶ LỤC MỚI 0.9118** (`submission_matchEmb_M20_n3.zip`). CŨ 0.9109.

**Hàng M=20, rổ `_matchEmbedded`:** n=1 `0.9031` · n=2 `0.9104` · **n=3 `0.9118` ← ĐỈNH** · n=4 `0.9056`

| | n=1 | n=2 | n=3 | n=4 |
|---|---|---|---|---|
| rổ mới, M=10 | — | — | **0.9074** ← đỉnh | — |
| **rổ mới, M=20** | 0.9031 | 0.9104 | **0.9118** ← đỉnh, CHỐT | 0.9056 |
| rổ cũ, M=20 | 0.9059 | **0.9109** ← đỉnh cũ | 0.9101 | 0.8980 |

### ⚠️ TÔI ĐOÁN ĐÚNG SỐ NHƯNG SAI CƠ CHẾ — HAI LẦN

| Đặt trước | Thực tế | |
|---|---|---|
| điểm rơi 0.909–0.912 | **0.9118** | ✅ đúng (sát mép trên) |
| Δ(M10→M20) **< +0,38** vì "rổ tốt → thưởng `M` teo" | **+0,44** (0.9074→0.9118), gần y hệt rổ cũ (+0,46) | ❌ SAI |
| đỉnh `n` dời 3 → 2 vì "đỉnh `n` chỉ phụ thuộc `M`" | đỉnh **VẪN Ở n=3** | ❌ SAI |

**Và lời khuyên "đừng chạy `public_b`" của tôi hôm 24/08 là sai.** Nếu nghe theo thì mất kỷ lục.
Khim quyết định chạy — quyết định đó đúng.

### 🔁 SỬA QUY LUẬT: **CẢ HAI** YẾU TỐ ĐỀU DỜI ĐỈNH `n`, NGƯỢC CHIỀU NHAU

| rổ | đỉnh ở M=10 | đỉnh ở M=20 |
|---|---|---|
| BM25 (cũ nhất) | — | n=2 |
| fusion cũ | n=3 | n=2 |
| **`_matchEmbedded`** | n=3 | **n=3** |

- **`M` lớn hơn → đỉnh `n` DỜI XUỐNG** (reranker khoẻ hơn, ít cần nhường suất cho rổ).
- **Rổ tốt hơn → đỉnh `n` DỜI LÊN** (thứ tự rổ đáng tin hơn, nhường thêm suất thì đáng).
- Trên rổ mới ở M=20, **hai hiệu ứng triệt tiêu nhau** → đỉnh đứng yên ở n=3.

⛔ **Hôm 24/08 tôi đã BÁC BỎ giả thuyết "rổ tốt → đỉnh dời lên" và ghi thành quy luật chốt.
Bác bỏ đó SAI** — bằng chứng khi ấy (cả hai rổ đều đỉnh n=3 ở M=10) không phân biệt được hai
giả thuyết, mà tôi lại coi là đã phân biệt. Giữ M=20 cố định thì thấy rõ: rổ cũ n=2, rổ mới n=3.
**Bài học: "không thấy hiệu ứng ở MỘT điểm đo" ≠ "hiệu ứng không tồn tại".**

## ⛔ 25/08 — **KHÔNG CHẠY M=30. ĐÃ ĐO TRẦN, CHỈ CÒN 2 CÂU.**

Δ(M) chưa hề teo (+0,46 rồi +0,44) nên M=30 nghe rất hợp lý. **Đo trước khi chạy** (`m30.py`,
CPU, vài giây): thứ hạng của gold theo `ce` ở 18 câu dev300 đang sai —

| hạng gold theo `ce` | số câu | M=30 có chạm tới? |
|---|---|---|
| 1–10 | 3 | đã đọc sâu rồi |
| 11–20 | 6 | đã đọc sâu rồi |
| **21–30** | **2** | ✅ **đây là toàn bộ phần M=30 mở thêm** |
| 31–50 | 2 | không |
| ngoài rổ | 5 | không (việc của D) |

→ **Trần tuyệt đối của M=30 = 2/18 câu = +0,67 điểm dev, và đó là trần ORACLE** (giả sử đọc sâu
xong là xếp đúng, điều gần như không xảy ra). Thực nhận sẽ là một phần nhỏ của con số đó.
**~4h GPU. Không đáng.** Ghi lại vì đây là lần "đo trần trước khi chạy" thay vì đoán.

**BÀI CHỐT: `Ketqua_E/submission_matchEmb_M20_n3.zip` — 0.9118.**

## ✅ 24/08 — **BẢNG ABLATION CHỐT Ở 10/11. `gte-multi` BỎ. TÔI ĐOÁN SAI NÓ HAI LẦN.**

`jina-v2` chạy trọn sau miếng vá `create_position_ids_from_input_ids`:
**R@1 0,4383 · R@5 0,7233 · R@10 0,8183 · MRR@10 0,5677 · R@5+RRF 0,8017 · 0,278B · 0,025 s/cặp.**
Xếp **hạng 3** về R@5, sau `bge-v2-m3` (0,7517) và `AITeamVN` (0,7467).

### ❌ `gte-multi` — HAI LẦN CHẨN ĐOÁN SAI, GHI LẠI ĐỂ KHÔNG LẶP

| Lần | Tôi kết luận | Thực tế |
|---|---|---|
| 1 | "kén sm_75+, Pascal thiếu tensor core → đổi accelerator" | Sai. Log ghi `Tesla T4` cả hai lượt. Lỗi phần mềm. |
| 2 | "`type_vocab_size=1` mà tokenizer chấm cặp sinh id 1" | **Sai.** Dòng `[gte-multi] ... đã bỏ token_type_ids` **KHÔNG in ra** → điều kiện không đúng → vá không kích hoạt. |

Lỗi thật vẫn là **tra bảng nhúng ngoài biên** ở lượt truyền xuôi đầu, nhưng ở bảng nào thì
chưa xác định. `CUBLAS_STATUS_NOT_SUPPORTED` trong `F.linear` ở cuối traceback chỉ là **triệu
chứng sau khi CUDA context đã hỏng**, không phải nguyên nhân — đừng đuổi theo nó.

**→ Ghi trong báo cáo là "KHÔNG ĐÁNH GIÁ ĐƯỢC", tuyệt đối không ghi điểm thấp.** Model không
chạy được vì lý do kỹ thuật thì không có quyền xuất hiện như một model kém.

### 🧠 BÀI HỌC PHƯƠNG PHÁP — cách tôi vá đã đúng, cách tôi đoán thì không

Miếng vá jina đúng vì nó đọc **thẳng từ traceback** (`ImportError` nêu đích danh tên hàm).
Miếng vá gte sai vì nó dựa trên **suy đoán về config mà tôi chưa hề in ra kiểm chứng**.
→ **Quy tắc: trước khi vá một assert ngoài biên, IN RA giá trị thật của trần và của chỉ số.**
Vá mù thì chỉ tốn thêm một lượt GPU để biết mình đoán trật.

**Cơ chế an toàn chạy đúng lần thứ ba:** `jina-v2` đã lưu file trước khi `gte-multi` làm sập
context → mất 0 công. Đúng lý do đặt model rủi ro xuống cuối danh sách. Giữ nguyên thiết kế này.

## 🎲 24/08 — **ĐẶT TRƯỚC: CHẠY `public_b` TRÊN RỔ MỚI. GIÁ TRỊ KỲ VỌNG ~HOÀ.**

Chạy vì **GPU đang rỗi và đây là cấu hình cuối cùng chưa ai đo**, không phải vì tin nó ăn.
Việc này **phá quy luật 4 do chính tôi viết 23/08** ("rổ mới về sau CHỈ chạy `public_a`,
BỎ lượt B") — phá có lý do nêu rõ, không phải quên.

**Cấu hình:** `MODE="public_b"` · `RO="_matchEmbedded"` · `TAG="matchEmb_M20"` ·
nạp lại tầng 1 từ `scores_public_fusion_M10_K20_matchEmbedded.json` (bỏ ~2h) → **~4h GPU**.

**DỰ ĐOÁN (viết TRƯỚC khi chạy): 0.909 – 0.912. Mốc phải vượt: 0.9109.**

Suy luận: rổ mới M=10 đỉnh 0.9074. Trên rổ CŨ, M=10→M=20 ăn +0,46 ở đỉnh, nhưng cột Δ
giảm đơn điệu theo `n` (+1,16 · +0,76 · +0,38 · +0,18) và đỉnh mới nằm ở n=3 nơi Δ chỉ +0,38.
Cộng quy luật 4 ("rổ càng tốt thì thưởng của `M` càng teo") → Δ thật **< +0,38**.

**Đỉnh `n` dự kiến DỜI TỪ 3 XUỐNG 2** (quy luật đã chốt: đỉnh `n` chỉ phụ thuộc `M`;
M=10→n=3, M=20→n=2). **Nộp `n=2` trước, rồi `n=3`.**

**Học được gì dù kết quả nào:**
- **> 0.9109** → kỷ lục mới, và quy luật 4 sai ở biên → phải viết lại.
- **0.907–0.911** → quy luật 4 đúng. Đóng hẳn hướng `M`. Giữ 0.9109.
- **< 0.907** → rổ mới tệ hơn hẳn ở M lớn, một kết quả bất ngờ đáng đào.

⛔ Đây là **lượt GPU cuối cho điểm số**. Xong là chuyển toàn bộ sang báo cáo.

## 🧩 24/08 — **HỌ LỖI "TRA BẢNG NHÚNG NGOÀI BIÊN" — ĐÃ DÍNH BA LẦN, GHI LẠI CHO CHẮC**

Lượt `abl_duoi` hỏng cả 2 model trong 256 giây. **Không cái nào hỏng vì phần cứng.**
Đổi T4 ↔ P100 không cứu được — đây là hai lỗi phần mềm thuần.

| Model | Lỗi thật | Vá |
|---|---|---|
| `jina-v2` | `ImportError: create_position_ids_from_input_ids` — mã `trust_remote_code` gọi một hàm **private** của `transformers` mà bản mới đã bỏ. Hỏng lúc **import**, chưa chạm GPU. | Cấy lại hàm đó (3 dòng, nguyên bản cũ) vào module trước khi tải |
| `gte-multi` | `device-side assert: index out of bounds` ngay forward đầu. Config `type_vocab_size = 1` nhưng tokenizer chấm **CẶP** nên sinh `token_type_ids` = 0 **và 1** → tra bảng cỡ 1 bằng chỉ số 1 | Bỏ hẳn `token_type_ids` khi `type_vocab_size <= 1` |

### ⚠️ QUY LUẬT: BA LẦN CHẾT, CÙNG MỘT HÌNH DẠNG

| Lần | Model | Bảng bị tra ngoài biên | Vì sao |
|---|---|---|---|
| 23/08 | `PhoRanker` | **bảng VỊ TRÍ** | PhoBERT `max_position_embeddings=258`, ta đưa 512 |
| 23/08 | `gte-multi` | (chưa rõ, tưởng là vị trí) | thật ra là bảng loại token |
| 24/08 | `gte-multi` | **bảng LOẠI TOKEN** | `type_vocab_size=1`, tokenizer sinh id 1 |

`gioi_han()` viết hôm 23/08 **chỉ canh bảng vị trí** nên không bắt được ca thứ ba.
→ **Trước khi chấm bất kỳ model lạ nào, kiểm CẢ HAI trần từ `config`:**
`max_position_embeddings` (so với `max_length`) **và** `type_vocab_size` (so với việc ta
chấm cặp). Đó là hai bảng tra duy nhất mà đầu vào của ta điều khiển được.

### 💡 BÀI HỌC CHẨN ĐOÁN — tôi đã đổ lỗi cho phần cứng

Tôi từng viết `gte-multi` "kén sm_75+", "Pascal không có tensor core" và khuyên đổi
accelerator. **Sai hướng hoàn toàn.** Cả hai lỗi đều là phần mềm và đọc thẳng ra được từ
log: một cái là `ImportError` (không thể là lỗi GPU), một cái là assert `index out of bounds`
(luôn luôn là chỉ số sai, không bao giờ là card yếu).
→ **`device-side assert` KHÔNG có nghĩa là lỗi GPU.** Nó gần như luôn là một chỉ số vượt
kích thước bảng. Đọc dòng cuối traceback trước khi nghĩ tới phần cứng.

**✅ Cơ chế an toàn chạy đúng lần thứ hai:** bắt lỗi → dọn dẹp trong try riêng →
`cuda_con_song()` phát hiện context chết → `DỪNG SẠCH` → vẫn in bảng. Chết trong 256s
thay vì treo cả phiên. Giữ nguyên khối này.

## 🛑 24/08 — **BA THÍ NGHIỆM CPU, 0 GIỜ GPU, CẢ BA ĐỀU ÂM. NGƯNG TÌM CÁCH NÂNG ĐIỂM.**

Hôm nay thử ba hướng "trộn cho mạnh hơn" hoàn toàn khác nhau. **Cả ba đều thua**, và cả ba
đều thua vì **cùng một lý do**. Đây là lần thứ ba trong một ngày quy luật đó tự lặp lại.

### ① Trộn nhiều bộ chấm (ensemble reranker) — **ÂM, và tôi suýt tin nó**

RRF 3 bộ chấm `AITeamVN + bge-v2-m3 + mMiniLMv2` (1,254B — **hợp lệ** dưới trần 3B):

| | R@5 tầng 1 |
|---|---|
| AITeamVN một mình | 0,7467 |
| ensemble 3 model | **0,7867 (+4,00)** ← nhìn rất ngon |

**Nhưng đối chiếu với pipeline đầy đủ thì lộ:**
```
19 câu ensemble cứu thêm được ở tầng 1
   → 19/19 câu pipeline đầy đủ VỐN ĐÃ làm đúng   (chồng lấp 100%)
   →  0/19 câu là lợi ích thật
 8 câu ensemble LÀM HỎNG, cả 8 pipeline đang đúng
NET = +0 − 8 = −8 câu = −2,67 điểm
```
→ **+4,00 điểm ở tầng 1 là ẢO 100%.** Tầng đọc sâu đã làm sẵn đúng phần việc đó rồi.

*Chỗ duy nhất ensemble có ích thật:* nó kéo gold vào top-10 (suất đọc sâu) ở **4 câu** mà `ce`
không kéo được (3/18 → 5/18). Nhưng tra `oracle13`: 3 trong 4 câu đó có đoạn tốt nhất của
gold chỉ đạt **0,006 / 0,013 / 0,0001** — vô vọng. Chỉ `63832` (0,8648) là có cửa.
→ **Trần thật ≤ 1 câu = +0,33 điểm dev**, đổi lấy **×2,1 giờ GPU tầng 1** và chạy lại toàn bộ. **Không đáng.**

### ② Trộn hai pipeline (rổ cũ M20 ⊕ rổ mới M10) — **ÂM, đo trên dev300**

Hai bài nộp mạnh ngang nhau (0.9109 và 0.9074) mà **lệch nhau cực nhiều**:
`756/1000` câu khác tập 5 id, `218` câu khác cả hạng 1, trung bình chỉ chung 3,85/5 id.
Nhìn thì đúng sách vở: hai hệ mạnh ngang nhau + đa dạng cao = trộn ăn đậm.

**Đo phép tương tự trên dev300** (rổ fusion ⊕ rổ BM25 — cùng kiểu khác biệt, cùng dấu vân
đa dạng: 227/300 khác tập 5, 106/300 khác hạng 1):

| | R@5 dev300 |
|---|---|
| hệ tốt nhất một mình (fusion n=1) | **0,9350** |
| RRF w=1:1 | 0,9250 (**−1,00**) |
| RRF w=2:1 | 0,9250 (−1,00) |
| RRF w=3:1 | 0,9250 (−1,00) |

**Thua ở MỌI trọng số, kể cả 3:1 (gần như chỉ còn hệ A).** Không phải chỉnh trọng số là cứu được.
→ **Sự "đa dạng" 756/1000 kia là NHIỄU giữa các ứng viên xấp xỉ bằng nhau, không phải tín hiệu bù nhau.**
Đã đóng gói sẵn `submission_mix_{1_1,2_1,3_1}.zip` — **ĐỪNG NỘP.** Giữ lại làm bằng chứng đã thử.

### ③ Rổ `_matchEmbedded` của D — **ÂM** (ghi ở mục dưới): dev +3,83 → public +0,11.

---

## ⚖️ QUY LUẬT ĐÃ ĐỦ BẰNG CHỨNG ĐỂ VIẾT VÀO BÁO CÁO

> **Mọi thành phần trong pipeline này đều đang tranh nhau sửa CÙNG một nhóm câu.**
> Cải thiện đo ở một tầng riêng lẻ gần như không cộng vào điểm cuối, vì tầng khác đã sửa xong rồi.

Bốn phép đo độc lập, bốn cơ chế khác nhau, cùng một kết luận:

| Thí nghiệm | Hứa hẹn (đo cô lập) | Thực nhận | Chồng lấp |
|---|---|---|---|
| rổ `_matchEmbedded` của D | recall@5 thô **+3,83** (dev) | **+0,11** (public) | ~97% |
| ensemble 3 bộ chấm | R@5 tầng 1 **+4,00** | **−2,67** | **100%** (19/19) |
| trộn 2 pipeline | 756/1000 câu đa dạng | **−1,00** (dev) | ~toàn bộ |
| enrich tiêu đề (23/08) | cứu 6 câu | 5/6 deepchunk đã cứu | 83% |

**Cách kiểm ĐÚNG cho mọi ý tưởng sau này:** đừng đo cải thiện của thành phần một mình.
Đo **giao với tập câu pipeline đang SAI**. Nếu giao = rỗng thì cải thiện đó bằng 0, dù con số
cô lập đẹp đến đâu. Script mẫu: `overlap.py` (CPU, vài giây).

## 🎯 CÒN LẠI GÌ — ĐÁNH GIÁ THẲNG

dev300 còn **18 câu sai**. Tra `oracle13`: ở phần lớn số đó, **đoạn tốt nhất của chính văn bản
gold** chỉ được CE cho **0,006 · 0,013 · 0,0001 · 1,3e-05**. Đó không phải lỗi xếp hạng,
không phải lỗi chọn đoạn, không phải lỗi truy hồi — **câu hỏi và văn bản gold gần như không
chia sẻ tín hiệu bề mặt nào.** Đổi bộ chấm, thêm bộ chấm, đổi rổ, trộn hệ đều không chạm tới.

→ **Điểm số coi như đã chốt ở 0.9109. Dồn toàn bộ thời gian còn lại vào BÁO CÁO.**
Bảng ablation 9–11 model + bốn phép đo âm ở trên là **nội dung báo cáo mạnh nhất đang có**:
chúng cho thấy đội đã kiểm đúng cách và biết vì sao dừng, chứ không phải thử bừa rồi hết ý.

## 📊 24/08 — **BẢNG ABLATION XONG 9/11 MODEL. `bang_ablation.md` DÁN THẲNG VÀO BÁO CÁO.**

Giao thức: dev300 · rổ fusion top-50 · 1 đoạn/văn bản (BM25 mức đoạn, gộp 1800) ·
chấm MỘT tầng, không đọc sâu · **15.000 cặp giống hệt nhau cho mọi model**. Trần rổ 0.9817.

| Model | Tham số | R@1 | R@5 | R@10 | MRR@10 | R@5 (+RRF) | s/cặp |
|---|---|---|---|---|---|---|---|
| **AITeamVN** ← đang dùng | 0,568B | **0,5017** | 0,7467 | 0,8300 | **0,6178** | **0,8267** | 0,058 |
| bge-reranker-v2-m3 | 0,568B | 0,4683 | **0,7517** | **0,8550** | 0,5994 | 0,8233 | 0,056 |
| mMiniLMv2 | 0,118B | 0,4867 | 0,7217 | 0,8200 | 0,5963 | 0,8117 | **0,007** |
| Qwen3-Reranker-0.6B (decoder) | 0,596B | 0,4133 | 0,7217 | 0,8250 | 0,5627 | 0,8083 | 0,257 |
| PhoRanker | 0,135B | 0,4283 | 0,7200 | 0,8000 | 0,5549 | 0,8217 | 0,014 |
| ViRanker | 0,568B | 0,3917 | 0,6867 | 0,7783 | 0,5182 | 0,7833 | 0,106 |
| bge-reranker-base | 0,278B | 0,3583 | 0,6850 | 0,7733 | 0,5064 | 0,8167 | 0,018 |
| ms-marco-MiniLM-L6-v2 *(đối chứng ÂM, tiếng Anh)* | 0,023B | 0,3233 | 0,5633 | 0,7000 | 0,4421 | 0,7333 | 0,005 |

**Còn thiếu 2: `jina-v2`, `gte-multi`** — hai model `trust_remote_code`, xếp cuối vì tiền sử
làm sập CUDA context. ~20 phút GPU là xong, nên chạy nốt cho trọn bảng.

### 🔁 TÔI ĐÃ SỬA SAI RỒI SAI LẠI — `thanhtantran/Vietnamese_Reranker` ĐÚNG LÀ BẢN SAO

Ban đầu tôi bảo nó là bản sao của AITeamVN. Rồi tra web thấy tác giả khác (Nguyễn Nho Trung,
Nguyễn Nhật Quang, Nguyễn Văn Huy) nên **tự "sửa lại" thành "đội khác, cùng nền"**. Sai.
Đo thẳng: điểm hai model **trùng khít từng bit trên cả 15.000 cặp, lệch tối đa 0,000e+00**.
Khác tài khoản HF, **cùng trọng số**. Đã loại khỏi bảng.
→ **Bài học: metadata trên web không phủ định được phép đo. Chạy thử rồi so số, đừng tra tiểu sử.**

### 🔑 BỐN KẾT LUẬN CHO BÁO CÁO

1. **Model đang dùng là lựa chọn đúng** — AITeamVN dẫn đầu ở R@1, MRR@10 và R@5 sau pha rổ,
   đúng ba chỉ số pipeline phụ thuộc. Chỉ thua nền của chính nó (`bge-v2-m3`) ở R@5 thuần
   −0,50, đổi lại R@1 +3,34 và MRR +1,84. Với bài chỉ nộp 5 đáp án, đánh đổi này có lợi.
   → **KHÔNG đổi model. Đây là dòng cho báo cáo, không phải cần gạt.**
2. **Tham số không dự đoán chất lượng** — `mMiniLMv2` 0,118B (0,7217) hơn `ViRanker` 0,568B
   (0,6867) **+3,50 điểm**, nhỏ hơn 4,8 lần, nhanh hơn 16 lần. Quyết định là **dữ liệu huấn
   luyện tiếng Việt/pháp lý**, không phải kích thước. (Củng cố trần 3B của BTC không phải rào cản.)
3. **Decoder không tự động tốt hơn** — Qwen3-Reranker-0.6B đúng 0,7217, **bằng** mMiniLMv2
   0,118B, mà chậm hơn **40 lần**. Khớp với hard15: decoder lớn hơn không mở ra nhóm câu mới.
4. **Đối chứng âm chạy đúng** — `ms-marco-MiniLM-L6-v2` (BERT tiếng Anh) rơi xuống 0,5633,
   cách nhóm dẫn đầu 18,8 điểm → bảng đo đúng năng lực tiếng Việt, không phải nhiễu.

## 🔴 24/08 — **RỔ `_matchEmbedded` KHÔNG CHUYỂN ĐƯỢC SANG PUBLIC. NHÁNH "THẤT BẠI" ĐÃ ĐẶT TRƯỚC ĐÃ NỔ.**

**Đỉnh `n=3` = 0.9074. Mốc phải vượt là 0.9109. KHÔNG VƯỢT.**
Bài chốt vẫn là **`submission_fusion_M20_n2.zip` = 0.9109** (rổ fusion cũ).

### So đúng cặp — cùng M=10, cùng n=3, chỉ khác rổ

| | recall@5 thô trên dev300 | public LB (M=10, n=3) |
|---|---|---|
| rổ fusion cũ | 0.8733 | 0.9063 |
| rổ `_matchEmbedded` | **0.9117** (+3,83) | **0.9074** (+0,11) |

**dev300 hứa +3,83 điểm recall thô, public trả về +0,11.** Tỉ lệ chuyển giao ≈ **3%**.
Từ trước tới nay mọi cải tiến đều chuyển dev→public **≥ 100%** (deepchunk 104%, M 192%,
rổ fusion vượt dự báo). Đây là **lần đầu tiên một cải thiện lớn không ăn gì cả.**

### 🧠 VÌ SAO — đây là bằng chứng TRỰC TIẾP cho "một nút thắt bão hoà"

Kết luận lớn nhất của phiên 23/08 nói: các hướng cải tiến **chồng lên nhau chứ không cộng
dồn**, vì tất cả cùng đánh vào một nút thắt. Lần này rổ của D và reranker của E chồng nhau:
**những gold mà D vừa kéo lên top-5 thì reranker VỐN ĐÃ lôi được chúng từ sâu trong rổ ra rồi.**
Recall@5 thô tăng thật, nhưng nó tăng ở đúng những câu pipeline đã làm đúng.

Khớp với con số đã ghi 23/08: đóng góp của reranker teo từ **+6,17 → +2,33** khi đổi rổ.
Không phải reranker yếu đi — mà là **rổ đã tự làm phần việc reranker vẫn đang làm**.

**→ DỰ BÁO: các đợt nâng recall tiếp theo của D cũng sẽ KHÔNG ăn.** Chỗ còn lại là 9 câu
"vô vọng" — đoạn tốt nhất của chính văn bản gold vẫn thua. Đó không phải bài toán truy hồi.

### ✅ GIẢ THUYẾT "RỔ TỐT HƠN → ĐỈNH `n` DỜI LÊN" — BÁC BỎ LẦN THỨ HAI, LẦN NÀY SẠCH

Đỉnh vẫn ở **n=3**, y hệt rổ fusion cũ ở cùng M=10, dù rổ mới tốt hơn hẳn.
Cộng với phép so cũ (giữ M=20: BM25 đỉnh n=2, fusion cũng đỉnh n=2 → hiệu ứng rổ = 0):

> **QUY LUẬT CHỐT: đỉnh `n` chỉ phụ thuộc `M`, KHÔNG phụ thuộc chất lượng rổ.**
> M=10 → n=3. M=20 → n=2. Đổi rổ thì KHỎI quét lại `n`; đổi `M` thì PHẢI quét.

### ⛔ KHÔNG CHẠY `public_b` (M=20) TRÊN RỔ MỚI

Ước tính: 0.9074 + (M=10→M=20 ở đỉnh, rổ cũ ăn +0,46) ≈ **0.912**, và theo kết luận 4 ngày
23/08 ("rổ càng tốt thì phần thưởng của `M` càng teo") thực tế sẽ **thấp hơn 0,46**.
→ **4h GPU đổi lấy khoảng +0,1 điểm bấp bênh.** Không đáng.
**Dồn GPU còn lại vào bảng ablation cross-encoder cho báo cáo** — giá trị chắc chắn, không rủi ro.

### 📁 Đổi tên file (24/08) — tên cũ quá dài

`submission_fusion_matchEmbedded_M10_n*.zip` → **`submission_matchEmb_n*.zip`** (trong `Ketqua_E/`).
Trong `fusion_v3_run.ipynb` đã thêm biến **`TAG = "matchEmb"`**; tên bài nộp giờ là
`submission_{TAG}_n{n}.zip`. Chạy `public_b` thì đặt `TAG = "matchEmb_M20"` để khỏi đè file.

## 🚀 24/08 — **5 BÀI NỘP `_matchEmbedded` ĐÃ KIỂM XONG. NỘP THEO THỨ TỰ n=2 → n=1 → n=3.**

`fusion_v3_run.ipynb` MODE=`public_a` chạy xong trên rổ mới của D. Đã kiểm cả 5 zip:

| n | số câu | zip (byte) | đủ 5 id/câu |
|---|---|---|---|
| 0 | 1000 | 22.351 | ✅ |
| 1 | 1000 | 22.372 | ✅ |
| 2 | 1000 | 22.429 | ✅ |
| 3 | 1000 | 22.491 | ✅ |
| 4 | 1000 | 22.408 | ✅ |

Tập qid giống hệt nhau ở cả 5 bài. **Số câu khác nhau (khác TẬP 5 id):**

```
        n=0    n=1    n=2    n=3    n=4
n=0       0    162    437    697    853
n=1     162      0    353    663    842
n=2     437    353      0    554    807
n=3     697    663    554      0    679
n=4     853    842    807    679      0
```

→ `n` **không** phải tham số vặt: n=0 và n=4 lệch nhau **853/1000 câu**. Phải chốt trên public LB.

**🔴 SỬA THỨ TỰ NỘP (24/08, sau khi soi lại bảng M × n).** Ban đầu tôi nói `n=2 → n=1 → n=3`.
**SAI** — tôi đọc hàng **M=20** trong khi lượt vừa chạy là **M=10**. Hai hàng có đỉnh khác nhau:

| | n=0 | n=1 | n=2 | n=3 | n=4 |
|---|---|---|---|---|---|
| M=10, rổ fusion cũ | 0.8775 | 0.8943 | 0.9033 | **0.9063** ← đỉnh | 0.8962 |
| M=20, rổ fusion cũ | — | 0.9059 | **0.9109** ← đỉnh | 0.9101 | 0.8980 |

**THỨ TỰ ĐÚNG: `n=3` → rồi mới quyết. MỐC PHẢI VƯỢT: 0.9109.**

**Vì sao n=3:** hiệu ứng `M` là bằng chứng SẠCH duy nhất — cùng rổ fusion, M=10 đỉnh n=3,
M=20 đỉnh dời xuống n=2. Lượt mới là M=10 → dự đoán đỉnh **n=3**.

**⚠️ Sửa luôn một suy luận cũ sai trong mục 3 ngày 23/08:** ở đó tôi viết "rổ tốt hơn →
đỉnh `n` dời lên", căn cứ BM25 M=20 (n=2) vs fusion M=10 (n=3) — **so lẫn hai biến**.
Giữ `M=20` cố định thì BM25 đỉnh n=2, fusion cũng đỉnh n=2: **hiệu ứng rổ = 0**.
Vậy "rổ mới tốt hơn nên nới `n`" là **giả thuyết CHƯA được kiểm**, không phải quy luật.

**Đặt trước:** nộp `n=3`. Dự báo 0.913–0.920.
- `n=3` ≥ 0.9109 → rổ mới ăn. Nộp tiếp **`n=4`** (kiểm đúng giả thuyết "rổ tốt → đỉnh dời lên",
  hướng duy nhất chưa ai kiểm và là hướng có upside). Rồi `n=2` nếu cần chặn đầu kia.
- `n=3` < 0.9109 → rổ mới KHÔNG chuyển được sang public. Giữ `submission_fusion_M20_n2.zip`
  (0.9109) làm bài chốt, và ghi nhận đây là lần đầu một cải thiện recall lớn của D không ăn.

⛔ **Đừng chọn `n` bằng dev300** — dev300 đã lừa về `n` ba lần (11/08, 18/08, 22/08).

**🐛 LỖI ĐÃ SỬA (24/08):** trong `CFG`, phần tử thứ 4 của mỗi tuple là chuỗi thường
chứ không phải f-string → file ra tên **`scores_public_fusion_M10_K20{RO}.json`** (có `{RO}`
in nguyên chữ). Vô hại cho lượt `public_a` này, nhưng `PREV` ở nhánh `public_b` **là** f-string
nên sẽ đi tìm `..._matchEmbedded.json` và không thấy. Đã sửa 4 dòng thành f-string.
→ Nếu chạy `public_b`, phải **đổi tên** file đã có thành `scores_public_fusion_M10_K20_matchEmbedded.json`
trước khi upload, hoặc chạy lại `public_a` bằng notebook đã sửa.

## 🟢 23/08 KHUYA — **D GIAO RỔ MỚI `_matchEmbedded`. VƯỢT NGƯỠNG. ĐÂY LÀ VIỆC TIẾP THEO.**

D chạy lại khâu truy hồi bằng embedding **khớp với `Vietnamese_Reranker`**. Kiểm trên CPU,
0 giờ GPU, trên đúng dev300:

| recall@k | rổ fusion CŨ | **rổ `_matchEmbedded`** | Δ điểm |
|---|---|---|---|
| @1 | 0.5783 | **0.6217** | **+4,33** |
| @3 | 0.8083 | 0.8450 | +3,67 |
| **@5 thô** | 0.8733 | **0.9117** | **+3,83** |
| @10 | 0.9317 | 0.9517 | +2,00 |
| @20 | 0.9633 | 0.9667 | +0,33 |
| **@50 (TRẦN)** | 0.9817 | **0.9883** | **+0,67** |

**✅ NGƯỠNG ĐẶT TRƯỚC (recall@50 > 0.9817) ĐÃ VƯỢT.** Theo đúng việc 3 đã ghi → đáng chạy.

**Ba phép kiểm CPU nữa, đều sạch:**

1. **Nhặt được 2/5 câu gold ngoài rổ** (`66564`, `83676`) · **không mất câu nào.**
   Còn lại 3 câu ngoài rổ: `112344` `12654` `162336`.
2. **Cấu trúc y hệt rổ cũ** — `doc_id` · `name` · `rrf_score` · `top_chunks{bm25_score,
   chunk_id,text}` · 50 ứng viên/câu · 1000 câu cả hai file. `fusion_run` chạy được ngay,
   chỉ đổi tên file. Tầng 1: **99.295 đoạn ≈ 2,1h**, y hệt rổ cũ (99.213) → **chi phí không đổi**.
3. **Trùng 74% văn bản với rổ cũ** (37/50) → 26% văn bản mới. Đổi thật, không phải xáo lại.

**Gỡ được cổng M=20 bao nhiêu?** Chỉ **1/5**: `63832` từ hạng tầng-1 21 → ~16, tức lọt vào
M=20 và **được đọc sâu** — mà oracle13 đã đo đoạn tốt nhất của nó là **0,865** so với ngưỡng
**0,165**, nên gần như chắc chắn cứu được. Bốn cái kia (`49070` 42→32 · `16942` 40→33 ·
`65498/285041` 40→35 · `64622` 28→26) vẫn ngoài M=20. *(Ước LẠC QUAN: 26% văn bản mới chưa
có điểm nên chưa cạnh tranh — hạng thật có thể tệ hơn.)*

**⚠️ Hai câu mới nhặt được nằm ở hạng 34 và 25 theo thứ tự rổ** (`66564/98731` hạng 34 ·
`83676/74494` hạng 25). Cổng M gác bằng **`ce` tầng 1**, không phải thứ tự rổ, nên **không
suy ra được từ CPU** là chúng có được đọc sâu hay không. Đừng tính chắc +0,67 cho chúng.

**Cộng lại: +0,33 khá chắc (`63832`) · tối đa +0,67 chưa rõ (2 câu mới) · phần thứ tự rổ
tốt hơn chưa ước được ≈ +0,3…+1,5 điểm dev.** Vẫn **dưới ngưỡng đo được của dev300**.
Kèm rủi ro thật: **26% văn bản MỚI là 26% đối thủ mới**, có thể đánh bật câu đang đúng.

### 🔑 SỐ ĐÁNG NHỚ NHẤT: PHẦN ĐÓNG GÓP CỦA RERANKER ĐANG TEO ĐI RẤT NHANH

| | recall@5 |
|---|---|
| rổ CŨ, thứ tự thô (không reranker) | 0.8733 |
| + reranker = pipeline chốt | **0.9350** → reranker thêm **+6,17** |
| **rổ MỚI, thứ tự thô (không reranker)** | **0.9117** → chỉ kém pipeline **2,33** |
| trần rổ mới | 0.9883 |

**Rổ mới, chưa cần bộ chấm nào, đã gần bằng cả pipeline hai tầng chạy trên rổ cũ.**
Công của E co từ +6,17 xuống còn tối đa ~2,3 điểm ở vùng đó. → Hệ quả chiến lược: **D
càng khá thì phần của E càng nhỏ**, và cần gạt đáng vặn nhất bây giờ là **`n`** — nghiêng
nhiều hơn về thứ tự rổ. Đúng lý do notebook quét `n = 0…4` thay vì chỉ (1,2).

### → CHẠY THẲNG `public_a`, ĐỪNG CHẠY dev. Lý do là quyết định, không phải lười.

Kỳ vọng ~+1,0 mà sàn nhiễu dev300 là ±1,5 câu (±0,5 điểm) — **dev300 không phân giải nổi**.
Chạy dev là đốt 3h để lấy một con số không đọc được, đúng cái bẫy đã ghi ở quy tắc 4.
Dụng cụ duy nhất đọc được mức này là **public LB**, và nó miễn phí. Đúng như việc 3 đã ghi
sẵn: *"Rồi CHỈ chạy `public_a`, bỏ lượt B."*

**`fusion_v3_run.ipynb`** (mới) = `fusion_run` + ba sửa đổi:
`RO = "_matchEmbedded"` chọn rổ bằng một dòng (để `""` là quay về rổ cũ) · tên file scores
và submission mang dấu rổ nên **không đè lên kết quả rổ cũ** · quét **n = 0…4** thay vì
chỉ (1,2), vì **đổi rổ thì đỉnh `n` dời** (kết luận 3) và quét thêm tốn **0 giờ GPU**.

**Nộp theo thứ tự `n=2` → `n=1` → `n=3`. MỐC PHẢI VƯỢT: 0.9109.**
⛔ **Đừng chọn `n` bằng dev300** — nó đã lừa về `n` **ba lần** (11/08, 18/08, 22/08).

**Upload lên dataset:** `fusion_rrf_top50_public_matchEmbedded.json` (207MB). Bản dev1000
chỉ cần nếu sau này muốn chạy `MODE=dev`.

## ⛔⛔ RÀNG BUỘC CỨNG — ĐỌC TRƯỚC KHI CHỌN BẤT KỲ MODEL NÀO

> **LUẬT BTC: tổng cả đội 4B tham số. D đã lấy 1B (khâu truy hồi). E CÒN 3B.**
> Đây **không** phải giới hạn phần cứng. **Lượng tử hoá KHÔNG nới được** — 4 bit chỉ đổi
> chỗ chứa, số tham số không đổi.

| model | tham số thật | E dùng được? |
|---|---|---|
| **AITeamVN/Vietnamese_Reranker** ← đang dùng | **0,568B** | ✅ còn dư ~2,4B |
| Qwen3-Reranker-0.6B | 0,596B | ✅ |
| Qwen3-Reranker-**4B** | **4,02B** | ❌ tên là "4B" nhưng thật là 4,02B — vượt cả trần đội |
| Qwen2.5-7B-Instruct | ~7,62B | ❌ |
| Qwen3-Reranker-**8B** | **8,19B** | ❌ gấp gần 3 lần suất của E |

**23/08 đã dính:** tôi tưởng `BUDGET = 3_000_000_000` là giới hạn bộ nhớ T4 nên cho
`load_4bit=True` đi vòng qua, rồi chạy hết 4B và 8B trên hard15. **Cả hai kết quả không
dùng cho bài nộp được.** Đã sửa `rerank_qwen.py`: ngân sách áp không ngoại lệ.

Bẫy phụ khiến phép kiểm cũ vô dụng: dưới NF4, bitsandbytes gói 2 trọng số vào 1 byte
`uint8`, nên `sum(p.numel())` báo **chưa tới một nửa** số thật — Qwen3-Reranker-4B báo
**2,205B** cho một model **4,02B**. Hàm `_real_params` nhân đôi phần `uint8`; test trong
`__main__` dựng lại đúng con số 2.205.126.656 của log và bắt buộc nó bị chặn.

→ **Mọi model mới phải kiểm số tham số THẬT trước khi chạy.** Tên repo không đáng tin.

### 🔒 RÀNG BUỘC THỨ HAI, VỪA PHÁT HIỆN 23/08: **DANH SÁCH TRẮNG MODEL**

Tra thể lệ (bản 2025 công khai, 2026 chưa đăng bản chi tiết):
**"Base-LLM phải nằm trong danh sách trắng của BTC"** · **"mọi LLM thương mại (GPT-4o,
Gemini, Claude...) sẽ không được chấm điểm"** · **"chỉ dùng dataset chính thức do BTC phát
hành, cấm gán nhãn tay và thu thập dữ liệu ngoài"**.

**⛔ `Qwen3-Reranker-8B` KHÔNG CÓ TRONG DANH SÁCH TRẮNG.** Danh sách chỉ có
`Qwen/Qwen3-Reranker-0.6B`. Vậy 8B bị chặn **hai lần** — vượt ngân sách **và** ngoài danh
sách. **Hướng distillation từ 8B coi như chết**, trừ khi xin BTC duyệt riêng.

**Xác nhận gián tiếp cho con số 4B:** cả danh sách trắng **kịch trần ở ~4B** — `Qwen3-4B`,
`Qwen3.5-4B`, `Qwen3-Embedding-4B`, `F2LLM-4B`, `Octen-Embedding-4B`, `PhoGPT-4B-Chat`.
**Không một model nào 7B/8B.** Khớp với ngân sách 4B, dù thể lệ công khai không ghi số.

**🔑 CÓ CỬA MỞ, VÀ CÓ HẠN CHÓT:** thể lệ cho phép **"gửi đề xuất bổ sung model mã nguồn mở
mới trước 10 ngày so với hạn private-test"**. Muốn model nào ngoài danh sách thì đây là
đường duy nhất — và nó có deadline, đừng để lỡ.

**⚠️ Chưa xác minh được:** con số 4B không có trong bất kỳ trang công khai nào tra được.
Nó đến từ tài liệu nội bộ của đội. **Cần đọc lại nguyên văn** — "mỗi model ≤4B" khác
"cả pipeline ≤4B" khác "cả đội ≤4B", và ba cách hiểu cho ba kế hoạch khác nhau.

## ▶ TRẠNG THÁI 23/08 — **MỐC MỚI 0.9109.** Rổ fusion đã chạy đề thi xong. Đọc mục này trước.

> **Bài chốt: `Ketqua_E/submission_fusion_M20_n2.zip` — public LB 0.9109.**
> Từ 0.8871 lên 0.9109 = **+2,38 điểm ≈ 24 câu** trong một ngày. Khoảng cách tới đỉnh
> bảng (0.95) thu từ 6,3 xuống **3,9 điểm**.

### Bảng đầy đủ 9 lượt nộp 22–23/08 — quét trọn hai chiều M × n

| | n=0 | n=1 | n=2 | n=3 | n=4 |
|---|---|---|---|---|---|
| **M=10** (lượt `public_a`) | 0.8775 | 0.8943 | 0.9033 | **0.9063** ← đỉnh | 0.8962 |
| **M=20** (lượt `public_b`) | — | 0.9059 | **0.9109** ← đỉnh, CHỐT | 0.9101 | 0.8980 |
| **Δ M=20 − M=10** | — | +1,16 | +0,76 | +0,38 | +0,18 |

Mốc cũ để so: `submission_v2_M20_n2` (rổ BM25) = 0.8871.

### SÁU KẾT LUẬN — đọc hết trước khi làm gì tiếp

**1. Rổ fusion ăn thật và ăn to.** Ngay lượt M=10 đã 0.9033 (+1,62 so 0.8871).
dev300 dự báo +1,00 → lại vượt dự báo, đúng khuôn deepchunk (dev +2,00 / public +2,67).

**2. ⛔ dev300 LỪA VỀ `n` LẦN THỨ BA. NGỪNG DÙNG NÓ CHO THAM SỐ NÀY.**

| n | dev300 (fusion) | public M=10 | lệch |
|---|---|---|---|
| 0 | 0.9283 | 0.8775 | −5,08 |
| 1 | **0.9350** ← đỉnh dev | 0.8943 | −4,07 |
| 2 | 0.9283 | **0.9033** ← đỉnh public | −2,50 |

Độ lệch dev→public **không hằng số**, chạy từ −2,50 tới −5,08 **tuỳ `n`**. Đó là bằng chứng
dứt khoát: dev300 không đo được cần gạt này. (11/08 chốt n=1 rồi bị lật · 18/08 báo n=0 mà
public nói n=2 · 22/08 báo n=1 mà public nói n=2/n=3.)
→ **Mọi cấu hình `n` sinh offline từ file scores, 0 giờ GPU. Nộp cả dải, để public LB quyết.**

**3. ĐỈNH `n` DỜI THEO `M` — cơ chế, đã dự đoán TRƯỚC khi đo và đúng.**
M=10 đỉnh n=3; M=20 đỉnh dời ngược về n=2. Lý do: `M` lớn = reranker khoẻ hơn →
`blend_bm25_first` hết chỗ dụng võ, đúng quy luật đã ghi từ 19/08. Đỉnh `n` trên rổ BM25 cũ
là n=2, trên rổ fusion M=10 là n=3 (rổ xếp hạng tốt hơn → nhường thêm suất thì đáng).
**Hai cơ chế đối nghịch, cả hai đều xác nhận. Đổi M hoặc đổi rổ thì phải quét lại `n`.**

**4. 🔑 RỔ CÀNG TỐT THÌ PHẦN THƯỞNG CỦA `M` CÀNG TEO — đổi hẳn kế hoạch chi phí.**
So đỉnh với đỉnh, M=20 chỉ ăn **+0,46** (0.9063 → 0.9109), trong khi trên rổ BM25 cũ
M=10→M=20 ăn **+1,27**. Cột `Δ` ở bảng trên giảm đơn điệu theo `n` (+1,16 → +0,18), khớp
chính xác số câu lệch giữa hai lượt (337 → 303 → 242 → 164 → 83).
→ **Lượt B tốn 4h GPU cho 0,46 điểm. Rổ mới về sau CHỈ CHẠY `public_a` (~5,7h), BỎ lượt B.**
Tiết kiệm 4h mỗi lần đổi rổ. Chỉ chạy lượt B nếu có lý do cụ thể.

**5. ⛔ CỔNG LỌC THEO ĐỘ TỰ TIN — ĐO LẠI TRÊN RỔ FUSION 23/08, CHẾT HẲN.**
Giả thuyết: `max` điểm cả rổ thấp = reranker không chắc → nới `n`. Quét 7 ngưỡng
(0,02…0,70) × 4 mức `n_lo` (2…5) trên `scores_dev300_fusion_M20_K20.json`, CPU, 0 giờ GPU.
**Không một ô nào vượt mốc 0.9350.** Tốt nhất là hoà, còn lại đều hại. Cùng kết luận 19/08
nhưng nay đã xác nhận trên rổ có bi-encoder. **ĐÓNG VĨNH VIỄN, gạch khỏi mọi danh sách.**

**6. Nhóm "cả rổ chấm ~0" gần như biến mất trên rổ fusion — chỉ còn 1 câu.**
Ước trước đó là 5–6 câu, sai. Rổ tốt hơn → ứng viên đầu bảng liên quan hơn → được chấm cao
hơn. **Bài học: đừng ngoại suy chẩn đoán từ rổ cũ sang rổ mới.**

### Chẩn đoán còn sai — dev300, cấu hình `max n=1` (0.9350)

Sai 18 câu · **13 câu gold VẪN trong rổ 50** = **4,33 điểm dư địa thuộc khâu xếp hạng**.

| qid | max điểm rổ | điểm gold | hạng gold | ngưỡng vào top-5 |
|---|---|---|---|---|
| 1524 | 1.0000 | 0.26096 | 8 | 0.6228 |
| 16942 | 1.0000 | 0.00023 | 40 | 0.9004 |
| 138214 | 0.9971 | 0.46892 | 10 | 0.9654 |
| 65498 | 0.9952 | 0.01057 | 40 | 0.9487 |
| 63832 | 0.9919 | 0.00112 | 21 | 0.1646 |
| **119400** | 0.9614 | 0.00035 | 10 | **0.0253** |
| 64622 | 0.9587 | 0.00398 | 28 | 0.5991 |
| 144234 | 0.9540 | 0.14827 | 9 | 0.2801 |
| 92466 | 0.8716 | 0.12296 | 7 | 0.1423 |
| 49070 | 0.6189 | 0.00017 | 42 | 0.3984 |
| **159444** | 0.2819 | 0.00051 | 19 | **0.0137** |
| **8946** | 0.1150 | 0.01302 | 7 | **0.0166** |
| **37542** | 0.0111 | 0.00007 | 9 | **0.0006** |

**12/13 câu có đối thủ được chấm 0,87–1,00** → máy **tự tin VÀ sai**, không phải "không có
ý kiến". Đó là lý do cổng lọc theo độ tự tin chết.

**4 câu in đậm có ngưỡng dưới 0,03** — bar cực thấp mà gold vẫn bị chấm ~0. Đúng nhóm mà
mô hình khác loại bắt được 10/15. **Đây là mục tiêu cụ thể, đo được, cho việc thử model mới.**
6/13 câu có gold ở hạng 7–10, tức sát ngay ngoài top-5.

### VIỆC TIẾP THEO — thứ tự không đổi

1. **Model khác loại trên 15 câu khó** — ✅ **CÔNG CỤ ĐÃ XONG 23/08, chờ một lượt GPU.**
   `hard15_run.ipynb` (mới) + `rerank_qwen.py` (đè bản cũ). Xem mục riêng ngay dưới.
2. **Làm giàu đoạn — ✅ LÊN SỐ 1, notebook `enrich_run.ipynb` đã xong 23/08.**
   Lưu ý: trần "chọn đoạn còn +0,67" áp cho việc CHỌN trong đám đoạn đang có; làm giàu
   tạo văn bản MỚI nên nằm ngoài trần đó. Xem mục riêng dưới.
3. **Rổ mới của D** (`AITeamVN/Vietnamese_Embedding` thay bge-m3 gốc) — khi nhận:
   **kiểm recall@50 trên CPU vài giây TRƯỚC**, phải vượt **0.9817** mới đáng chạy.
   Rồi CHỈ chạy `public_a`, bỏ lượt B (kết luận 4).
4. **Fine-tune: TREO.** Vòng luẩn quẩn — muốn nhãn mức đoạn sạch cho nhóm bảng/danh mục thì
   cần một model đọc được bảng, mà có model đó rồi thì có khi khỏi cần fine-tune. Lối ra duy
   nhất là **distillation**: dùng model giỏi dán nhãn ~140 ca khó (~6.000 lượt đọc, vài chục
   phút) rồi dạy cross-encoder rẻ. Chỉ làm SAU khi việc 1 có kết quả.

### 🔴 CHỐT 23/08 TỐI — HAI LƯỢT ĐÃ XONG. **8B TRÙNG KHÍT GEMINI. LÀM GIÀU ĐOẠN VÀO VÙNG MÙ.**

#### A. Việc 1 chạy đủ 4 model — **Qwen3-Reranker-8B bắt 10/15, ĐÚNG BẰNG VÀ ĐÚNG NHỮNG CÂU Gemini bắt**

| qid | `ce_ours` 0,6B | 4B | **8B** | Qwen2.5-7B-Ins | Gemini |
|---|---|---|---|---|---|
| 112344 · 128326 · 156454 · 52126 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 33938 · 159444 | ✓ | · | ✓ | 1/2 | ✓ |
| 119400 · 49070 | · | ✓ | ✓ | 1/2 | ✓ |
| 138214 · 92466 | · | · | ✓ | · | ✓ |
| 65498 | · | ✓ | · | · | · |
| **1524 · 16942 · 37542 · 8946** | · | · | · | · | · |
| **TỔNG** | **6** | **7** | **10** | **6** | **10** |

**Ba điều đọc được, cái thứ hai là cái đáng giá nhất:**

1. **Thang theo cỡ model, trong cùng một họ:** 0,6B → 6 · 4B → 7 · 8B → 10. Đơn điệu.
2. **Tập 10 câu của 8B TRÙNG KHÍT tập 10 câu của Gemini** (giao 10, hợp cũng 10), và
   **bao trùm hẳn `ce_ours`** — thêm `119400` `138214` `49070` `92466`, **không mất câu nào**.
   Một reranker mã nguồn mở 8B tái lập **y hệt** hành vi của một LLM thương mại đời mới,
   trên tập câu được chọn TRƯỚC bằng lỗi của bên thứ ba. Đây không phải nhiễu.
   → **Kế hoạch B cho vụ "BTC cấm API ngoài" đã có lời giải cụ thể, có tên model.**
3. **4 câu `1524` `16942` `37542` `8946` không bộ chấm nào bắt được** — cả 5 bộ đều trượt.
   Lõi cứng thật sự, đừng đổ cho bộ chấm nữa.

**Qwen2.5-7B-Instruct chỉ 6/15, hạng 1 chỉ 1/15** → model chat thường KHÔNG thay được
reranker chuyên dụng ở cơ chế pointwise. Đóng nhánh đó.

**⛔ HAI THỨ CHẶN 8B, chưa cái nào được đo:**

**🛑 CHỐT CUỐI 23/08: 8B VÀ 4B ĐỀU VƯỢT NGÂN SÁCH BTC → KHÔNG DÙNG ĐƯỢC CHO BÀI NỘP.**
Xem mục ràng buộc cứng ở ĐẦU FILE. E chỉ có 3B; 8B là 8,19B, 4B là 4,02B. **Toàn bộ phần
tính chi phí và ngưỡng bên dưới đã thành lịch sử** — `rescore8b_run.ipynb` **ĐỪNG CHẠY**.
Giữ lại vì hai thứ vẫn còn giá trị:

1. **Số đo thì vẫn thật.** 8B = 10/15, trùng khít Gemini, bao trùm `ce_ours`. Nó chứng
   minh **cơ chế** có tồn tại, chỉ là mình không được phép dùng cỗ máy đó.
2. **Cửa còn lại duy nhất của trục model: DISTILLATION.** Dùng 8B **ngoại tuyến** dán nhãn
   ca khó rồi dạy một model ≤3B — đúng mục "việc 4" đã ghi. **Phải hỏi BTC trước:** luật
   cấm model >4B *lúc suy luận*, hay cấm cả việc dùng nó để **sinh dữ liệu huấn luyện**?
   Hai câu trả lời khác nhau hoàn toàn. Hỏi mất 5 phút, và `scores_hard15_qwen3rr8b.json`
   đã nằm sẵn trên máy nếu được phép.

**⚠️ Và thang theo cỡ model nói điều không vui:** 0,6B → 6 · 4B → 7 · **8B → 10**. Bước
nhảy nằm giữa 4B và 8B, tức **ngoài tầm với**. Trong khoảng ≤3B thì `ce_ours` 0,568B đã
được 6/15 rồi — một model 2–3B nhiều khả năng chỉ hoà hoặc hơn 1 câu. **Trục "đổi model"
coi như đóng vì ngân sách**, trừ khi distillation được phép. Dồn sức sang việc 2.

<details><summary>(lịch sử) tính chi phí 8B — giữ để tham chiếu, không còn dùng</summary>

**ĐÃ CÓ SỐ TỐC ĐỘ. TÔI NÓI SAI Ở LƯỢT TRƯỚC — 8B KHÔNG CHẾT VÌ CHI PHÍ.**

Đo thật: `ce_ours` 0,128 s/cặp · 4B **2,62** · 8B **4,69** · Qwen2.5-7B 4,40.
8B chậm hơn model đang dùng **37 lần**. Tôi lấy con số đó nhân với TOÀN BỘ 157.008 đoạn
của đề thi rồi tuyên "113 giờ, chết". **Sai ở chỗ đặt vai trò**: 8B chưa bao giờ định làm
bộ chấm chính — vai của nó là **chấm lại DANH SÁCH NGẮN** ("3 mình + 2 model ngoài",
19/08). Tính lại theo đúng vai:

| việc | cặp | giờ @8B | |
|---|---|---|---|
| **dev300 top-10** | 3.000 | **3,9h** | ✓ lượt kế tiếp |
| dev300 top-20 | 6.000 | 7,8h | ✓ |
| **đề thi top-8** | 8.000 | **10,4h** | ✓ vừa dưới trần 12h |
| đề thi top-10 | 10.000 | 13,0h | ✗ vượt trần |
| dev300 cả rổ 50 | 15.000 | 19,5h | ✗ vượt trần |

**Bài học phương pháp:** ước chi phí phải gắn với **vai trò** của thành phần, không phải
với cỡ dữ liệu lớn nhất tưởng tượng ra. Nhân sai một lần suýt đóng oan hướng mạnh nhất.

**⚠️ NHƯNG CÓ TRẦN CỨNG, TÍNH TRÊN CPU TRƯỚC KHI CHẠY: +2,17 ĐIỂM.**
8B chọn **hoàn hảo** 5 trong top-10 thì dev300 = **0.9567**, hơn mốc 0.9350 đúng +2,17.
Trần theo cỡ danh sách: top-10 và top-15 đều +2,17 (nên top-15 vô nghĩa, đắt hơn 50% mà
trần y hệt) · top-20 +2,50 · top-30 +3,67 (11,7h, sát trần) · top-50 +4,67 (19,5h).
→ **Chấm lại danh sách ngắn, kể cả hoàn hảo, chỉ đóng được hơn nửa khoảng cách 3,9 điểm.**
Không phải viên đạn bạc. Biết trước còn hơn biết sau 4 giờ GPU.

**Tỉ lệ phá vẫn chưa đo** — hard15 chỉ đo phần ĂN THÊM. Gemini cũng 10/15 mà thay toàn bộ
thì **lỗ 2 câu**. Đây là thứ `rescore8b_run.ipynb` sinh ra để đo.

**Ngưỡng đã hiệu chỉnh theo trần** (luật +2,0 đặt cho hiệu ứng trần mở; ở đây đòi +2,0 là
đòi 92% oracle, bất khả): **Δ ≥ +1,50 VÀ ròng ≥ +4 câu** → chạy đề thi · +0,70…+1,50 vùng
mù · ≤+0,70 đóng · **tỉ lệ phá > 3% → ĐÓNG bất kể điểm ròng** (Gemini chết ở 4,3%).
+1,50 = 4,5 câu = 3 lần sàn nhiễu dev300, và đây là đổi CƠ CHẾ — hai lần đổi cơ chế trước
(deepchunk, rổ fusion) đều VƯỢT dự báo public (134%, 192%), vặn heuristic thì hụt (31%).

(hết phần lịch sử)
</details>

### 🧠 KẾT LUẬN LỚN NHẤT CỦA PHIÊN — **BỐN "GIẢI PHÁP" HOÁ RA LÀ MỘT. ĐỪNG CỘNG DỒN CHÚNG.**

Đo chồng lấn trên CPU 23/08, 0 giờ GPU, và nó **hạ cấp việc 2 xuống dưới ngưỡng đáng chạy**:

| | |
|---|---|
| pipeline hai tầng (`max` n=1) | 0.9350 · **đúng 282/300** |
| enrich `front`, một đoạn (n=3) | 0.9000 · đúng 273/300 |
| enrich `plain`, một đoạn (n=3) | 0.8900 · đúng 270/300 |

**6 câu mà tiêu đề cứu được → 5 câu pipeline hai tầng ĐÃ đúng sẵn.** Chỉ **1 câu**
(`63832`) là thứ tiêu đề bù được mà đọc sâu không bù được.

→ **Làm giàu đoạn và đọc sâu chữa CÙNG MỘT lỗi**, không phải hai lỗi khác nhau. Con số
+1,00 đo được là tiêu đề **thay thế** cho tầng đọc sâu đang thiếu ở cấu hình một đoạn,
**không phải cộng thêm** vào nó. Chồng lấn tổng thể: pipeline đúng/front sai **13 câu** ·
front đúng/pipeline sai **4 câu** · cùng đúng 269 · cùng sai 14.
**Hợp HOÀN HẢO hai bên = 0.9483, tức +1,33** — mà đó là oracle (phải biết trước câu nào
tin bên nào). Kỳ vọng thật của việc nhét `head` vào cấu hình hai tầng: **~+0,33 (1 câu)**.

**⛔ VẬY THÌ ĐỪNG CHẠY LƯỢT HAI TẦNG 3h CHO VIỆC 2.** Quy tắc 4: kỳ vọng dưới 2,0 điểm
thì dev300 không đo nổi. Tôi đã khuyến nghị chạy nó một tiếng trước — **rút lại**, phép
đo chồng lấn này chưa có lúc đó.

**Cùng một chữ ký lặp lại ở khắp nơi, đó mới là điều đáng nhớ:**

| quan sát | ý nghĩa |
|---|---|
| tiêu đề cứu 6 câu, **5 câu đọc sâu đã cứu rồi** | hai cần gạt trùng nhau |
| 8B bắt 10/15, **bao trùm hẳn** 6/15 của `ce_ours` | không phải "khác loại", chỉ là **xa hơn trên cùng một trục** |
| 8B và Gemini bắt **đúng cùng 10 câu**, giao = hợp = 10 | hai model độc lập hội tụ vào cùng một tập |
| 4 câu `1524` `16942` `37542` `8946` **cả 5 bộ chấm đều trượt** | lõi cứng, không cần gạt nào chạm tới |

Bốn "giải pháp" khác nhau đều tấn công **một nút thắt duy nhất**: cho bộ chấm đủ ngữ cảnh
để nhận ra ĐÂY LÀ VĂN BẢN NÀO. Chúng **không cộng dồn**. Mọi biến thể tiếp theo của
"cho bộ chấm nhiều/tốt hơn" sẽ rơi vào đúng 10 câu đó và trượt đúng 4-5 câu đó.
**Ngừng tìm cần gạt thứ năm cùng loại.**

### 🔬 MỔ LẠI 18 CÂU SAI, 23/08 — **CHẨN ĐOÁN CŨ SAI: 5 VĂN BẢN GOLD CHƯA HỀ ĐƯỢC ĐỌC SÂU**

Chạy CPU, 0 giờ GPU, trên rổ fusion + cấu hình chốt (`max`, n=1, 0.9350).

| | câu | điểm | thuộc về |
|---|---|---|---|
| gold **ngoài rổ 50** | 5 | 1,67 | **D** — E không chạm được |
| gold trong rổ, xếp hạng hỏng | **13** | **4,33** | **E** |

**🔑 PHÁT HIỆN LẬT CHẨN ĐOÁN.** `deepen_all` chỉ đọc sâu **M=20 văn bản đầu theo `ce` tầng
1**. Năm văn bản gold rớt ngoài mốc đó, nên `ce_deep` **chưa từng được tính** cho chúng:

| qid | gold | hạng tầng 1 | `ce` | `ce_deep` |
|---|---|---|---|---|
| 49070 | 129275 | **42** | 0,00017 | chưa đọc |
| 16942 | 102434 | **40** | 0,00023 | chưa đọc |
| 65498 | 285041 | **40** | 0,01057 | chưa đọc |
| 64622 | 149370 | **28** | 0,00398 | chưa đọc |
| 63832 | 213302 | **21** | 0,00112 | chưa đọc |

**Điểm ~0 của chúng là chấm trên 3 đoạn của D, KHÔNG phải phán quyết của khâu đọc sâu.**
Mọi chỗ trong file này gọi nhóm đó là "máy mù" đều **phát biểu sai** — chưa ai cho model
cơ hội đọc. Sửa cách nói ở mọi chỗ.

**Và đọc sâu nâng gold rất mạnh khi được áp dụng:** `65498/23402` **0,163 → 0,862** ·
`8946` 0,00045 → 0,013 (**29×**) · `92466` 0,029 → 0,123 (4×) · `144234` 0,065 → 0,148.
→ Câu hỏi "**cổng M=20 có phải nút thắt không**" là câu hỏi thật, chưa ai trả lời.

**Phân nhóm 13 câu của E:**

| nhóm | câu | đặc điểm |
|---|---|---|
| A· gold bị chấm <0,01 | 7 | `49070` `64622` `63832` `16942` `159444` `37542` `119400` |
| B· gold hạng 6-10, điểm khá | 6 | `144234` `1524` `92466` `138214` `65498` `8946` |
| C· điểm khá mà hạng >10 | **0** | — |

**Hai câu thua sát rạt:** `92466` (0,123 vs ngưỡng 0,142) và `8946` (0,013 vs 0,017) —
cách top-5 chưa tới **0,02 điểm**.
**9/13 câu có đối thủ chấm >0,87** — máy tự tin mà sai, y như mọi lần đo trước.
**`102434` là gold của CẢ `92466` lẫn `16942`, 378 đoạn gộp** — K=20 phủ 5%.

**⚠️ Bẫy đã dính khi mổ:** lần đếm đầu tôi quên `DC.MERGE_CHARS = 1800` nên ra **2.951**
đoạn thô thay vì **1.353** đoạn gộp — sai gấp đôi, và suýt dùng để ước chi phí.
`deep_chunk` mặc định `MERGE_CHARS = 0`; **notebook nào cũng phải tự đặt lại**.

### 🏁 KẾT QUẢ ORACLE13 (23/08) — **E ĐÃ CHẠM TRẦN CỦA MODEL NÀY. DƯ ĐỊA CÒN +0,80.**

Chấm trọn 1.353 đoạn của 13 văn bản gold. Kết quả: **cứu được 4/13**, oracle **+1,33 điểm**,
quy về thực tế (× 0,6) = **+0,80** → **dưới ngưỡng +2,0. Đừng đổi pipeline vì nó.**

| qid | gold | điểm nay | ORACLE | ngưỡng | đọc sâu? | |
|---|---|---|---|---|---|---|
| 64622 | 149370 | 0,004 | **0,999** | 0,599 | CHƯA | ✅ |
| 16942 | 102434 | 0,0002 | **0,9998** | 0,900 | CHƯA | ✅ |
| 63832 | 213302 | 0,001 | **0,865** | 0,165 | CHƯA | ✅ |
| 92466 | 102434 | 0,123 | **0,755** | 0,142 | CÓ | ✅ |
| 65498 | 23402 | 0,862 | 0,923 | 0,949 | CÓ | thua sát |
| 65498 | 285041 | 0,011 | 0,748 | 0,949 | CHƯA | thua |
| 144234 · 138214 · 8946 · 119400 | | | **oracle = điểm nay** | | CÓ | đã tìm hết |
| 1524 · 159444 · 37542 | | | **oracle THẤP HƠN điểm nay** | | CÓ | xem dưới |
| 49070 | 129275 | 0,0002 | 0,006 | 0,398 | CHƯA | vô vọng |

**BA KẾT LUẬN, cái thứ ba là cái quyết định:**

**1. Cổng M=20 có ăn thật, nhưng chỉ ~1 câu chắc chắn.** 3/4 câu cứu được là văn bản
CHƯA từng được đọc sâu. Nhưng nâng M chỉ *cho phép* đọc, không đảm bảo `pick_chunks` tìm
đúng đoạn: `64622` có 19 đoạn → K=20 phủ 100%, **chắc ăn**. `63832` 74 đoạn → 27%.
`16942` **378 đoạn → 5%**. Cộng lại thực nhận ~+0,33…+0,67. Không đáng một lượt GPU.

**2. `pick_chunks` BỎ SÓT thật, có bằng chứng trực tiếp.** `92466` ĐÃ được đọc sâu ở K=20
và chỉ ra 0,123, trong khi đoạn tốt nhất của văn bản đó là **0,755**. Bộ chọn đoạn nhìn
trượt. Nhưng văn bản đó 378 đoạn — muốn chắc thì K phải ~378, đúng cái mà quét K 19/08 đã
định giá là tuyến tính và chỉ ăn +0,80 ở K=120.

**3. 🔴 CHÍN CÂU VÔ VỌNG — kể cả ĐOẠN TỐT NHẤT của chính văn bản gold cũng thua.**
Đây là **trần của model**, không phải trần của cách băm. Ba câu `1524` `159444` `37542`
còn có oracle **THẤP HƠN** điểm hiện tại — tức đoạn của D chấm cao hơn mọi đoạn mình tự
băm; cách băm của mình còn **hại** ở đó.

→ **E HẾT ĐƯỜNG TRONG NGÂN SÁCH 3B.** Toàn bộ dư địa còn lại của khâu xếp hạng là
**+1,33 oracle / +0,80 thực tế**, mà ngưỡng đo được của dev300 là 2,0. Mọi thứ E vặn thêm
đều nằm dưới sàn nhiễu. Không phải "chưa tìm ra cách" — là **đã đo được trần và trần thấp**.

**Bức tranh đầy đủ, 6,5 điểm còn thiếu chia làm ba:**

| | điểm | ai | trạng thái |
|---|---|---|---|
| gold ngoài rổ 50 | 1,67 | **D** | mở — nâng rổ là nâng trần |
| E: chọn đoạn + cổng M | **1,33** oracle / 0,80 thực | E | **dưới ngưỡng, đóng** |
| E: model chấm sai hẳn (9 câu) | 3,00 | E | **cần model >3B → luật cấm** |

**→ Việc còn lại đáng làm nhất không nằm ở E nữa. Dồn cho D nâng rổ.**

**⚠️ Thiếu sót của lượt này, ghi để lần sau khỏi lặp:** notebook chỉ lưu điểm **cao nhất
mỗi văn bản**, không lưu điểm từng đoạn — nên không kiểm được `pick_chunks(k=20)` có chọn
trúng đoạn thắng hay không. Lần sau lưu cả **hạng của đoạn thắng**, thêm 3 dòng code, trả
lời được câu "nâng K có cứu được không" mà khỏi chạy lại.

### ▶️ `oracle13_run.ipynb` — **1,7 phút GPU, chốt luôn hướng đi của E**

Chấm **trọn 1.353 đoạn** của 13 văn bản gold bằng chính model đang có (không chọn lọc gì).

- **Có đoạn vượt ngưỡng top-5** → nút thắt là **CHỌN ĐOẠN / CỔNG M** → sửa được, **0 tham
  số phát sinh**, không đụng ngân sách 3B, không cần danh sách trắng.
- **Không có** → nút thắt là **MODEL** → trong 3B thì E hết đường, dồn toàn bộ cho D.

Ngưỡng: quy về thực tế (× 0,6 như quy ước 17/08) **≥ +2,0 làm tiếp · <+0,7 đóng.**
Notebook tự dựng lại mốc 0.9350 và assert đúng 13 câu trước khi chạm GPU.
**Đã kiểm logic đo:** thay điểm oracle bằng điểm cũ → ra **đúng 0.9350**; thay bằng 1.0 →
**0.9783 = +4,33**, khớp con số "13 câu = 4,33 điểm" đã ghi từ trước.

### ✅ VIỆC KẾ TIẾP SAU KHI BIẾT TRẦN 3B VÀ BIẾT CHỒNG LẤN

1. **Hỏi BTC về distillation** (5 phút, 0 GPU). Đây là cửa duy nhất còn lại để lấy phần
   8B ăn được mà vẫn ở trong 3B. `scores_hard15_qwen3rr8b.json` đã có sẵn trên máy.
2. **Rổ mới của D** — trục DUY NHẤT không nằm trên nút thắt đã bão hoà. Nó nâng TRẦN
   (0.9817), còn mọi thứ E làm chỉ đang tranh nhau phần dưới trần. Nhắc D: D 1B + E
   0,568B mới hết 1,57B/4B — **E còn dư ~2,4B và đang không biết tiêu vào đâu cho đáng**,
   nếu D cần thêm chỗ thì lấy.
3. **14 câu cả hai cấu hình cùng sai trên dev300** — chẩn đoán chúng trước khi thiết kế
   bất cứ thí nghiệm nào nữa. Đừng thiết kế mù thêm lần nào.

**⛔ ĐỪNG chạy `rescore8b_run.ipynb`** (vượt ngân sách) **và đừng chạy lượt hai tầng cho
việc 2** (kỳ vọng +0,33). Giữ cả hai file để tham chiếu cách đo.

#### B. Việc 2 — `enrich_run` xong. **`front` +1,00 → VÙNG MÙ. KHÔNG mang lên đề thi.**

| nhánh | n=0 | n=1 | n=2 | n=3 | tốt nhất | Δ so `plain` |
|---|---|---|---|---|---|---|
| `plain` | 0.7467 | 0.8267 | 0.8700 | 0.8900 | 0.8900 | — |
| **`front`** | 0.7733 | 0.8467 | 0.8800 | **0.9000** | **0.9000** | **+1,00** |
| `back` | 0.7650 | 0.8383 | 0.8733 | 0.8933 | 0.8933 | +0,33 |

Đối chiếu từng câu: `front` **cứu 6 · phá 3 · ròng +3 câu**.

**Theo ngưỡng đặt trước thì đây là VÙNG MÙ (+0,7…+2,0), và tiền lệ nói phải nghe theo:**
lượt "BM25 chọn đoạn + gộp 1800" cũng **+1,00 trên dev300** → public chỉ **+0,31**, đúng
31% dự báo. CLAUDE.md đã chẩn: *"+1,00 = 3 câu, dưới sàn nhiễu ±1,5 câu của chính nó —
dev300 tung đồng xu và ra mặt ngửa."* **Cùng con số, cùng vùng. Đừng lặp lại.**

**Nhưng có hai thứ nâng độ tin, ghi lại cho công bằng:**
- `front` hơn `plain` ở **CẢ BỐN `n`** (4/4), không phải thắng nhờ chọn `n` khéo.
- Khớp cơ chế đã thấy ở hard15 (6/15 vs 3/15) — hai phép đo độc lập, cùng chiều.

**✅ ĐÓNG CÂU HỎI TREO TỪ 13/08: vị trí ĐẦU thắng vị trí CUỐI** (+1,00 vs +0,33).
Giả thuyết "chiếm mất vị trí đầu là có hại" (cơ chế 2) **SAI**. Vụ thua −2,0 điểm ngày
12/08 là do **mất dấu** (cơ chế 1), không phải do vị trí. Tiêu đề CÓ DẤU ghép vào ĐẦU thì
dương ở mọi cấu hình. Gạch cơ chế 2 khỏi mọi lập luận sau này.

⚠️ Bảng trên là cấu hình **một đoạn/văn bản, không có tầng đọc sâu** — `plain` = 0.8900
chứ không phải 0.9350. **Không so chéo với bảng hai tầng.**

#### C. Việc kế tiếp — thứ tự

1. **Lấy số phút của 8B từ log**, rồi vặn tốc độ (~10 phút GPU). Đây là cửa chặn của
   hướng mạnh nhất đang có. Không có tốc độ thì không đo nổi tỉ lệ phá, mà không có tỉ lệ
   phá thì 8B vĩnh viễn không dùng được.
2. **Tỉ lệ phá của 8B trên dev300** — chỉ khi bước 1 xong.
3. **Làm giàu đoạn ở cấu hình HAI TẦNG** (~3h): nhét `head` vào `pick_chunks`, chạy
   `fusion_run` MODE=dev, so thẳng với **0.9350**. Đây là cách duy nhất biết +1,00 kia
   nở ra hay teo đi ở cấu hình thật. Ngưỡng: ≥0.9550 mới mang lên đề thi.

### 🔑 KẾT QUẢ VIỆC 1 (23/08, chạy dở) — **ĐỐI CHỨNG NỔ. THỦ PHẠM LÀ ĐẦU VÀO, KHÔNG PHẢI MODEL.**

| | bắt/15 | hạng 1 | ghi chú |
|---|---|---|---|
| SÀN đếm từ trùng | 3 | — | |
| pipeline chốt (blend n=2) | **0** | — | theo định nghĩa: 15 câu này chọn VÌ nó sai |
| **`ce_ours`** — chính AITeamVN, đầu vào `head`+`excerpt` | **6** | 5 | ⚠️ **≥5 → nhánh "ĐẦU VÀO" đã kích hoạt** |
| `qwen3rr4b` — Qwen3-Reranker-4B, cùng đầu vào | **7** | 4 | **32,7 phút** |
| Gemini 2.5 Flash (listwise, cả 50 cùng lúc) | 10 | 5 | mốc cũ |
| TRẦN | 15 | | |

**Phân rã sạch, đo trên CPU 0 giờ GPU** — cùng model AITeamVN, cùng rổ, chỉ đổi từng thứ một:

| cấu hình | bắt/15 | câu bắt được |
|---|---|---|
| blend n=2 + `max(ce,ce_deep)` ← pipeline chốt | 0 | — |
| **bỏ blend**: n=0 + `max(ce,ce_deep)`, vẫn đoạn sâu | **3** | `156454` `33938` `52126` |
| **đổi đầu vào**: n=0 + `head`+`excerpt` | **6** | ba câu trên **+** `112344` `128326` `159444` |

**Đọc cho đúng — hai nửa không cùng giá trị:**

- Nửa "bỏ blend" (+3) phần lớn là **hiệu ứng chọn mẫu**: 15 câu này được chọn bằng chính
  cấu hình có blend, nên đổi luật chốt kiểu gì cũng vớt lại được vài câu. **Đừng dùng số
  này để kết tội `n=2`** — public LB đã nói n=2 thắng, và bảng M×n 23/08 xác nhận.
- Nửa "đổi đầu vào" (+3) **là thật**. Hai cột đều dùng n=0 nên đứng cùng vạch xuất phát so
  với phép chọn mẫu. Và nó **bao trùm hẳn**: 6 câu ⊃ 3 câu, không đánh đổi câu nào.

**→ `head` (260 ký tự đầu: TÊN + SỐ HIỆU văn bản) là thứ bộ chấm đang thiếu.** Đây chính
là **việc 2 — làm giàu đoạn**, và giờ nó không còn là phỏng đoán: đã đo được +3/15 trước
khi tiêu một giờ GPU nào cho nó. **Việc 2 lên số 1.**

**⛔ TRỤC "ĐỔI MODEL" GẦN NHƯ CHẾT — không phải vì điểm, mà vì CHI PHÍ.**
Qwen3-Reranker-4B hơn chính model của mình đúng **+1/15** (7 vs 6) — dưới ngưỡng phân giải
của n=15. Mà nó chạy **2,6 giây/cặp**, trong khi AITeamVN chạy **12,9 đoạn/giây** →
**chậm hơn ~33 lần**. Quy ra: dev300 47.240 đoạn = **34 giờ**, đề thi 157.008 đoạn =
**113 giờ**. Vặn fp16 + batch lớn may ra nhanh 5–10 lần thì đề thi vẫn ~11h, sát trần 12h.
**Trả 33 lần chi phí cho +1 câu nhiễu.** Chỉ còn cửa duy nhất: dùng làm lượt chấm lại
HẸP (top-20 văn bản × 1 đoạn/câu), và cửa đó phải tự chứng minh chứ đừng mặc định.

**⚠️ NGƯỠNG ≥8/15 ĐẶT TRƯỚC LÀ SO VỚI MỐC 0 — MỐC ĐÚNG LÀ 6.** Không phải ngưỡng sai vì
đặt ẩu, mà vì chính phép đối chứng này chưa từng chạy. Phát biểu lại cho lần sau:
*model mới phải hơn `ce_ours` TRÊN CÙNG ĐẦU VÀO*, không phải hơn 0. Theo thước đó thì
4B được **+1**, tức chưa được gì.

**❌ Ước chi phí của tôi sai nặng: nói "15–25 phút cho 4 model", thực tế ~2,5–3 giờ.**
Nguyên nhân: T4 (Turing) **không có bf16 phần cứng**, torch vẫn nhận `is_bf16_supported()`
= True rồi chạy đường giả lập rất chậm. Lần sau ước bằng **giây/cặp đo thật của đúng model
đó**, đừng ngoại suy từ AITeamVN — hai kiến trúc chênh nhau 33 lần.

### VIỆC 2 — `enrich_run.ipynb`, dựng xong 23/08. **Đây là việc chạy tiếp theo.**

**Không nhảy thẳng vào lượt hai tầng 3h.** Lý do: 12/08 đã ghép tên văn bản một lần và
**thua −2,0 điểm** (mục "Ghép tên văn bản — ĐÃ THỬ VÀ THUA" cuối file). Lần đó dùng slug
URL **không dấu** của D, ghép vào ĐẦU đoạn. Ba cơ chế đã chẩn: mất dấu · chiếm vị trí đầu ·
lệch phân phối. **Chưa từng thử vị trí CUỐI** nên chưa tách được cơ chế 1 khỏi cơ chế 2.

Lượt này tách hẳn: tiêu đề lấy từ **chính `passage`** (có dấu, đúng phân phối), quét **cả
hai vị trí**, và chạy **trọn dev300** — vì 15 câu khó chỉ đo được phần ĂN THÊM, trong khi
lần thua 12/08 thua chính vì **phá các câu đang đúng**.

| nhánh | văn bản đưa model | |
|---|---|---|
| `plain` | `excerpt` | **ĐỐI CHỨNG** |
| `front` | `head` + `excerpt` | đúng cấu hình đã đo 6/15 |
| `back` | `excerpt` + `head` | trả lời câu treo từ 13/08 |

Ba nhánh dùng CHUNG một `excerpt` do `pick_chunks` chọn → khác biệt duy nhất là tiêu đề.

**Ngưỡng đặt TRƯỚC, so với `plain` (KHÔNG so với 0.9350 — đó là cấu hình hai tầng khác):**
≥ +2,0 thắng rõ, nhét vào `pick_chunks` rồi chạy lượt 2 tầng · +0,7…+2,0 vùng mù, không
mang lên đề thi · −0,7…+0,7 hoà, đóng · ≤ −0,7 thua dù đã có dấu → **đóng vĩnh viễn**.

**Chi phí ~58 phút GPU** (45.000 cặp @ 12,9 cặp/s), rẻ hơn lượt hai tầng ba lần mà tách
biến sạch hơn. **Không cần upload gì mới** — mọi file đã có từ `fusion_run`.

**Đã kiểm hàm đo trước khi giao:** `rec()` + `blend_bm25_first` + cách nạp rổ trong
notebook này dựng lại bảng `max` ngày 20/08 **khớp cả bốn `n`** (0.9283 / 0.9350 / 0.9283
/ 0.9233). Nên nếu số ra lạ thì lỗi ở phần chấm, không phải ở phần đo.

### VIỆC 1 — `hard15_run.ipynb`, dựng xong 23/08. Đọc trước khi bấm chạy.

**Upload lên dataset `project-ir`:** `rerank_qwen.py` (**BẢN MỚI, đè**) · `rerank.py` ·
`Ketqua_E/gemini/batch_0{1,2,3}.json` · `dev_300_locked.json` (đã có). **Internet ON.**
Chi phí ~15–25 phút GPU cho 4 model. T4 hay P100 đều được.

**🔴 BẬT ACCELERATOR TRƯỚC KHI CHẠY — đã dính 23/08.** Lượt đầu chạy nhầm session CPU:
upload đúng hết (hash khớp, Bước 1 in đủ trần 15/15 và sàn 3/15), nhưng cả 4 model chết
lần lượt vì `Torch not compiled with CUDA enabled` — **Kaggle cài bản torch KHÔNG có CUDA
cho session CPU**, nên lỗi chỉ nổ ra ở `.to("cuda")`, tức là SAU khi đã tải vài GB trọng
số. Cùng họ bẫy "thứ trông giống phép kiểm mà kiểm sai chỗ": Bước 1 chạy trót lọt tạo cảm
giác mọi thứ ổn. Đã thêm `assert torch.cuda.is_available()` ngay dòng đầu Bước 1 → giờ
chết trong 1 giây kèm hướng dẫn bật, thay vì 3 phút tải rồi mới chết.

**⚠️ SỬA MỘT LỖI CHÍNH TẢ CỦA KẾ HOẠCH CŨ:** mục việc-tiếp-theo ghi 15 câu nằm ở
`batch_01.json`. **Sai.** `Q_PER_BATCH` đã hạ xuống 5 (bẫy "chat im lặng cắt bớt"), nên
15 câu nằm ở **`batch_01` + `batch_02` + `batch_03`**, mỗi lô 5 câu. Đã kiểm: đúng 750 cặp,
gold còn trong rổ ở **15/15** câu.

**Đã kiểm cả 10 lô, 23/08 — kết quả chính xác, ghi lại để khỏi kiểm lần nữa:**

| | |
|---|---|
| `batch_01` `02` `03` | 5 câu/lô · **hợp = ĐÚNG 15 câu khó**, không thiếu, không thừa |
| `batch_04` `06` `07` `09` `10` | lượt dựng 150 câu dễ, **0 câu khó** |
| `batch_05` `08` | lượt cũ, nhưng mỗi lô **có 1 câu khó** (`112344`, `119400`) |

Hai lô `05`/`08` **không phải rác hoàn toàn** như ghi lúc đầu — hai câu trùng đó đã đối
chiếu và **giống hệt từng ký tự** với bản ở `batch_01` (cùng câu hỏi, cùng 50 `doc_id`,
cùng thứ tự, cùng `head`/`excerpt`). Nên dù có upload nhầm cả 10 lô thì việc notebook ghi
đè theo `qid` cũng **không đổi một cặp nào**. Đây là fact đã đo, không phải suy đoán.

→ Vẫn chỉ upload `01` `02` `03`, nhưng lỡ upload thừa thì đừng lo, và đừng đi sửa gì.

**Đối chiếu ngược 750 cặp về corpus, 23/08 — sạch:** 644 `doc_id` duy nhất, **750/750 có
`context_<id>.json`**, **750/750 `head` khớp ĐÚNG `passage[:260]`** từng ký tự, `link` đủ
ở mọi văn bản. Không có id bịa, không có id chết. `excerpt`: 746 nằm nguyên văn trong văn
bản gốc, **4 câu chỉ lệch khoảng trắng** (`pick_chunks` gộp mảnh nên nuốt vài `\\r\\n`) —
chuẩn hoá khoảng trắng thì khớp 4/4, nội dung không mất gì. Đáng chú ý: cả 4 ca đó đều là
**biểu mẫu / tờ khai / danh mục** (`56363` tố cáo · `5374` và `17095` phiếu dự thi ·
`267226` tờ khai) — đúng nhóm "máy mù" đã chẩn đoán. Trùng hợp, nhưng hợp lý: văn bản
dạng bảng mới có kiểu xuống dòng vụn như thế.

**Bốn model, mỗi model một vòng riêng, hỏng cái này không giết cái kia:**

| tag | model | vì sao |
|---|---|---|
| `ce_ours` | AITeamVN/Vietnamese_Reranker | **ĐỐI CHỨNG, quan trọng nhất** — xem dưới |
| `qwen3rr4b` | Qwen/Qwen3-Reranker-4B | 0.6B từng đo 0.7711 (dev150, fp16 tràn số). Đây là phép hỏi "thua vì NHỎ hay vì CƠ CHẾ" |
| `qwen3rr8b` | Qwen/Qwen3-Reranker-8B | to nhất họ này còn chạy nổi trên T4 |
| `qwen25i7b` | Qwen/Qwen2.5-7B-Instruct | model sinh văn bản thường — gần Gemini nhất về loại |

**Ba mốc để đọc kết quả, cả ba đã đo sẵn, 0 giờ GPU:**

| mốc | số | ý nghĩa |
|---|---|---|
| TRẦN | 15/15 | gold còn trong rổ ở mọi câu — không ai đổ tại rổ được |
| Gemini 2.5 Flash | **10/15** (hạng 1 chỉ **5/15**) | mốc phải đuổi |
| **SÀN — đếm từ trùng thuần** | **3/15** | **ngưỡng ĐÓNG ≤3 nằm đúng ở đây**, không tuỳ tiện |

Sàn 3/15 là số mới đo 23/08. Nó biến ngưỡng "≤3 thì đóng" từ con số cảm tính thành một
phát biểu có nghĩa: *model không hơn được phép đếm từ thì không mang gì mới vào.*

**🔑 ĐỐI CHỨNG `ce_ours` — biến gây nhiễu chưa ai loại trừ, và nó có thể lật cả hướng.**
Pipeline thật chấm **đoạn sâu** do `pick_chunks` cắt. Gemini được cho **`head` 260 ký tự +
`excerpt` 900 ký tự** — đầu vào KHÁC HẲN. Nên "Gemini 10/15, mình 0/15" đang trộn hai
nguyên nhân. Notebook chấm chính model của mình trên đúng đầu vào của Gemini để tách:

- `ce_ours` ra **0–2/15** → khác biệt nằm ở **MODEL**. Giả thuyết đứng, đi tiếp.
- `ce_ours` ra **≥5/15** → khác biệt nằm ở **ĐẦU VÀO**, không phải model. Khi đó việc phải
  làm là sửa cách dựng đoạn — **rẻ hơn nhiều, và trùng luôn với việc 2 (làm giàu đoạn)**.
  Mọi câu chữ "cần model khác loại" phải viết lại. Đây là kịch bản có lợi, đừng ngại nó.

**⚠️ Giới hạn phải ghi kèm nếu ra kết quả xấu:** notebook chấm **theo từng cặp**
(pointwise, P("yes") ở token cuối); Gemini xếp hạng **cả 50 cùng lúc** và có suy luận.
Ra ≤3/15 thì mới chỉ bác được **pointwise**, CHƯA bác được "model khác loại". Muốn tách
thì chạy lại đúng 15 câu này ở chế độ sinh văn bản xếp cả rổ. **Đừng ghi gọn vào file này
thành "model khác loại thua"** — đó đúng loại rút gọn đã giết oan một hướng ở lượt 19/08.

**Vì sao chạy được model >3B trên T4** (ngân sách 3B cũ là do fp32): `load_4bit=True` →
NF4, 8B chỉ ~6GB, nhưng **giải nén ra fp32 để tính** nên tránh đúng bẫy tràn số fp16 đã
làm Qwen3-0.6B ra 0.7711. Sanity check cũ vẫn chạy trước mỗi model và vẫn có quyền chặn.

### ⚠️ `Ketqua_E/scores_public_fusion_M20_K20.json` CHƯA TẢI VỀ MÁY

CLAUDE.md liệt kê nó là tài sản nhưng thư mục chỉ có bản M10. File còn trong output lượt
`public_b` trên Kaggle — **tải về trước khi phiên đó bị dọn**. Không có nó thì mọi thí
nghiệm chốt top-5 trên rổ M=20 của ĐỀ THI phải chạy lại 4h GPU (quy tắc 2).

### ⚠️ QUOTA: 60h/TUẦN, KHÔNG PHẢI 30h — quota KHÔNG còn là nút thắt

Ngân sách 4 tuần tới 15/09 ≈ **240h**. Toàn bộ kế hoạch trên ăn ~78h (đã nhân 1,5 dự phòng).
**Bỏ mọi lập luận ưu tiên dựa trên "thiếu quota" ở các mục dưới.** Ba thứ 240h KHÔNG mua được:

| Ràng buộc thật | Vì sao quota không gỡ được |
|---|---|
| **Trần 12h mỗi lượt** | per-run, tài khoản phụ không nới, Kaggle cấp T4/P100 ngẫu nhiên chênh 2x |
| **Số lượt nộp/ngày** | dụng cụ đo duy nhất cho hiệu ứng dưới 2 điểm |
| **dev300 mù dưới 2 điểm** | chạy 20 thí nghiệm nhỏ = 20 kết quả không đọc được |

→ Nguyên tắc còn lại là nguyên tắc DUY NHẤT: **mỗi lượt GPU phải trả lời một câu hỏi đã
viết ra trước, với ngưỡng đã đặt trước.** Không phải để tiết kiệm — để kết quả có nghĩa.

### Tài sản mới 22–23/08

| file | nội dung |
|---|---|
| `Ketqua_E/scores_public_fusion_M10_K20.json` | đề thi, `ce_deep` hạng 1-10 |
| `Ketqua_E/scores_public_fusion_M20_K20.json` | đề thi, `ce_deep` hạng 1-20 — **đầy đủ** |
| `Ketqua_E/tang1_scores_public_fusion_M10_K20.json` | tầng 1 riêng, dự phòng |
| `Ketqua_E/submission_fusion_M20_n{1,2,3,4}.zip` | **n=2 là bài chốt 0.9109** |
| `Ketqua_E/submission_fusion_M10_n{0,1,2,3,4}.zip` | dải M=10, n=3 tốt nhất 0.9063 |
| `hard15_run.ipynb` | **MỚI** — việc 1, 4 model × 750 cặp trên 15 câu khó |
| `rerank_qwen.py` | **ĐÃ ĐÈ** — thêm `load_4bit` (chạy 8B trên T4) và khuôn `instruct` |

Năm phép kiểm offline lượt B, pass hết: đúng **20/20** văn bản có `ce_deep` mỗi câu ·
`ce` tầng 1 **0/50.000** lệch · **`ce_deep` hạng 1-10 của lượt A giữ nguyên 0/10.000**
(cơ chế `skip=10` khâu đúng giữa hai phiên GPU cách nhau nhiều giờ) · bài nộp hợp lệ,
không lọt dev · dựng lại từ scores khớp 1000/1000.

---

## TRẠNG THÁI 20/08 — lịch sử. **RỔ FUSION THẮNG TRÊN dev300.** Đã thực hiện, xem mục 23/08.

D giao `fusion_rrf_top50_{dev_1000,public}.json` (BM25 + bge-m3 gốc, hoà RRF, top-50).
**D KHÔNG fine-tune gì** → không rò rỉ dev, số đo sạch.

### Đã chạy xong `fusion_run.ipynb` MODE=dev (~3h). Kết quả dev300:

| biến thể | n=0 | n=1 | n=2 | n=3 |
|---|---|---|---|---|
| base | 0.8533 | 0.8800 | 0.8983 | 0.9000 |
| **max** | 0.9283 | **0.9350** ← đỉnh | **0.9283** | 0.9233 |
| replace | 0.9200 | 0.9233 | 0.9233 | 0.9250 |

`max n=2` = **0.9283**, khớp **đúng đến từng chữ số** với mô phỏng chặn dưới chạy trên CPU
trước đó → pipeline đọc rổ mới đúng thiết kế. Δ **+1,00** so mốc rổ BM25 cũ (0.9183).

Chốt kiểm cấu trúc sạch: 300 câu · 50 ứng viên/câu · **đúng 20 văn bản có `ce_deep`**/câu.

**Vì sao rổ fusion thắng** (dev300):

| | BM25 top-100 | fusion top-50 |
|---|---|---|
| recall@1 | 0.4450 | **0.5783** |
| recall@5 | 0.7533 | **0.8733** |
| trần | 0.9783 *(100 vb)* | **0.9817 *(50 vb)*** |

Trần dâng lên **và** tầng 1 rẻ đi một nửa.

### Đối chiếu từng câu với bài chốt 0.8871

| | sửa được | làm hỏng | ròng |
|---|---|---|---|
| **n=1** | **7** | 3 | **+4 câu** |
| n=2 | 4 | 2 | +2 |

7 câu n=1 cứu: `74872` `156454` `52126` `128326` `1454` `33938` `11536`.
- `11536`, `74872`: gold NGOÀI top-100 BM25 — từng bị xếp "không ai cứu được". Rổ mới kéo vào.
- `1454`, `33938`: đúng hai câu chẩn đoán 19/08 là "cái giá của `n_bm25=2`". Hạ xuống n=1 trả lại.

Còn sai 18 câu, **13 câu gold vẫn trong rổ 50** → còn dư địa cho khâu xếp hạng.

### ⚠️ ĐỈNH DỜI SANG n=1 — SINH CẢ HAI BÀI, ĐỪNG CHỌN THEO dev300

n=1 hơn n=2 đúng **2 câu** = dưới ngưỡng phân giải. dev300 đã lừa về `n` **hai lần**
(11/08 chốt n=1 rồi bị lật; 18/08 báo n=0 nhưng public LB nói n=2). Notebook sinh cả
`n=1` lẫn `n=2`, 0 giờ GPU thêm. **Để public LB quyết.** Mốc phải vượt: **0.8871**.

### ⏸ ĐANG CHỜ QUOTA (còn 2h, cần 9,7h) — kế hoạch khi có quota

`fusion_run.ipynb` có 4 MODE, đổi đúng một dòng:

| MODE | việc | chi phí | ghi chú |
|---|---|---|---|
| `dev` | ✅ ĐÃ CHẠY | ~3h | ra `scores_dev300_fusion_M20_K20.json` |
| `public_t1` | CHỈ tầng 1, có **checkpoint mỗi 100 câu** | ~2,1h | chạy lại là nối tiếp, không mất |
| `public_a` | tầng 1 + đọc sâu hạng 1-10 | ~5,7h | tự sinh bài nộp M=10 |
| `public_b` | đọc sâu hạng 11-20 | ~4h | **nạp lại tầng 1 của lượt A** (tiết kiệm 2h) |

Đường nhanh nhất khi có đủ quota: **`public_a` → upload output → `public_b`**.
Nếu quota lẻ tẻ: `public_t1` trước, banked, rồi `public_a` chỉ còn ~3,6h.

### ⚠️ HỎI D TRƯỚC KHI CHẠY ĐỀ THI

D đang dùng **`BAAI/bge-m3` gốc**. Đề xuất đổi sang **`AITeamVN/Vietnamese_Embedding`**
(bản v1, KHÔNG phải v2 — v1 thắng v2 ở mọi chỉ số Zalo Legal: Acc@5 0.9305 vs 0.9268).
Căn cứ: bảng ablation của chính nhóm — cùng nền bge-m3, bản fine-tune tiếng Việt hơn
bản gốc **3 điểm** ở phía reranker.

**Nếu D giao rổ mới thì tầng 1 vừa chạy thành RÁC.** → Hỏi D "tuần này có giao bản mới
không?" TRƯỚC khi đốt quota. Hai phút, tránh mất 2-6 giờ.

Cảnh báo tốc độ cho D (đo thật 19/08): 2048 token fp32 chỉ chạy **4,3 mảnh/giây** →
cả kho mất 7,4h. Đặt `max_seq_length=1024` + `model.half()` thì còn ~2h.

### Tài sản mới trên máy

| file | nội dung |
|---|---|
| `Ketqua_E/scores_dev300_fusion_M20_K20.json` | điểm đầy đủ, rổ fusion — mọi thí nghiệm chốt top-5 chạy CPU |
| `Ketqua_E/tang1_scores_dev300_fusion_M20_K20.json` | tầng 1 riêng |
| `fusion_run.ipynb` | notebook 4 MODE |
| `bi_encoder.py` · `biencoder_run.ipynb` | ⛔ **BỎ** — D đã làm khâu truy hồi |

## 🚨 CHUYỂN HƯỚNG 19/08 tối — **TOP LB = 0.95, MÌNH 0.8871, HẠNG ~30.** Đọc mục này TRƯỚC MỌI THỨ.

**Chênh 6,3 điểm = 63 câu.** Con số này KHÔNG vá được bằng cần gạt dưới 1 điểm.
Mọi thứ đã xoay cả ngày (K, chọn mảnh, n_bm25) cộng lại chưa tới 2 điểm. **Chênh cỡ này
là CẤU TRÚC.** → Mọi kết luận "hết đường kỹ thuật" phía dưới đều viết khi chưa biết
mốc top là bao nhiêu. Đọc chúng như lịch sử, đừng dùng làm quyết định.

### Đối chiếu với kiến trúc của các giải pháp mạnh (tra 19/08)

Chuẩn của bài toán tra cứu văn bản pháp luật tiếng Việt là **HAI TẦNG, CẢ HAI FINE-TUNE**:

| thành phần | giải pháp mạnh | nhóm mình |
|---|---|---|
| truy hồi | **bi-encoder fine-tune** + BM25 | ❌ chỉ BM25 |
| xếp hạng | cross-encoder **đã fine-tune** | ❌ cross-encoder GỐC |
| tách từ tiếng Việt | có | ❌ không |

**Nhóm thiếu đúng hai thứ lõi của công thức thắng.** Đó là 6,3 điểm, không phải K=20 vs 25.

### NGUYÊN NHÂN MỚI của thất bại fine-tune: NEGATIVE QUÁ KHÓ

Nguồn: *Optimizing Legal Document Retrieval in Vietnamese with Semi-Hard Negative Mining*
(arxiv 2507.14619) — thứ đem lại cải thiện lớn nhất là **negative BÁN khó**, +23% tương đối.
Negative **quá** khó thì phá huấn luyện.

Nhóm mình lấy negative từ **BM25 top-20** = khó nhất có thể. Trong kho pháp luật, top-20
BM25 đầy văn bản gần trùng nội dung với gold, nhiều cái cũng trả lời được câu hỏi nhưng
không được gán nhãn. **Dạy máy "những cái đó là SAI" là dạy nó điều không đúng.**

→ Fine-tune hỏng ở **CẢ HAI đầu**: nhãn dương bẩn (33%) *và* nhãn âm quá khó.

### ⛔→✅ MỞ LẠI HƯỚNG FINE-TUNE. Ba chỗ sửa, không phải chạy lại y hệt.

| chỗ hỏng | cách sửa |
|---|---|
| nhãn dương chọn bằng BM25, đúng 33% | chọn mảnh dương bằng **CHÍNH BỘ CHẤM GỐC** — oracle đã chứng minh nó tìm đúng mảnh với điểm 0.9997 |
| negative từ BM25 top-20, quá khó | lấy **hạng 10–50**, loại bỏ cái bộ chấm gốc cho điểm rất cao (nhiều khả năng là gold chưa gán nhãn) |
| huấn luyện 1 mảnh, suy luận 20 mảnh | huấn luyện theo đúng cách sẽ chấm |

Lập luận đóng hướng cũ ("thua hai lần") viết khi tưởng mình gần trần. Giờ biết chênh 63 câu,
và **thứ mình thất bại chính là thứ các nhóm mạnh làm thành công**. Tránh nó = tự nhốt ở 0.88.

### VIỆC 1 ĐANG LÀM: BI-ENCODER — `bi_encoder.py` + `biencoder_run.ipynb` (viết 19/08)

Model: **AITeamVN/Vietnamese_Embedding** — cùng nền bge-m3 với reranker đang dùng,
0,6B tham số, **2048 token/lần đọc (gấp 4 lần cross-encoder)**, đã đo trên
**Zalo Legal 2021: Accuracy@5 = 0.9305**.

Giả thuyết phụ đáng để ý: nhóm 12 câu "máy mù" toàn văn bản dạng **bảng/danh mục** —
cửa sổ 512 token của cross-encoder cắt vụn chúng. Đọc 2048 token có thể nhìn ra.

Chi phí: nhúng cả kho **~45 phút GPU, MỘT LẦN**, kho dùng chung dev + đề thi.
Sinh `emb_*.npy` + `emb_meta.json` → sau đó **mọi thí nghiệm hoà điểm chạy trên CPU**
(cùng khuôn đã làm `oracle_chunks_dev300.json` sinh lợi).

**Ngưỡng đặt TRƯỚC khi chạy:**

| đo được | quyết định |
|---|---|
| recall@100 hybrid **> 0.9783** | rổ tốt hơn → dùng, mở ra 2,17 điểm của 7 câu ngoài top-100 |
| recall@5 riêng dense **> 0.80** | mạnh (BM25 thô 0.7533) → hoà vào điểm cuối |
| recall@5 riêng dense **< 0.70** | yếu → chỉ dùng làm tín hiệu phụ |

Upload lên dataset `project-ir`: **`bi_encoder.py`** (file MỚI). GPU T4 · Internet ON.

### THỨ TỰ VIỆC — và thứ PHẢI BỎ

1. **Bi-encoder** (đang làm) — lỗ hổng cấu trúc lớn nhất, D đã bỏ rơi, E tự làm được
2. **Fine-tune lại** với ba chỗ sửa ở trên — ~5h chấm mảnh dương + ~2h huấn luyện
3. **Đổi mô hình lớn hơn / khác loại** — thử trên `Ketqua_E/gemini/batch_01.json` (15 câu khó
   đã dựng sẵn, 750 cặp ≈ vài phút). So thẳng: mình 0/15 · Gemini 10/15 · model mới ?/15
4. **Tách từ tiếng Việt** trước khi vào BM25 và vào model

**BỎ HẲN, đừng quay lại:** nâng K · vặn n_bm25 · tinh chỉnh chọn mảnh. Đã đo hết,
tổng dưới 1 điểm. Ở khoảng cách 6,3 điểm chúng là nhiễu.

Ngân sách: ~120h GPU, 4 tuần tới 15/09. Đủ cho cả bốn việc nếu không quay lại cần gạt nhỏ.

## TRẠNG THÁI 19/08 — **CHỐT 0.8871. HẾT ĐƯỜNG KỸ THUẬT.** Đọc mục này trước.

> **Bài chốt: `Ketqua_E/submission_v2_M20_n2.zip` — public LB 0.8871.**
> Fine-tune đã thua lần hai (−6,50 dev300) → đóng. Hướng chunk đã cạn. Việc còn lại:
> **⚠️ 19/08 muộn: "hết đường" chỉ đúng với KIẾN TRÚC CROSS-ENCODER. Gemini bắt được
> `119400` thuộc nhóm 'máy mù' — xem mục ✅ ĐO GEMINI LẠI trước khi trích kết luận này.**
> D nâng recall@100, và **viết báo cáo**. Chi tiết ở hai mục ⛔ và "E ĐÃ HẾT ĐƯỜNG" dưới.


| bài | public LB | Δ |
|---|---|---|
| baseline n=2 (12/08) | 0.8573 | — |
| deepchunk M=20 (17/08) | 0.8840 | +2,67 |
| **BM25 chọn đoạn + gộp 1800, n=2** (`submission_v2_M20_n2`) | **0.8871** ← tốt nhất | +0,31 |
| cùng cấu hình, n=0 (`submission_v2_M20_n0`) | 0.8851 | −0,20 vs n=2 |

### BÀI HỌC ĐẮT NHẤT: dev300 GÃY KHUÔN, và gãy theo hướng có lợi

| | dev300 | public | tỷ lệ |
|---|---|---|---|
| deepchunk M=10 | +1,34 | +1,40 | 104% |
| deepchunk M=20 | +2,00 | +2,67 | 134% |
| M=10 → M=20 | +0,66 | +1,27 | 192% |
| **BM25 + gộp 1800** | **+1,00** | **+0,31** | **31%** |

Ba lần đầu vượt dự báo, lần thứ tư hụt hai phần ba. Không phải phương pháp tệ đi:
**+1,00 trên dev300 = 3 câu, dưới sàn nhiễu ±1,5 câu của chính nó.** dev300 chưa bao giờ
*đo* được cái này — nó tung đồng xu và ra mặt ngửa. Ba lần trước hiệu ứng đủ lớn nên đo thật.

→ **Quy tắc 4 giờ là luật cứng, không phải khuyến nghị.** Hiệu ứng dưới +2,0 trên dev300
thì ĐỪNG mang lên đề thi. Trước đây nghĩ "dưới ngưỡng thì không chắc"; giờ có bằng chứng
nó **sai hẳn hướng**.

### n=2 THẮNG n=0 TRÊN LB — giữ nguyên, đừng nghe dev300

dev300 sau lượt mới báo `max n=0` = 0.9217 > `n=2` = 0.9183. Public trả lời:
**n=2 = 0.8871 > n=0 = 0.8851.** Bẫy 11/08 lặp lại y hệt, tránh được vì không đổi.

Nhưng khoảng cách n=2 vs n=0 **teo từ 22 câu xuống 2 câu** (12/08: 0.8573 vs 0.8350).
Đúng cơ chế đã dự đoán: reranker khoẻ lên thì `blend_bm25_first` hết chỗ dụng võ. Chưa
âm, nhưng gần hết giá trị. **Đừng bỏ n=2, cũng đừng kỳ vọng gì thêm từ nó.**

### CÓ VÒNG PRIVATE TEST (xác nhận 19/08) — hệ quả

1. **Ngừng đuổi chênh lệch dưới ~1 điểm trên public.** +0,31 và +0,20 vừa rồi là 3 câu
   và 2 câu; trên private chúng có thể đảo dấu.
2. **Chỉ những thứ làm MODEL tốt lên mới chuyển được sang private.** Heuristic chốt top-5
   fit theo public thì không.
3. Kiểm xem BTC cho chọn bài nào tính điểm private. Nếu được chọn → chốt
   `submission_v2_M20_n2.zip`: nó được chọn dựa trên cơ chế đo trên dev300, không phải
   fit vào public, nên chuyển sang private an toàn.

### ⛔ FINE-TUNE ĐÃ THUA LẦN THỨ HAI (19/08). ĐÓNG HƯỚNG NÀY VĨNH VIỄN.

Chạy `finetune_v2_run.ipynb` 5h. Kết quả dev300, cùng cấu hình BM25+gộp1800/M=20/K=20:

| biến thể | n=0 | n=1 | n=2 | n=3 |
|---|---|---|---|---|
| base | 0.8317 | 0.8483 | **0.8650** | 0.8617 |
| max | 0.8283 | 0.8550 | **0.8533** | 0.8650 |
| replace | 0.8067 | 0.8433 | 0.8467 | 0.8650 |

| | gốc | ft v2 | Δ |
|---|---|---|---|
| `base` n=2 (tầng 1) | 0.8883 | 0.8650 | **−2,33** |
| `max` n=2 (hai tầng) | 0.9183 | 0.8533 | **−6,50** |

**−6,50 KHÔNG phải nhiễu** — lần đầu dev300 nói được điều gì đó chắc chắn về fine-tune.

**Giả thuyết "train lệch inference" SAI dứt khoát.** Nếu đúng thì model được huấn luyện
đúng loại đoạn nó phải chấm (BM25 gộp 1800) phải khá lên **ở tầng 2**. Thực tế tầng 2
tụt **6,50**, tệ hơn tầng 1 (−2,33) — **nó tệ nhất đúng ở chỗ nó được huấn luyện.**
Không phải lệch phân phối, mà là model xấu đi thật.

Xác nhận thứ hai: `max` **thua** `base` ở n=2 (0.8533 vs 0.8650) → `ce_deep` của ft model
**có hại**, thêm bằng chứng vào làm hỏng xếp hạng. Với model gốc `max` thắng `base` ở cả
bốn n. Toàn bộ cấu trúc điểm bị đảo lộn.

So với 13/08 (−0,50, coi như hoà): bản "sửa cho sạch positive" làm **tệ đi 4 lần**.
Nhiều khả năng là **quên tai hại** — AITeamVN vốn ĐÃ là bge-m3 fine-tune tiếng Việt trên
dữ liệu lớn; huấn luyện tiếp 1 epoch trên 30.000 cặp tự dựng thì đè lên thứ nó vốn làm
tốt hơn ta nhiều.

**HAI LẦN THỬ, lần sau có cơ chế rõ ràng và dữ liệu sạch hơn, vẫn thua nặng hơn.**
Hướng này TẠM ĐÓNG với cấu hình đã dùng — nhưng đóng có điều kiện, không phải cấm tuyệt đối.

> ⚠️ **SỬA 19/08 — bản cũ ghi "đừng đổi base model" là SAI, đã bỏ.** Chính bảng ablation
> của nhóm cho thấy đổi mô hình nền ăn **+3 điểm** (AITeamVN 0.8900 vs bge-v2-m3 0.8600),
> tức đây là cần gạt TRÊN ngưỡng quy tắc 4. Và 19/08 còn có bằng chứng mạnh hơn nhiều:
> một mô hình **khác loại** bắt được **10/15** câu bài mình sai hoàn toàn.
> **"Dùng mô hình nào" là cần gạt đòn bẩy nhất tìm được cả tuần** — cấm nó là tự bịt
> đúng hướng duy nhất còn sống. Lệnh cấm cũ đã phủ nhầm lên một thứ khác hẳn về bản chất.

**Ba mức, phân biệt cho rõ:**

| việc | trạng thái | lý do |
|---|---|---|
| **Đổi mô hình nền / thử mô hình khác loại** | ✅ **MỞ, ưu tiên cao** | đo được +3 điểm và 10/15 câu khó. Trên ngưỡng, là cơ chế |
| **Fine-tune lại với dữ liệu đã sạch hơn** | 🟡 mở CÓ ĐIỀU KIỆN | chỉ khi nâng được tỉ lệ chọn đúng mẩu **trên 33%** — đó là nguyên nhân đã đo, không phải suy đoán |
| **Vặn epoch / lr / n_neg / loss trên đúng dữ liệu cũ** | 🔴 không nên | các nút này thường đổi **dưới 2 điểm** → dev300 mù, đo bao nhiêu lượt cũng không phân giải được. Muốn vặn thì phải nêu TRƯỚC cơ chế vì sao nó đổi ≥2 điểm |

LoRA rơi vào hàng thứ hai: nó chữa "quên kiến thức cũ", trong khi nguyên nhân đã đo là
**nhãn bẩn**. Sạch nhãn trước, rồi LoRA là lựa chọn đầu tiên — không phải ngược lại.

Tài sản để lại: `Ketqua_E/scores_dev300_ftv2_{tang1,deep_M20_K20}.json`.

Điểm sáng: quy tắc quyết định đặt TRƯỚC khi chạy đã làm đúng việc — **5h để đóng một
hướng, thay vì 10h nữa mang lên đề thi rồi mới biết.**

### (lịch sử) kế hoạch fine-tune v2 — đã thực hiện, đã thua

**Không vặn siêu tham số** (`epochs=1, lr=2e-5, n_neg=4, bs=8, max_length=512` y hệt
13/08). Đổi đúng MỘT thứ: **đoạn dùng làm ví dụ huấn luyện.**

`finetune_rerank.best_chunk` bản cũ dùng `max(parts, key=len(qs & tok(c)))` trên đoạn
`chunks_of` không gộp — **đúng hàm mà 17/08 đo được là kém BM25 mức đoạn 1,34 điểm.**
Đo trên 24 văn bản gold khó nhất của dev300, tỷ lệ positive trùng đoạn CE thích nhất:

| băm | hàm chọn | trùng đoạn tốt nhất | trong top-3 |
|---|---|---|---|
| `chunks_of` thô | `count` ← **bản 13/08** | **3/24 = 12,5%** | 7/24 |
| `chunks_of` thô | `bm25` | 5/24 | 9/24 |
| gộp 1800 | `count` | 6/24 | 9/24 |
| **gộp 1800** | **`bm25`** ← bản vá | **8/24 = 33%** | 11/24 |

**Gần 9/10 ví dụ dương của lượt 13/08 là bằng chứng SAI.** Với nhóm CE chấm ~0,00 trên
toàn văn bản gold, positive là dòng **mục lục** không chứa câu trả lời — model bị dạy
"dòng mục lục này trả lời câu hỏi này", đúng chế độ hỏng đang thấy lúc suy luận.

Tầng thứ hai: **train lệch inference.** Lúc chấm model thấy đoạn BM25 gộp ~1.460 ký tự;
lúc huấn luyện nó thấy đoạn term-overlap ~650. Bản vá gọi thẳng `DC.pick_chunks` —
**cùng một hàm, không chép lại**, vì chép là hai bên trôi khỏi nhau, mà trôi khỏi nhau
chính là bug này.

**KHÔNG dùng cổng chặn "đo tầng 1 cho rẻ".** Tầng 1 chấm `top_chunks` của D (~1.387 ký
tự, chọn kiểu khác) — đúng loại đầu vào model này KHÔNG được huấn luyện, đo ở đó sẽ đánh
giá thấp nó. Phải đo đủ hai tầng.

**Đọc kết quả — so với 0.9183** (model gốc, cùng cấu hình BM25+gộp1800/M=20/K=20/n=2):

| ft ra | quyết định |
|---|---|
| **≥ 0.9383** (+2,0) | thắng rõ → chạy đề thi 2 lượt với `ft_model_v2`, nộp |
| 0.9183 – 0.9383 | **vùng mù** → ĐỪNG đốt 10h đề thi. Bài học 18/08 ở trên |
| < 0.9183 | thua lần hai với dữ liệu đã sạch → **đóng hướng fine-tune vĩnh viễn** |

**Upload:** `finetune_rerank.py` (BẢN MỚI, đè) + `deep_chunk.py` (đã có thì thôi).
Chốt kiểm: `hard negative: 24.000/24.000` · `đoạn dài TB > 900 ký tự` (13/08 là ~650).

### ⛔ BTC KHÔNG CHO GỌI LLM DỊCH VỤ NGOÀI (xác nhận 19/08) — hệ quả

Hướng gọi API Gemini **chết cho bài nộp**. Nhưng cơ chế đã chứng minh KHÔNG chết:
điều đo được là **"mô hình KHÁC LOẠI đọc được văn bản dạng bảng/danh mục"**, không phải
"Gemini giỏi". → Kế hoạch B: **LLM mã nguồn mở chạy trên Kaggle GPU** (còn ~120h quota).

Toàn bộ số liệu Gemini vẫn dùng được cho **BÁO CÁO** như một phân tích đối chứng —
nó là thứ chứng minh nút thắt nằm ở BỘ CHẤM, không ở chọn mẩu.

### ⛔ CẦN GẠT K (số mảnh chấm mỗi văn bản) — ĐÃ ĐO 19/08, CHẾT. Đừng nâng K.

Mục "Ngưỡng giao D" từng để ngỏ *"2,5h dôi ra nâng K từ 20 lên 45"*. **Đã đo trên CPU
bằng `oracle_chunks_dev300.json`, không tốn giờ GPU nào:**

| K | mô phỏng (chỉ nâng gold) | × hệ số 0,6 |
|---|---|---|
| **20** ← đang dùng | 0.9250 | mốc |
| 25 | 0.9283 | **+0,60** |
| 30 · 40 · 60 | 0.9283 | +0,60 |
| 120 | 0.9317 | +0,80 |

**Nâng K gấp 6 lần chỉ ăn +0,80 điểm.** Dưới ngưỡng 2,0 rất xa, mà chi phí GPU tăng tuyến
tính theo K. Đóng cần gạt này.

### CHẨN ĐOÁN NHÓM C (4 câu "cứu được bằng chọn mảnh") — thực ra chỉ 2

Đo hạng của mảnh THẮNG theo đúng `pick_chunks` hiện tại:

| qid | gold | số mảnh | MAX mảnh | `ce_deep` đang có | hạng mảnh thắng | phán |
|---|---|---|---|---|---|---|
| 156454 | 279981 | 90 | 0.9787 | 0.4765 | **23** | K=20 hụt đúng **3 hạng** |
| 92466 | 102434 | 378 | 0.7554 | 0.1230 | **109** | cần K=110, vô vọng |
| 119814 | 247578 | 93 | 0.3196 | 0.3196 | 12 | **đã chấm rồi, thua vì kém thật** |
| 152252 | 249638 | 25 | 0.9370 | 0.9370 | 5 | **đã chấm rồi, thua vì kém thật** |

→ **2/4 ca không phải lỗi chọn mảnh** — mảnh tốt nhất đã được chấm, chỉ là đối thủ mạnh hơn.
Nhóm "chọn mảnh cứu được" thực chất chỉ còn **2 câu**, và 1 trong 2 cần K=110.

### CHẨN ĐOÁN 2 CÂU CÒN TREO (`1454`, `33938`) — là CÁI GIÁ CỦA `n_bm25=2`

Cả hai đều có gold ở **hạng CE số 4**, tức nằm trong top-5 nếu xếp thuần theo CE.
Chúng rớt vì `blend_bm25_first(n=2)` ép 2 suất đầu cho BM25, đẩy hạng CE 4 xuống vị trí 6.

Đối chiếu đầy đủ trên dev300:

| | số câu |
|---|---|
| n=2 CỨU được mà n=0 mất | 4 (`144234`, `50168`, `64622`, `74932`) |
| n=2 LÀM MẤT mà n=0 được | 4 (`156454`, `52126`, `1454`, `33938`) |
| **ròng trên dev300** | **hoà 0 câu** |

Nhưng trên đề thi thật n=2 = 0.8871 > n=0 = 0.8851, tức **n=2 lãi 2 câu**.
**Hai tập cho kết quả ngược dấu → đây là vùng dưới ngưỡng phân giải, đừng đụng vào `n`.**
Giữ n=2 vì nó thắng trên tập đo lớn hơn và không có nhiễu lấy mẫu.

### 🔥 GEMINI TRÊN 15 CÂU KHÓ — **BẮT ĐƯỢC 10/15.** Hướng đầu tiên vượt ngưỡng từ 13/08

`gemini_bench.py build --hard` → 15 câu bài mình SAI HẾT mà gold còn trong rổ 50 ứng viên.
**Gemini bắt 10/15**, gồm cả những ca đã bị đóng dấu "bất lực":

| qid | gold | Gemini | `ce` của mình | nhóm đã phân loại |
|---|---|---|---|---|
| 112344 | 105634 | ✅ hạng 1 | 0,011 | B1 cần đọc sâu |
| 128326 | 75112 | ✅ hạng 1 | 0,001 | B1 cần đọc sâu |
| 156454 | 279981 | ✅ hạng 1 | 0,477 | C chọn mảnh |
| 92466 | 102434 | ✅ hạng 3 | 0,123 | C chọn mảnh |
| 52126 | 301607 | ✅ hạng 1 | 0,010 | **E máy mù** |
| 119400 | 285994 | ✅ hạng 2 | 0,0004 | **E máy mù** |
| 138214 | 58662 | ✅ hạng 1 | 0,469 | **E máy mù** |
| **159444** | **228108** | **✅ hạng 4** | 0,0005 | **E máy mù — "LỖI NHÃN"** |
| 49070 | 129275 | ✅ hạng 4 | 0,0002 | B2 mù |
| 33938 | 274746 | ✅ hạng 4 | 0,889 | chưa chẩn đoán |
| 1524 · 16942 · 37542 · 65498 · 8946 | | ❌ | | |

**Kể cả `159444` cũng bị bắt** — ca tôi đã tuyên là lỗi nhãn không ai cứu được ("lệ phí"
xuất hiện 0 lần trong gold). **Tuyên bố đó SAI.** Xoá khỏi mọi lập luận về "trần của nhãn".

#### ⛔ CỔNG LỌC THEO ĐỘ TỰ TIN KHÔNG DÙNG ĐƯỢC — đã đo, đừng thử lại

Giả thuyết tự nhiên: chỉ gọi model ngoài khi `max ce` thấp. **Hỏng.**
**8/10 câu Gemini thắng có `max ce` của mình > 0,6** (có ca 0,994 · 0,997 · 0,999).
Mô hình của mình **tự tin VÀ sai**. Không ngưỡng nào tách được nhóm cần cứu ra khỏi
nhóm đang đúng — quét thresh 0,05→0,80 đều thế.

> **XÁC NHẬN LẠI 23/08 trên rổ fusion:** trong 13 câu sai còn gold trong rổ, **12 câu có
> đối thủ được chấm 0,87–1,00**. Cùng một hiện tượng, đo trên rổ khác, cùng kết luận.
> Đây là lý do CƠ CHẾ khiến mọi cổng lọc theo độ tự tin đều chết — không phải vặn ngưỡng sai.

#### PHÉP TÍNH RÒNG — THAY TOÀN BỘ bằng Gemini là LỖ

Trên 50 câu chạy sạch: trong 46 câu mình ĐÚNG, Gemini **làm hỏng 2 → tỉ lệ phá 4,3%**.

| | |
|---|---|
| được: 15 câu cứu được × 67% | **+10 câu** |
| mất: 278 câu đang đúng × 4,3% | **−12 câu** |
| **ròng** | **−2 câu = −0,70 điểm** |

**→ Gemini giỏi câu KHÓ, dở câu DỄ. Bài mình ngược lại. Thay thế = lỗ.**

#### CỬA DUY NHẤT: GHÉP, giữ 3 suất đầu của mình

Quét trên 50 câu đã chạy (offline, 0 chi phí):

| cách chốt top-5 | recall@5 |
|---|---|
| chỉ bài mình | 0.9100 |
| chỉ Gemini | 0.9000 |
| 1 mình + 4 Gemini | 0.9000 |
| 2 mình + 3 Gemini | 0.9000 |
| **3 mình + 2 Gemini** | **0.9400** |
| 4 mình + 1 Gemini | 0.9300 |

Cơ chế: 3 suất đầu bảo vệ câu dễ, 2 suất cuối vốn hay phí thì giao cho bộ chấm khác loại.

⚠️ **+3,00 điểm này đo trên n=50 → chỉ bằng 1,5 câu. CHƯA đủ tin.** Tỉ lệ phá 4,3% ước từ
46 câu, sai số rất rộng. **Số đáng tin duy nhất hiện nay là 10/15 trên câu khó.**

#### VIỆC TIẾP THEO, theo đúng thứ tự — đọc mục này trước khi làm gì

0. **HỎI BTC: có được gọi API ngoài không?** Miễn phí, 5 phút, và nếu KHÔNG thì cả hướng
   này chết ngay — khỏi tốn thêm giờ nào. **Làm trước mọi thứ khác.**
1. **Chuyển sang API, bỏ giao diện chat.** Chat làm tối đa 5 câu/lượt; đề thi 1.000 câu =
   200 lượt tay, không khả thi. Flash Lite qua API rẻ, 1.000 câu chỉ vài đô.
2. **Đo TỈ LỆ PHÁ trên ~150 câu bài mình ĐANG ĐÚNG.** Đây là con số quyết định lãi/lỗ,
   hiện chỉ có 2/46. Không có nó thì đừng mang lên đề thi.
3. **Chốt cách ghép** (3+2 vs 4+1) — offline, 0 chi phí, làm sau khi có dữ liệu bước 2.
4. Chạy đề thi, nộp. **Giữ nguyên `submission_v2_M20_n2.zip` (0.8871) làm bài an toàn.**

**Kế hoạch B nếu BTC cấm API:** thay Gemini bằng một LLM tiếng Việt mã nguồn mở chạy trên
Kaggle GPU (còn ~120h quota). Cơ chế giống hệt — điều đã chứng minh là "model KHÁC LOẠI đọc
được văn bản dạng bảng/danh mục", không phải "Gemini giỏi".

### ✅ ĐO GEMINI LẠI CHO ĐÚNG 19/08 — **HOÀ, và LẬT một kết luận của chính mình**

Chạy `gemini_bench.py` trên **50 câu đầu dev300**, rổ 50 ứng viên BM25 kèm trích đoạn.
Đầu vào KHÔNG có submission nào của mình. Tự chấm, 0 lượt nộp, 0 giờ GPU.

| | recall@5 trên 50 câu |
|---|---|
| Gemini 2.5 Flash Lite | **0.9000** |
| bài chốt (cùng 50 câu) | **0.9100** |

**Hoà** — chênh 0,5 câu. Đối chiếu từng câu: **2-2**.

| | câu |
|---|---|
| Gemini đúng / mình sai | `112344`, `119400` |
| mình đúng / Gemini sai | `11534`, `12732` |
| cả hai cùng sai | `11536`, `12654` — **cả hai đều gold NGOÀI top-100 → của D** |

Chốt kiểm sạch: **250/250 mã hợp lệ, không bịa số nào**, không câu nào thiếu id.

#### ⚠️ LẬT KẾT LUẬN: nhóm "MÁY MÙ" KHÔNG phải trần tuyệt đối

Mục kiểm kê dưới ghi 12 câu "máy mù — đọc hết vẫn không nhận ra" là **không có phương án
nào**. **Sai.** `119400` chính là một trong nhóm đó, và Gemini xếp gold lên **hạng 2**.

| `119400`, gold `285994` (Công văn 1682 tuyển sinh lớp 10) | |
|---|---|
| `ce` của mình | 0,00015 |
| **MAX trên MỌI mảnh** (oracle, 104 mảnh) | **0,00035** |
| BM25 xếp | hạng 9 |
| Gemini xếp | **hạng 2** |

Cross-encoder đọc hết mọi mảnh và chấm ~0; mô hình ngôn ngữ đọc **đúng đoạn trích đó** và
nhận ra ngay. → Khớp chính xác chẩn đoán "văn bản dạng **bảng biểu / danh mục / công văn**
nằm ngoài thứ AITeamVN được huấn luyện để đọc". Chẩn đoán đó dự đoán model KHÁC LOẠI sẽ
đọc được — **đã được xác nhận bằng thực nghiệm**.

→ **Sửa cách phát biểu ở mọi chỗ, kể cả báo cáo:** không phải "hết đường kỹ thuật", mà là
**"hết đường với kiến trúc cross-encoder hiện tại"**. Trần 12 câu kia là trần của BỘ CHẤM,
không phải trần của bài toán.

#### Tín hiệu mạnh nhất: 2/2 trên đúng nhóm câu khó

Trong 50 câu đã chạy, bài mình sai 4 câu. Hai câu gold còn trong rổ ứng viên là `112344`
(nhóm "cần đọc sâu hơn") và `119400` (nhóm "máy mù") — **Gemini bắt được CẢ HAI**.
Hai câu còn lại gold nằm ngoài top-100 nên không ai chạm tới.

**2/2 trên n=2 thì chưa kết luận được**, nhưng hai lần thắng rơi vào đúng hai nhóm đã được
phân loại TRƯỚC bằng hai lý do khác nhau — theo phân biệt "cơ chế vs siêu tham số" của
chính file này, đây là loại bằng chứng đáng tin.

→ **VIỆC TIẾP THEO, rẻ và quyết định:** `python gemini_bench.py build --hard` → đúng
**15 câu** bài mình đang sai mà gold vẫn trong rổ, 3 batch. Bắt được ≥8/15 thì hướng
"mô hình ngôn ngữ chấm lại các văn bản CE cho ~0" là thật, trần ~3,3 điểm dev300.
Bắt được ≤3/15 thì đóng, và 2/2 vừa rồi là may.

#### Hai điều phải ghi kèm nếu định dùng thật

1. **Gemini KHÔNG tất định.** Chạy hai lần cùng batch_01 ra kết quả khác nhau, tự trùng
   chỉ **4,2/5 mã**. Bộ chấm của mình tất định. Đây là trần đo lường: chênh lệch nhỏ hơn
   mức tự-lệch của nó thì không đọc được.
2. **Chat không kham nổi lô lớn.** 20 câu/batch (1,2MB) → nó lặng lẽ chỉ làm 5 câu rồi
   xin thêm file. Phải hạ `Q_PER_BATCH=5`. Cùng họ lỗi "im lặng cắt bớt" đã làm mất 275
   câu ở lượt nộp hỏng bên dưới. Muốn chạy 1.000 câu thì phải qua API, không qua chat.

### ⛔ "ĐO GEMINI 2.5 FLASH LITE" 19/08 — **PHÉP ĐO HỎNG. GEMINI CHÉP LẠI BÀI CỦA MÌNH.**

Nộp `Ketqua_E/submission_gemini_hybrid.zip` → public LB 0.8853. **Con số này KHÔNG nói gì
về Gemini.** Kiểm chéo sau khi biết đầu vào:

> Đầu vào đưa cho Gemini gồm: `public-official.json` + `selected-contexts.zip` +
> **`submission_B_M20.json` (bài nộp 0.8840 của chính mình)**.

| đối chiếu | trùng TB | trùng cả 5 id | y hệt cả THỨ TỰ |
|---|---|---|---|
| **Gemini vs `submission_B_M20`** | **5,000/5** | **725/725 = 100%** | **725/725 = 100%** |
| Gemini vs bài chốt v2 | 4,604/5 | 470 (64,8%) | 387 (53,4%) |

**Gemini không xếp hạng gì cả — nó chép nguyên `submission_B_M20` rồi trình bày lại thành
bảng markdown.** 725 câu, 3.625 id, đúng từng id, đúng từng vị trí.

**Số học xác nhận:** bài lai = 725 câu của B_M20 (0.8840) + 275 câu của v2 (0.8871).
Trộn thuần: `0,725×0.8840 + 0,275×0.8871 = 0.8849`. Thực tế **0.8853** — lệch 0,4 câu.
Đúng bằng một phép trộn hai bài cũ, không có đóng góp nào từ mô hình ngoài.

**HỆ QUẢ — bắt buộc:**

1. **KHÔNG được viết vào báo cáo** là "đã đối chứng với mô hình ngôn ngữ đời mới". Chưa
   đối chứng gì hết. Viết ra là sai sự thật và sẽ bị bắt lỗi ngay nếu ai hỏi số liệu.
2. **Đã đốt một lượt nộp cho một phép đo rỗng.** Bảng E7 giữ dòng này để nhớ, đánh dấu rõ.
3. Muốn đo thật thì đầu vào **KHÔNG được chứa bài nộp của mình** — chỉ đưa câu hỏi + rổ
   ứng viên (top-100 BM25) và bắt xếp hạng. Đưa đáp án vào thì chép lại là đường rẻ nhất.

**Bài học phương pháp (cùng họ với "guard kiểm bằng text tự bắn vào chân" ở cuối file):**
tôi đã đo độ trùng 4,60/5 với bài chốt v2 và ghi nhận là "cao bất thường" — nhưng **không
đối chiếu với `submission_B_M20`, đúng file đã đưa cho Gemini**. So sai mốc nên bỏ lỡ dấu
hiệu 100%. → **Trước khi nộp bất kỳ kết quả từ nguồn ngoài: đối chiếu output với TỪNG file
đã đưa vào, không chỉ với bài hiện hành.** Kiểm này mất 10 giây và cứu được một lượt nộp.

### ⛔ HƯỚNG "GỢI Ý LIÊN QUAN" (kiểu Google) — ĐÃ ĐO 19/08, THUA CẢ BA BIẾN THỂ

Câu hỏi đặt ra: nhóm BẤT LỰC lệch **nhiệm vụ**, vậy sao không xếp hạng theo **độ liên quan
/ gợi ý** thay vì ngữ nghĩa? Đã đo hết trên CPU, 0 giờ GPU, dùng
`scores_dev300_bm25pick_merge1800_M20_K20.json`. **Cả ba biến thể đều THUA.**
(Đã tái lập đúng n=0..3 = 0.9217/0.9117/0.9183/0.9100 trước khi đo → code kiểm đúng.)

| biến thể | cơ chế | kết quả |
|---|---|---|
| **prior độ phổ biến** | `ce + λ·log(1+số lần doc là gold ở train)`, đếm trên 6.700 câu NGOÀI dev300 | **hại đơn điệu**: λ=0,01 → 0.9117 (−0,66); λ=0,05 → 0.9100; λ=0,4 → 0.8567 |
| **blend thích ứng theo độ tự tin** | maxCE thấp = reranker không chắc → nới `n_bm25` | **mọi cấu hình ≤ 0.9183**. Quét thresh ∈ {0,1…0,7} × n_lo ∈ {2…8}, không ô nào vượt mốc. **ĐO LẠI 23/08 trên rổ fusion: vẫn không ô nào vượt 0.9350 → ĐÓNG VĨNH VIỄN** |
| **đồ thị trích dẫn** | gold và doc điểm cao có chung "Căn cứ …"? | **0 cạnh chung** trên ca 159444 với cả 5 doc top-5 |

**Vì sao prior chết:** 74,8% gold của dev300 ĐÃ từng là đáp án ở train — nhưng đối thủ
trong cùng top-100 cũng vậy (chúng cùng chủ đề). Prior đúng nhưng **không phân biệt được**,
nên chỉ thêm nhiễu vào thứ tự CE vốn đã tốt.

**Vì sao hướng "gợi ý" không chuyển sang được — số liệu quyết định:**

| dạng câu hỏi | số câu train | số doc gold khác nhau | 5 doc phổ biến nhất phủ |
|---|---|---|---|
| lệ phí / mức thu | 76 | **63** | 22,9% |
| thủ tục / hồ sơ | 369 | **302** | 8,3% |
| thời hạn / bao lâu | 254 | 210 | 10,0% |
| xử phạt / vi phạm | 351 | 135 | 25,9% ← đặc nhất |

**Gần như mỗi câu trỏ vào một văn bản mới.** Google gợi ý được vì một mẫu truy vấn có hàng
triệu quan sát; ở đây một mẫu câu hỏi có 76 quan sát trỏ vào 63 đích. Không có gì để gợi ý.

#### CA 159444 — lỗi NHÃN (đã xác minh; ĐỌC TIẾP mục sửa lại bên dưới trước khi trích dẫn)

Mổ ca `159444` ("Lệ phí cấp đổi giấy phép kinh doanh dịch vụ lữ hành quốc tế là bao nhiêu?"):

- gold `228108` = QĐ 3684/QĐ-BVHTTDL công bố thủ tục hành chính. Chuỗi **"lệ phí" xuất
  hiện ĐÚNG 0 LẦN** trong 45.307 ký tự. Không có số tiền nào. Chỉ có dòng danh mục
  *"71. Thủ tục cấp đổi giấy phép kinh doanh dịch vụ lữ hành quốc tế"*.
- top-5 của reranker: Luật Du lịch 2017 · **TT 44/2023/TT-BTC mức thu phí, lệ phí** ·
  TT 120/2021/TT-BTC · TT 74/2022/TT-BTC · Luật Phí và lệ phí 2015.

→ **Reranker đang trả lời ĐÚNG câu hỏi; nhãn mới là thứ trỏ chỗ khác.** Nhãn nhiều khả năng
là "văn bản mà người trả lời trích dẫn", không phải "văn bản chứa câu trả lời". Không mô
hình nào học được điều đó từ 6.700 ví dụ one-shot.

Ca này gold ở **hạng BM25 số 3**, nên `n_bm25=3` cứu được nó — nhưng n=3 = 0.9100 trên
dev300 và 0.8424 trên public, thua rõ. Cứu một câu, hỏng nhiều câu khác. Đã chốt, đừng đụng.

#### ⚠️ SỬA LẠI KẾT LUẬN TRÊN — "trần của nhãn" là KHÁI QUÁT VỘI TỪ MỘT CA

Ban đầu tôi viết "nhóm BẤT LỰC là lỗi nhãn". **Sai — chỉ đúng với ca 159444.** Sau khi mở
cả 8 ca (lọc: gold trong top-100, trượt top-5, điểm CE < 0,01) và đối chiếu với
`oracle_chunks_dev300.json` (điểm CE của **mọi** đoạn trong văn bản gold):

| qid | gold | điểm hiện tại | MAX mọi đoạn | cần để vào top-5 | phán |
|---|---|---|---|---|---|
| 16942 | 102434 (BLTTHS) | 0,00023 | **0,9997** | 0,8761 | **CỨU ĐƯỢC bằng chọn đoạn** |
| 128326 | 75112 (NĐ 96/2016) | 0,00095 | **0,9999** | 0,0347 | **CỨU ĐƯỢC bằng chọn đoạn** |
| 49070 | 129275 (TCVN 12873) | 0,00017 | 0,0064 | 0,4228 | CE mù dù đọc HẾT 8 đoạn |
| 8946 | 32928 (QĐ 4291/TLĐ) | 0,00045 | 0,0130 | 0,0152 | CE mù, **sát ngưỡng** |
| 52126 | 301607 (TT 35/2022) | 0,00960 | 0,0015 | 0,0065 | CE mù |
| 119400 | 285994 (CV 1682 SGDĐT) | 0,00035 | 0,0006 | 0,0253 | CE mù dù có 199 đoạn |
| 37542 | 107157 (TT 05/2005) | 0,00007 | 0,0000 | 0,0006 | CE mù, văn bản chỉ 9.107 ký tự |
| 159444 | 228108 (QĐ 3684) | 0,00051 | 0,0085 | 0,0137 | **lỗi nhãn thật** |

**Ba điều phải sửa trong nhận thức:**

1. **2/8 ca KHÔNG hề bất lực** — CE chấm 0,9997 và 0,9999 cho đúng đoạn, chỉ là bộ chọn
   đoạn không bao giờ đưa đoạn đó vào K=20. Ca 128326 chỉ cần 0,0347 mà có đoạn 0,9999
   nằm trong 63 đoạn đã gộp. **Đây là lỗ hổng chọn đoạn còn sót, không phải trần.**
2. **Chỉ 1/8 là lỗi nhãn được chứng minh** (159444, "lệ phí" 0 lần). Các ca còn lại
   văn bản gold CÓ chứa nội dung liên quan — đếm được: `diện tích`=18 (49070),
   `người giám định`=45 (16942), `nguyên giá`=44 (52126), `lớp 10`=65 (119400),
   `phụ cấp trách nhiệm`=15 (37542). **Không thể gọi chung là nhãn sai.**
3. **Mẫu số chung thật của nhóm CE mù: DẠNG VĂN BẢN, không phải nhãn.** Gold của chúng là
   TCVN / Công văn / Quyết định công bố danh mục / Thông tư khung — toàn bảng biểu, danh
   mục, phụ lục. AITeamVN học trên văn xuôi pháp lý nên chấm ~0 trên nội dung dạng bảng.
   Ca 37542 là bằng chứng sạch nhất: văn bản chỉ 9.107 ký tự (5 đoạn sau gộp) → CE đã đọc
   TOÀN BỘ và vẫn ra 0,0000. Không liên quan gì đến chọn đoạn hay nhãn.

→ **Cách gọi đúng: “trần của mô hình trên văn bản dạng bảng/danh mục”**, kèm 1 ca lỗi nhãn.
Viết vào báo cáo theo cách này, đừng viết "nhãn sai" — vừa không đúng số liệu, vừa dở.

→ **Việc còn cửa (chưa làm): soi lại vì sao bộ chọn đoạn bỏ lỡ đoạn 0,9997/0,9999 ở 2 ca
trên.** Trần chỉ +0,67 điểm (2 câu) nên **dưới ngưỡng quy tắc 4, đừng chạy GPU vì nó** —
nhưng chẩn đoán trên CPU thì miễn phí và có thể lộ ra lỗi hệ thống ảnh hưởng rộng hơn 2 ca.

**Bài học phương pháp:** kết luận "trần của nhãn" viết ra sau khi mở **đúng 1 ca**. Mở nốt
7 ca còn lại mất 10 phút CPU và lật ngược 2/8. **Đừng khái quát nhóm từ một mẫu** — cùng
loại lỗi với bẫy dev150 ngày 11/08.

### E ĐÃ HẾT ĐƯỜNG KỸ THUẬT. Chốt 0.8871.

Kiểm kê 24 gold còn cứu được trên dev300, sau khi mọi hướng đã chạy:

| nhóm | số | trạng thái |
|---|---|---|
| chọn đoạn cứu được | 9 | **ĐÃ THU HOẠCH** (BM25 + gộp 1800, LB +0,31) |
| cần M>20 | 8 | đắt, lợi ít, đã tính và bỏ |
| **BẤT LỰC** — CE chấm ~0,00 toàn văn bản | **7** | fine-tune là đường duy nhất, **đã thua 2 lần** |
| *(ngoài top-100, không nằm trong 24)* | *7* | **của D** |

Nhóm 7 "BẤT LỰC" là lệch ngữ nghĩa nhiệm vụ: gold là **văn bản nền tảng**, câu hỏi hỏi
**tình huống áp dụng cụ thể**. Không hàm chọn đoạn nào chạm tới, và fine-tune — thứ duy
nhất về nguyên tắc chạm được — đã thua hai lần. **Đó là trần thật của kiến trúc này.**

Còn lại đúng hai việc, không việc nào là của E về mặt kỹ thuật:

1. **D nâng recall@100** — 7/314 gold nằm ngoài top-100 (2,2%), E không với tới.
2. **Chốt `submission_v2_M20_n2.zip` (0.8871) và dồn sức vào báo cáo.**

Bài nộp đó an toàn cho vòng private: nó được chọn bằng cơ chế đo trên dev300, không phải
fit vào public LB.

## TRẠNG THÁI 17/08 22:29 — ĐÃ NỘP B. **PUBLIC LB = 0.8840** — đọc mục này trước

**`submission_B_M20.zip` → 0.8840. Mốc mới. Baseline cũ 0.8573 → Δ +2,67 điểm ≈ 27 câu.**
Bằng hoặc trên đỉnh dải dự báo (0,875-0,88). Deepchunk ăn thật trên đề thi, không chỉ dev.

**Độ lệch dev→public thu hẹp: −2,43** (0.9083 → 0.8840), không phải −3,1 như hai lần trước.
Dev300 dự báo hơi bi quan ở cấu hình này. Ghi nhận nhưng **chưa đổi hằng số −3,1** — một
điểm quan sát không đủ; đợi LB của A xem lệch có ổn định quanh −2,4 không.

**Trần candidate public = 0.9875 → còn 10,35 điểm dư địa.** Vẫn nằm hết ở thứ tự trong
top-100, không ở việc tìm thêm ứng viên.

### ĐÃ NỘP CẢ HAI — M=20 THẮNG DỨT KHOÁT (22:48)

`submission_A_M10.zip` → **0.8713**. B hơn A **+1,27**, gần gấp đôi cái dev300 báo (+0,66).
**B là bài chốt, đóng chuyện M.**

| bài | dev300 | public | Δ vs baseline 0.8573 |
|---|---|---|---|
| baseline n=2 | 0.8883 | 0.8573 | — |
| A, M=10 | 0.9017 | **0.8713** | +1,40 *(dev báo +1,34)* |
| B, M=20 | 0.9083 | **0.8840** | +2,67 *(dev báo +2,00)* |
| **A → B** | +0,66 | **+1,27** | |

**Hai điều đọc được:**

1. **Deepchunk chuyển dev→public gần 1:1.** M=10 dev báo +1,34, public ăn +1,40. Hiệu ứng
   đủ lớn (>2 điểm) thì dev300 đo đúng — đừng vứt dev300 đi.
2. **Dưới 2 điểm thì dev300 MÙ, không phải sai.** +0,66 = **2 câu** trên 300, dưới nhiễu
   ±1,5 câu; bootstrap 77,8% nghĩa là "không có thông tin", không phải "hơi yếu". Public
   1000 câu **cùng một bộ đề nên không có nhiễu lấy mẫu** → đo ra +1,27 = 12,7 câu.
   **Hệ quả mới: với hiệu ứng dưới 2 điểm, LB là dụng cụ đo duy nhất, và nó tốn 0 giờ GPU.**

**ĐỪNG đọc thành "nhân delta của dev với 1,9".** Không có hệ số quy đổi. dev300 không đo
sai +0,66 — nó không đo được. Xây lý thuyết trên tỷ số của một phép đo 2-câu = bẫy 11/08.

**Cám dỗ phải chặn: đừng dùng LB để vặn siêu tham số.** Phân biệt hai loại câu hỏi:

| loại | ví dụ | dùng LB? |
|---|---|---|
| **cơ chế** — dự đoán trước, thắng đều nhiều cấu hình | M=10 vs M=20 · chọn đoạn bằng embedding | **có**, LB là dụng cụ đúng |
| **siêu tham số** — chọn hậu nghiệm trên chính dữ liệu đang đo | α=0,3 vs `max` (hơn 0,17 = nửa câu) · δ trong `max(ce, ce_deep−δ)` | **không** — fit vào 1000 câu public, mất trắng nếu có vòng private |

**Chưa biết có vòng private LB không → hỏi BTC/trưởng nhóm.** Câu trả lời đổi hẳn mức
liều được phép dùng LB.

## PHÂN VAI MỚI 17/08 — E nhận trọn việc chunk, D chuyển sang chi phí

**Chunk + sinh `top_chunk` đã BÀN GIAO cho E, E toàn quyền tối ưu.** Thực chất chỉ chính
thức hoá cái đã đúng sẵn: `deep_chunk.py` tự băm lại toàn văn từ `selected-contexts/`,
không dùng gì của D. **E không còn phải chờ ai** — mục "Đang chờ D #3 (bi-encoder D4)" chết.

Dư địa 10,35 điểm còn lại trên public (0.8840 → trần 0.9875) chia:

| của ai | dư địa | là gì |
|---|---|---|
| D | **1,25 điểm** | gold ngoài top-100 hoàn toàn. E không chạm tới được |
| **E** | **9,10 điểm** | thứ tự bên trong 100 ứng viên |

→ D còn đúng một đòn điểm và nó gần cạn. Mọi thứ khác D làm là **chi phí**.
~88% dư địa còn lại là của E.

### Hai cần gạt của E — cả hai đều là MỘT dòng code

1. **Chọn đoạn** — `deep_chunk.py:80`, `sorted(parts, key=lambda p: -len(qs & p[1]))`.
   Đếm từ trùng. 16 câu kẹt = 16 văn bản ĐÚNG mà 20 đoạn từ-trùng-nhất vẫn không chứa
   câu trả lời (trung vị 125 đoạn/văn bản, max 744). Thay bằng model embedding tiếng Việt
   có sẵn trên HF — không cần huấn luyện, rẻ hơn cross-encoder nhiều, cache được.
   **Nhớ bài học `max > replace`: CỘNG đoạn của bi-encoder vào, đừng thay thế.**
2. **Băm đoạn** — `chunks_of` trong `make_candidates_fallback.py`. Kích thước đoạn +
   độ chồng lấn. **MỚI được quyền đụng** — trước là tham số của D, E phải nhận nguyên.
   Nếu 125 đoạn/văn bản là do băm quá vụn thì sửa từ gốc rẻ hơn chọn khéo trong 125.

Đo cả hai trên dev300 trước, ngưỡng ≥2,0 điểm (quy tắc 4). Mỗi lượt một biến (quy tắc 3).

## TRẠNG THÁI 18/08 — BM25 CHỌN ĐOẠN + GỘP 1800 ĐÃ ĐO XONG. THẮNG Ở CẢ BỐN n.

`chunk_v2_run.ipynb` chạy 3h, 108.302 đoạn, nhịp **10,0 đoạn/s**. Kết quả dev300:

| biến thể | n=0 | n=1 | n=2 | n=3 |
|---|---|---|---|---|
| base | 0.8650 | 0.8633 | **0.8883** ✓ tầng 1 nguyên vẹn | 0.8683 |
| **max (BM25+gộp1800)** | **0.9217** | 0.9117 | **0.9183** | 0.9100 |
| replace | 0.9150 | 0.9133 | 0.9183 | 0.9033 |
| max (cấu hình cũ) | 0.8983 | 0.9017 | 0.9083 | 0.9033 |
| **Δ mới − cũ** | **+2,34** | **+1,00** | **+1,00** | **+0,67** |

**Thắng cả bốn n, trung bình +1,25.** Đây mới là bằng chứng, không phải +1,00 ở n=2 —
nhiễu thì hướng phải ngẫu nhiên, không cùng dấu bốn lần. Cùng lập luận đã dùng cho
M=20 vs M=10, và lần đó public LB xác nhận (+1,27).

Tài sản mới: `Ketqua_E/scores_dev300_bm25pick_merge1800_M20_K20.json` (300/300 câu đủ 20/20).

### HỆ SỐ 0,6 — ước từ oracle phải nhân 0,6

Oracle dự đoán 0.9250 (+1,67), thực tế 0.9183 (+1,00) = **60%**. Nguyên nhân đã lường
trước: mô phỏng offline chỉ nâng điểm văn bản **gold**, lượt thật nâng cả **19 đối thủ**
nên chúng nuốt mất 40% phần thắng. **Mọi ước từ `oracle_chunks_dev300.json` về sau nhân
0,6** trước khi so với ngưỡng quy tắc 4.

Nhịp: đoạn dài gấp 2,2 lần (650 → 1.460 ký tự) chỉ làm chậm **22%** (12,9 → 10,0 đoạn/s),
không phải gấp đôi. Trung vị đoạn/văn bản 125 → **42**, và **27% văn bản có ≤20 đoạn** nên
`pick_chunks` trả về HẾT — với một phần tư văn bản thì không còn phải chọn nữa. Đó là cơ
chế thật của việc gộp đoạn.

### ĐỈNH `n_bm25` VỪA DỜI SANG n=0 — ĐỪNG ĐỔI, NHƯNG ĐÁNG THỬ BẰNG LB

`max n=0` = 0.9217 > `max n=2` = 0.9183. Chênh **+0,34 = 1 câu** trên dev300.
Đối chọi: public LB n=0 = 0.8350 vs n=2 = 0.8573 — **hơn 22 câu, 1000 câu, không nhiễu
lấy mẫu**. Một câu dev300 không lật nổi 22 câu LB. **Giữ n=2.** Đây đúng bẫy 11/08.

Nhưng **cơ chế hợp lý**: `blend_bm25_first` ép 2 suất vì reranker hay vứt nhầm thứ BM25
chọn đúng. Reranker khoẻ lên thì giá trị cứu của blend giảm, cái giá 2 suất thì không đổi.
→ Có `scores_public` mới rồi thì **sinh cả n=2 lẫn n=0, nộp cả hai, 0 giờ GPU**. Đây là
câu hỏi CƠ CHẾ ("blend còn đáng không sau khi reranker khoẻ lên"), không phải vặn hệ số.

### LƯỢT ĐỀ THI — `K=20`, TÁCH HAI LƯỢT. Chạy `final_v2_run.ipynb` HAI LẦN (~5,0h/lượt)

**ĐÃ CÂN NHẮC HẠ K XUỐNG 15 RỒI BỎ. Đừng đề xuất lại trừ khi thiếu quota.**

`ce_deep` = max trên K đoạn → bớt đoạn thì mọi văn bản chỉ có thể **TỤT**, không bao giờ
tăng. Hạ K là đòn **tiết kiệm**, không phải đòn **điểm**. Có 26h quota thì không đổi điểm
lấy giờ.

Bằng chứng đã đo trên oracle (đừng đo lại): **3/24 văn bản có đoạn thắng ở hạng BM25
16-20**, cắt xuống 15 mất thật — ca nặng nhất mất **0,478** điểm CE (65498/285041:
0.236 → 0.714). Recall@5 tình cờ không đổi vì cả ba ca đó đằng nào cũng thua (hạng 5 của
chúng là 0.949). **May, không phải cơ chế.** Và oracle chỉ có 24 văn bản đang HỤT top-5 —
**275 gold đang THẮNG hoàn toàn không có dữ liệu**, không biết chúng có phụ thuộc đoạn
hạng 16-20 hay không.

| | đoạn (đo thật) | giờ @10 đoạn/s | dư so trần 12h |
|---|---|---|---|
| **lượt A** `SKIP,M_DOC = 0,10` | ~182.000 | 5,0h | **2,4x** |
| **lượt B** `SKIP,M_DOC = 10,20` | ~177.400 | 5,0h | **2,4x** |
| ~~gộp một lượt K=20~~ | 355.000 | 9,9h | 17% — **cấm** |

**Quota nhiều KHÔNG cứu được trần 12h** — trần đó là **per-run**, tài khoản phụ không nới,
và commit bị cắt thì Kaggle **không xuất bản gì cả**. Kaggle cấp T4 hay P100 tuỳ lúc,
chênh ~2x → dư 17% không sống nổi qua xổ số đó.

**Notebook dùng CHUNG cho cả hai lượt, đổi đúng hai dòng:**

```python
SKIP, M_DOC = 0, 10                                  # lượt B:  10, 20
SCORES_IN = f"{INPUT_DIR}/scores_public.json"        # lượt B:  .../scores_public_bm25merge_M10_K20.json
```

**Upload:** trước lượt A — `deep_chunk.py` (bản mới) + `Ketqua_E/scores_public.json` (6,8MB).
Trước lượt B — output lượt A (`scores_public_bm25merge_M10_K20.json`).

Đã dry-run **cả hai lượt** trên 40 câu dev300 với điểm giả: `skip` giữ nguyên `ce_deep`
lượt A **0 lệch**, `ce` tầng 1 **0 cặp bị ghi đè**, cả hai lượt ra submission sạch.

Notebook có: **Bước 0 in dấu vân tay file code vào log** · checkpoint mỗi 100 câu + tự
resume · guard chặn qid trùng dev · guard đầu vào (lượt A phải nhận tầng 1 SẠCH, lượt B
phải nhận đúng 10/10 văn bản có `ce_deep`) · bốn phép kiểm chéo `skip` · soi lại zip từ đĩa.

#### Dấu vân tay chuẩn — đối chiếu trong log Kaggle (đo trên máy 18/08)

| file | bytes | sha256[:12] |
|---|---|---|
| **`deep_chunk.py`** | **14.621** | **`2a8c193a1e4a`** ← bản BM25 + MERGE_CHARS |
| `rerank_from_d.py` | 12.422 | `8688f4b7308d` |
| `submission.py` | 16.732 | `9734ddd4255d` |
| `make_candidates_fallback.py` | 14.010 | `30bd05a6eef8` |
| `scores_public.json` | 6.806.629 | `4a752fc89cb9` |
| `public-official.json` | 186.517 | `adaa250c5469` |

`deep_chunk.py` ra hash khác hoặc **8.659 bytes** = bản CŨ, dừng, upload đè.
Bước 0 còn `assert` bốn thứ hành vi (`MERGE_CHARS` tồn tại · `idf.get` có trong
`pick_chunks` · `len(qs & p[1])` KHÔNG còn · `K1,B == 1.5,0.75`) và chạy `__main__`
self-test của `deep_chunk.py` — chốt mạnh nhất, vì self-test có ca BM25 phải chọn đoạn
chứa term hiếm thay vì đoạn lặp nhiều term rác, đúng ca bản `count` cũ trượt.

**Đừng tin timestamp file.** Mount hiển thị lệch múi giờ (Windows thấy 23:00 17/08,
Linux thấy 16:43 17/08). Kích thước + hash + self-test mới là bằng chứng.

**Lượt A tự sinh bài nộp M=10** — bảo hiểm nếu lượt B trục trặc.

**Sinh HAI bài nộp mỗi lượt, 0 giờ GPU thêm: `n=2` (chốt) và `n=0` (đo cơ chế đỉnh vừa
dời). Nộp n=2 TRƯỚC.** Mốc phải vượt: **0.8840**. Dưới 0.884 là tụt, quay về bài B cũ.

### ORACLE ĐÃ CHẠY XONG 17/08 — KHÔNG CẦN EMBEDDING. Sửa hàm chọn đoạn là đủ.

`Ketqua_E/oracle_chunks_dev300.json` (7.362 đoạn, 9,5 phút GPU) giờ cho quét mọi hàm
chọn đoạn **trên CPU**. Quét xong rồi, M=20/K=20 giữ nguyên, chỉ đổi cách chọn/băm:

| hàm chọn | `chunks_of` gốc | gộp 1800 ký tự |
|---|---|---|
| `count` (cũ) | 0.9083 ← mốc | 0.9183 (+1,00) |
| `idf` | 0.9150 | 0.9183 |
| `idf/√len` | 0.9117 | 0.9217 |
| **`bm25` mức đoạn ← CHỐT** | **0.9217 (+1,34)** | **0.9250 (+1,67)** |
| lai `count`+`bm25` | 0.9183 | 0.9250 |
| *chọn HOÀN HẢO (trần)* | *0.9250* | *0.9317 (+2,34)* |

**Bản cũ hỏng ở chỗ đếm term thô.** `len(qs & terms)` không IDF, không chuẩn hoá độ dài
→ thưởng đoạn dài, coi "của" ngang "lữ hành". BM25 mức đoạn (idf tính trong phạm vi văn
bản + tf bão hoà + chuẩn hoá độ dài) ăn **+1,34, không thêm một dependency nào**.

**ĐỪNG thêm model embedding.** Khoảng cách từ `bm25`+gộp (0.9250) tới trần (0.9317) chỉ
còn **+0,67 = 2 câu**. Một model 2GB tranh nhau đúng 2 câu đó, dưới mọi ngưỡng đo được.

**Lai `count`+`bm25` THUA `bm25` thuần** → bài học `max > replace` KHÔNG chuyển sang chọn
đoạn. Gộp bằng chứng thì hedge tốt, chọn bằng chứng thì phải dứt khoát.

#### 24 gold hụt chia ba nhóm — chỉ MỘT nhóm là của chọn đoạn

| nhóm | số | bản chất |
|---|---|---|
| chọn đoạn CỨU ĐƯỢC | 9 | K=20 bỏ sót đoạn tốt hơn ← mục tiêu |
| M>20 | 8 | CE hạng 21-78, chưa từng chấm sâu. Đòn M, đắt, bỏ |
| **BẤT LỰC** | **7** | CE chấm ~0,00 trên **toàn bộ** văn bản |

Nhóm BẤT LỰC đã soi dữ liệu thô: **không có bug**, văn bản sạch. Nguyên nhân là lệch ngữ
nghĩa nhiệm vụ — gold là **văn bản nền tảng**, câu hỏi hỏi **tình huống áp dụng cụ thể**.
Ví dụ qid `159444` hỏi lệ phí cấp đổi giấy phép lữ hành, gold là Quyết định **liệt kê danh
mục thủ tục**, đoạn khớp nhất chỉ là dòng mục lục, không hề có số tiền. CE chấm 0 là **đúng
về ngữ nghĩa**, chỉ sai theo luật chơi. Không hàm chọn đoạn nào cứu được nhóm này.

Hạng BM25 của 7 cái đó: **[3, 5, 9, 18, 42, 44, 48]** — ba cái trong BM25 top-10. BM25
*thấy* chúng, reranker vứt đi. Đó đúng là địa hạt của `blend_bm25_first`, quét được offline
0 giờ GPU. **Nhưng chỉ đụng nếu tìm ra CƠ CHẾ, đừng vặn `n`** (n đã chốt bằng public LB).

#### VIỆC NGAY: chạy `chunk_v2_run.ipynb` (~3-5h)

**Upload: đúng MỘT file — `deep_chunk.py` bản mới, ĐÈ bản cũ.**
`scores_dev300_deep_M20_K20.json` đã upload từ lượt oracle. Tầng 1 KHÔNG chạy lại
(bóc `ce_deep` cũ khỏi file đó là ra tầng 1 sạch — ce_deep cũ băm kiểu khác, giữ lại là
trộn hai hệ đo).

**Việc thật của lượt này là LOẠI TRỪ TỤT ĐIỂM, không phải đo mức tăng.** +1,67 dưới ngưỡng
2,0 nên dev300 mù. Nhưng gộp đoạn đổi đầu vào CE cho **cả 20 văn bản** → rủi ro pha loãng
làm tệ đi, và tụt ≥2 điểm thì dev300 bắt thừa sức. Mức tăng thật đo bằng public LB.

| `max n=2` ra | quyết định |
|---|---|
| ≥ 0.9083 | không tụt → chạy đề thi (~9h, đã có `scores_public.json`), nộp, để LB đo |
| 0.89 – 0.9083 | pha loãng → chạy lại `MERGE_CHARS = 0`, giữ mỗi BM25 (riêng nó +1,34) |
| < 0.89 | tụt thật → quay về `deep_chunk.py` cũ |

**Hai biến một lượt là CỐ Ý.** Quy tắc 3 tồn tại để quy công khi thắng — oracle đã quy công
sẵn trên CPU (BM25 +1,34, gộp thêm +0,33). Tách hai lượt 5h để đo hai hiệu ứng đều dưới
ngưỡng phân giải là đốt quota vô ích.

**Ước thời gian: ~4h** (khoảng 3–5,5h). Tầng 2 còn ~100.000–115.000 đoạn (thấp hơn
118.000 của bản cũ vì gộp đoạn đẩy nhiều văn bản xuống dưới 20 đoạn → `pick_chunks`
trả hết). Khoảng rộng vì **chưa ai đo cross-encoder với đoạn ~1.460 ký tự** (~430 token,
gấp 2,2 lần cũ). Nhịp giữ 12,9 đoạn/s → 2,4h; rơi nửa → 4,7h.
→ **Biết chắc sau ~10 phút**: Bước 4 in ETA + nhịp thật ở câu 25. Vượt 6h thì dừng, đặt
`K_CHUNK = 12` (gộp rồi thì K=12 phủ 17.500 ký tự, vẫn hơn K=20 bản cũ phủ 13.000).

**Bẫy `skip`:** `skip` chỉ đúng khi hai lượt cùng `MERGE_CHARS` và cùng `pick_chunks`.
Đổi cách băm rồi thì `ce_deep` cũ không so được với mới — phải chấm lại từ hạng 0.
Đã ghi cảnh báo vào docstring `deepen_one`.

**RAM: `_cache` nặng hơn bản cũ.** Trước lưu `(text, set token)`, giờ lưu
`(parts, tfs Counter, lens, idf, avglen)` — thêm ~30-50%. Mốc cũ: 200 văn bản = 148MB
→ phủ hết corpus 8532 văn bản ≈ 6,3GB, giờ ≈ **9GB**. Kaggle GPU ~29GB nên dev300
(~3.000 văn bản, ~3GB) thoải mái, nhưng **để ý khi chạy đề thi**. Nếu OOM: bỏ `tfs`
sau khi dựng xong `idf` là không được (BM25 cần tf lúc chấm) — thay vào đó xoá
`_cache` mỗi 200 câu, đổi lại mất phần dùng lại giữa các câu.

#### HAI BUG ĐÃ BẮT KHI VIẾT `deep_chunk.py` MỚI — cả hai IM LẶNG, không crash

Kiểm chéo bắt được (dựng lại đúng 0.9217/0.9250 của nguyên mẫu offline mới phát hiện):

1. **`df.update(t)` với `t` là `Counter` CỘNG TẦN SUẤT, không đếm số đoạn chứa term.**
   `Counter.update(Counter)` cộng giá trị; muốn document frequency phải `df.update(t.keys())`.
   Hậu quả: `c > n` nên `log(1+(n-c+.5)/(c+.5))` ra âm → idf đảo dấu → **+1,34 tụt về +0,00**.
   Code vẫn chạy, vẫn ra số hợp lý, chỉ là số sai.
2. **`sorted(key=score, reverse=True)` lật ngược thứ tự khi HOÀ điểm.** Rất nhiều đoạn ăn
   đúng 0 (không term nào của câu hỏi xuất hiện), `reverse=True` lấy đoạn CUỐI văn bản
   thay vì đoạn đầu. Phải viết `key=lambda i: -score(i)`.

→ **Bài học chung: mọi hàm mới phải tái lập được một số ĐÃ BIẾT trước khi lên GPU.**
Ở đây số đã biết là 0.9217/0.9250 từ nguyên mẫu quét trên `oracle_chunks_dev300.json`.
Không có mốc đó thì hai bug này đi thẳng lên Kaggle, đốt 4h và ra kết luận "BM25 không ăn".

Self-test trong `__main__` của `deep_chunk.py` giờ có ca bắt bug 1: đoạn nhiều "thuế"
phải THUA đoạn chứa "trước bạ" (term hiếm). Bản `count` cũ không phân biệt được ca này.

### (lịch sử) kế hoạch lượt oracle — đã thực hiện xong

**Mục đích thật không phải go/no-go mà là sinh TÀI SẢN**: chấm CE trên **TOÀN BỘ** đoạn của
24 văn bản gold hụt trên dev300 (chưa vào top-5 nhưng còn trong top-100), **lưu điểm TỪNG
ĐOẠN** — không phải chỉ max. ~24 × 200 ≈ 5.000 đoạn ≈ 7 phút.

Ra `Ketqua_E/oracle_chunks_dev300.json`. Có file đó thì **mọi hàm chọn đoạn sau này đo
được trên CPU**, không cần GPU: hỏi "top-20 của hàm f có chứa đoạn thắng không?".
Đúng khuôn đã làm deepchunk rẻ (ghi `ce_deep` riêng → 3 biến thể × 4 giá trị n từ 1 lượt).

Nó trả lời hai câu cùng lúc:

| oracle | nghĩa |
|---|---|
| ≥6 câu được kéo lên top-5 khi cho chọn đoạn hoàn hảo | chọn đoạn ĐÚNG là nút thắt → embedding là đòn đúng, biết luôn trần |
| ≤2 câu | **không phải vấn đề chọn đoạn** → đừng đốt 2,5h, quay hướng khác |

So sánh với hạng 5 hiện tại lấy thẳng từ `scores_dev300_deep_M20_K20.json` — điểm đối thủ
đã có sẵn, không chấm lại. **Đây là chặn TRÊN chặt**: không hàm chọn đoạn nào vượt được
"chọn hoàn hảo trong 125". Đọc hơi lạc quan vì cải tiến toàn cục thì đối thủ cũng được nâng
theo — đúng rủi ro "phồng điểm mọi văn bản" ở mục `max` vs `replace`.

**Bước CPU: ĐÃ CHẠY 17/08, kết quả dưới đây. Đừng chạy lại.**

Chạy thẳng trên máy, hai chốt kiểm khớp tuyệt đối (`base n=2 = 0.8883`, `max n=2 = 0.9083`):

| nhóm | số gold | ghi chú |
|---|---|---|
| gold tổng dev300 | 314 | |
| hụt top-5 | 31 | |
| ├─ còn trong top-100 | **24** | E chạm tới được |
| └─ ngoài top-100 | 7 | D chịu |
| trong 24: có **>20 đoạn** | **22** | chọn đoạn CÓ THỂ cứu |
| trong 24: **≤20 đoạn** | 2 | `pick_chunks` trả về HẾT rồi → không hướng nào cứu |
| trong 22: CE hạng 1-20 (đã chấm sâu) | **15** | ← MỤC TIÊU CHÍNH, trần +4,78 điểm |

**Suy ra thứ tự BM25 từ khoá `bm25` trong file scores là ĐÚNG** — dựng lại ra đúng
0.8883/0.9083. → **không cần `bm25_top100_dev300.json` (100MB)** cho mọi việc dev300
từ giờ. Bớt được một file to khỏi mọi lượt Kaggle.

Kích thước đoạn đo thật trên 24 văn bản này: `chunks_of` cho **652 ký tự/đoạn, 212
đoạn/văn bản** (cao hơn trung vị corpus 125 vì tập hụt lệch về văn bản dài) → **K=20 chỉ
phủ 9%**. Gộp lên 1.800 ký tự → 95 đoạn/văn bản → **phủ 21%**, gấp 2,3 lần.

### `oracle_run.ipynb` — ĐÃ VIẾT XONG, ĐÃ DRY-RUN, nằm ở gốc repo

**Upload lên dataset `project-ir` — đúng MỘT file mới:**
`Ketqua_E/scores_dev300_deep_M20_K20.json` (2,2MB). Mọi thứ khác đã có sẵn.

Upload `oracle_run.ipynb` dưới dạng **notebook**, gắn dataset `project-ir`, **GPU T4**,
**Internet On**, **Save & Run All (Commit)**.

Chi phí đã đếm: **5.090 + 2.272 = 7.362 đoạn ≈ 9,5 phút.**

Chốt kiểm khi chạy:

1. Bước 1 phải in `base 0.8883 OK` và `max 0.9083 OK`, rồi `24 gold hụt`
2. Bước 2 phải in `TỔNG 7,362 đoạn` — lệch nhiều là sai thiết lập, dừng
3. Bước 4 lưu `oracle_chunks_dev300.json` **trước** khi phân tích (quy tắc 2)

Bước 6 là chỗ chỉ thẳng cần sửa gì: đoạn điểm cao nhất đang bị tiêu chí từ trùng xếp
hạng bao nhiêu. Hạng >20 = K=20 chưa từng thấy nó → embedding có cửa. Hạng ≤20 = nó đã
được chấm mà vẫn thua → đổi tiêu chí chọn vô ích.

### ỨNG VIÊN THỨ HAI — KÍCH THƯỚC ĐOẠN. Rẻ hơn embedding, cùng lượt oracle đo được luôn

Mới có quyền đụng từ 17/08. Hiện đoạn của E trung bình **686 ký tự**, trung vị **125
đoạn/văn bản** → K=20 chỉ phủ **16%** văn bản. Nhân đôi kích thước đoạn → ~62 đoạn →
K=20 phủ **32%**, gấp đôi xác suất đoạn đúng lọt vào.

**Và nhiều khả năng gần như MIỄN PHÍ.** Log 15/08 đã ghi: đoạn của E ngắn hơn của D
(686 vs 1.387 ký tự) mà **không chạy nhanh hơn** — "chi phí bị chi phối bởi padding +
overhead, không phải độ dài thật". Tức nới đoạn lên ~1.400 ký tự tốn xấp xỉ như cũ.

**Rủi ro thật: pha loãng.** Đoạn 1.400 ký tự chứa câu trả lời + 1.000 ký tự luật lệ không
liên quan có thể bị cross-encoder chấm thấp hơn đoạn 686 ký tự toàn nội dung đúng. Không
hiển nhiên thắng — là thí nghiệm thật, không phải chỉnh config.

→ File `oracle_chunks_dev300.json` đo được **cả hai** ứng viên trên CPU nếu lượt oracle
băm ở **nhiều kích thước** rồi chấm hết. Cân nhắc nới lượt oracle lên ~15.000 đoạn
(~20 phút) để có 2-3 kích thước đoạn — vẫn rẻ, và tránh phải chạy lại GPU lần nữa.

### Ngưỡng giao D — dưới ngưỡng là HẠ TRẦN, không phải cải tiến

D chuyển sang recall 100 → 50 → 25. Cắt thuần tuý làm E **mất** điểm (đã đo, dev300):
top-50 → 0.9000 (−0,83) · top-25 → 0.8833 (−2,50, xoá sạch phần thưởng deepchunk).
**Trần chỉ có thể TỤT khi cắt, không bao giờ tăng.**

| D giao | phải vượt | hiện tại |
|---|---|---|
| top-25 | **recall@25 > 0.9283** | 0.9283 |
| top-50 | **recall@50 > 0.9683** | 0.9683 |
| top-100 | recall@100 > 0.9783 | 0.9783 ← đòn ĐIỂM duy nhất của D |

**Ba điều bắt buộc nói với D:**

1. **`M` chọn theo hạng CE, KHÔNG phải hạng BM25** (`deep_chunk.py:110`). D sắp lại thứ
   tự BM25 **không** đổi tập văn bản được chấm sâu. Nó chỉ ăn vào hai chỗ: trần recall,
   và 2 suất ép của `blend_bm25_first(n_bm25=2)`.
2. **Đổi bộ candidate = mọi scores đã lưu thành rác.** `scores_public.json` +
   `scores_public_deep_M20_K20.json` khoá theo đúng 100 văn bản hiện tại — **~9h GPU đã
   nằm trong ngân hàng**. Đổi candidate là chạy lại CẢ HAI tầng trên đề thi.
   → D phải đo trên dev300 và vượt ngưỡng **TRƯỚC**, đừng giao file rồi tính sau.
3. **Chi phí D tiết kiệm chỉ có giá trị nếu E TIÊU nó.** D cắt xuống 25 mà E vẫn chạy
   K=20 như cũ = −2,50 điểm và không được gì. Trước khi D bắt tay, E chốt trước tiêu vào
   đâu — ví dụ "2,5h dôi ra nâng K từ 20 lên 45 trên cả 20 văn bản".

## TRẠNG THÁI 17/08 (tối) — lịch sử

**XONG CẢ HAI LƯỢT. Có bài nộp M=20 đầy đủ — đúng cấu hình 0.9083 của dev300. ĐÃ NỘP → 0.8840.**
Chia tầng 2 làm hai lượt đã chạy trót lọt: A ~3h20m, B xong trong 5h40 quota còn lại.

`Ketqua_E/` giờ có đủ, không còn lỗ hổng nào:

| file | nội dung |
|---|---|
| `scores_public.json` | tầng 1, 1000×100 |
| `scores_public_deep_M10_K20.json` | + `ce_deep` hạng 1-10 |
| `scores_public_deep_M20_K20.json` | + `ce_deep` hạng 1-20 ← **đầy đủ** |
| `submission_B_M20.zip` / `.json` | **bài nên nộp** |
| `submission_A_M10.zip` / `.json` | bài M=10, dự phòng / để đo |
| `pred_public_tang1.json` | 4 bộ n=0..3 của tầng 1 |

**Năm kiểm tra offline, pass hết:**

1. Đúng **20/20** văn bản/câu có `ce_deep`, cả 1000 câu
2. `ce` tầng 1 không bị ghi đè: **0** cặp lệch
3. **`ce_deep` hạng 1-10 của lượt A giữ nguyên tuyệt đối: 0 lệch** → `skip=10` khâu đúng
   giữa hai phiên GPU riêng biệt. Cơ chế tách lượt đã được chứng minh trên đề thi thật
4. Dựng lại submission từ scores: **1000/1000** khớp
5. 5 id/câu, không trùng, đủ 5 cho cả 1000 câu

Lệch: **B vs A = 222 câu** · **B vs bản 0.8573 = 500 câu** (một nửa bài).
92% id trong top-5 (4.614/5.000) là văn bản đã chấm sâu. n=2 vẫn là đỉnh.

**Dự báo public: ~0,875-0,88** (dev300 = 0.9083, độ lệch dev→public −3,1).

### NỘP GÌ — nộp CẢ HAI, B trước

1. **`submission_B_M20.zip`** — bài chốt.
2. **`submission_A_M10.zip`** — không phải để dự phòng, mà để **đo**. dev300 nói
   M=20 hơn M=10 đúng +0,66 với bootstrap 77,8%, tức không tin được một mình.
   Hai bài lệch nhau 222 câu, và public có 1000 câu (1 câu = 0,1 điểm) nên LB **phân giải
   được** cái mà dev300 không phân giải nổi. Đây là cách duy nhất biết +0,66 là thật,
   giá 0 giờ GPU. Ghi cả hai vào bảng E7.

## TRẠNG THÁI 17/08 (chiều) — lịch sử

**LƯỢT A XONG. Có bài nộp M=10 hợp lệ, đã kiểm offline, CHƯA NỘP.**
Bỏ tầng 1 nhờ `scores_public.json` → lượt A về đích thoải mái trong 12h.

Tài sản mới trên máy, `Ketqua_E/`:

| file | nội dung |
|---|---|
| `scores_public_deep_M10_K20.json` | 1000 câu, **đúng 10 văn bản/câu có `ce_deep`**. Đầu vào của lượt B |
| `submission_A_M10.zip` / `.json` | bài nộp `max` + n=2, M=10 |
| `scores_public.json` | tầng 1, giữ nguyên |
| `pred_public_tang1.json` | 4 bộ n=0..3 của tầng 1 |

**Bốn kiểm tra offline, pass hết:**

1. `question_id` khớp khít 1000 câu đề thi
2. **`ce` tầng 1 không bị ghi đè: 0/100.000 cặp (câu, văn bản) lệch** → lượt B chồng lên
   file này an toàn, `skip=10` sẽ sắp hạng đúng như lượt A
3. Dựng lại submission từ scores ra **1000/1000** khớp — cả chuỗi rank_by → blend → build đúng
4. 5 id/câu, không trùng, đủ 5 cho cả 1000 câu

**Lệch 376/1000 câu so với bản 0.8573.** 88% id trong top-5 (4.391/5.000) là văn bản đã
được chấm sâu. n=2 vẫn là đỉnh (n=0 lệch 613 câu, n=1 lệch 517, n=3 lệch 678 so với bản nộp).

**Dự báo public: ~0,870-0,875.** Căn cứ: dev300 M=10 = 0.9017, độ lệch dev→public lâu nay
−3,1 điểm (0.8883 → 0.8573).

### "OPTIMIZE CÁCH GỘP ĐIỂM" — ĐÃ QUÉT HẾT 17/08, KHÔNG CÒN GÌ. Đừng làm lại.

Quét toàn bộ họ hàm gộp `ce` với `ce_deep` trên dev300 (0 giây GPU, dùng
`scores_dev300_deep_M20_K20.json`):

| `α·ce + (1−α)·ce_deep` | n=1 | n=2 | n=3 |
|---|---|---|---|
| α=0,0 (= replace) | 0.9017 | 0.9033 | 0.8950 |
| α=0,2 | 0.9017 | 0.9067 | 0.8950 |
| **α=0,3** | 0.8983 | **0.9100** | 0.8950 |
| α=0,5 | 0.8983 | 0.9050 | 0.8933 |
| α=1,0 (= base) | 0.8633 | 0.8883 | 0.8683 |
| **`max` (đang dùng)** | 0.9017 | **0.9083** | 0.9033 |

`max(ce, ce_deep − δ)` với δ = 0,02…0,3: **mọi δ > 0 đều tệ hơn hoặc bằng**.

**Kết luận: `max` đã ở đỉnh của họ hàm này.** α=0,3 hơn 0,17 điểm = **nửa câu** — nhiễu,
và nó được chọn trên CHÍNH 300 câu đang đo, đúng cái bẫy đã dính ngày 11/08 (chốt n=1 trên
dev150 với bootstrap 96,9% rồi dev300 lật ngược). Không đổi.

**Vì sao không quét được gì hơn: chỉ lưu `ce_deep` = MAX của K đoạn.** Mọi hàm gộp thú vị
hơn (trung bình 3 đoạn cao nhất, đếm số đoạn vượt ngưỡng, phân tán điểm giữa các đoạn)
cần **điểm từng đoạn** — không có thì không thí nghiệm offline được.
→ **Lượt GPU tới, sửa `deepen_one` lưu cả list điểm đoạn, không chỉ max.** Thêm ~386k số
float, gần như miễn phí, và nó mở ra cả một họ hàm gộp mới quét được trên CPU.

### CẮT ỨNG VIÊN 100 → 50 → 25: đo rồi, đây là đòn CHI PHÍ, không phải đòn ĐIỂM

Đo trên dev300 với chính `scores_dev300_deep_M20_K20.json` (17/08, CPU vài giây):

| trần recall@k của candidate D | @5 | @10 | @25 | @50 | @100 |
|---|---|---|---|---|---|
| dev300 | 0.7533 | 0.8533 | **0.9283** | **0.9683** | 0.9783 |

Hạng BM25 của 5 id cuối cùng được chọn (1.500 id, cấu hình chốt M=20/max/n=2):

| hạng BM25 | số id được chọn | trong đó là gold |
|---|---|---|
| 1-10 | 1.043 (69,5%) | 256 |
| 11-25 | 212 (14,1%) | 19 |
| 26-50 | 123 (8,2%) | **5** |
| 51-100 | 122 (8,1%) | **3** |

| nếu D chỉ giao | recall@5 | mất |
|---|---|---|
| top-100 (hiện tại) | **0.9083** | — |
| top-50 | 0.9000 | −0,83 |
| top-25 | 0.8833 | **−2,50** |

**Cắt xuống 25 xoá sạch toàn bộ phần thưởng deepchunk (+2,00).** Cắt xuống 50 mất 0,83
điểm, đổi lấy tầng 1 nhanh gấp đôi (~1,7h GPU trên đề thi) — chỉ đáng nếu đang thiếu quota,
và hiện không có chỗ nào để tái đầu tư 1,7h đó cho hơn 0,83 điểm.

**Trần chỉ có thể TỤT khi cắt, không bao giờ tăng.** Nên "D cắt xuống 50/25" tự nó không
phải cải tiến. Chỉ khác nếu D **cải tiến truy hồi**: recall@25 phải vượt 0.9283 hoặc
recall@50 phải vượt 0.9683 (đo trên cùng dev300) thì mới là được thêm.

### LƯỢT B — notebook đã đặt sẵn, nhưng KIỂM QUOTA TRƯỚC KHI BẤM

`finalAnswer_run.ipynb` giờ là cấu hình B: `SKIP, M_DOC, K_CHUNK = 10, 20, 20`,
`SCORES_TANG1 = {INPUT_DIR}/scores_public_deep_M10_K20.json`.
**Upload `Ketqua_E/scores_public_deep_M10_K20.json` lên dataset trước** — thiếu nó là
tầng 1 chạy lại, mất 3,4h vô ích rồi vẫn không đủ giờ.

**Số học quota: B cần ~4,8h, mà sau lượt A chỉ còn ~4,2h.** Thiếu ~40 phút.
Chạy mà bị cắt ở trần tuần thì mất trắng y như 15/08 — Kaggle cắt cứng, `try/except`
không đỡ. → Xem số quota thật trên Kaggle: **≥5h thì chạy, dưới thì đợi reset tuần**.
Hạn thi 15/09, đợi một tuần không mất gì.

Chốt kiểm phút đầu: log phải in `đọc lại điểm cũ ... 1000 câu`, rồi
`tầng 2 sẽ chấm ~193.000 đoạn`. Ra 386.000 là `SKIP` chưa ăn — dừng ngay.

→ **NỘP `Ketqua_E/submission_A_M10.zip`.** Có LB rồi mới quyết lượt B (xem mục dưới:
+0,66 dưới ngưỡng quy tắc 4, và quota tuần chỉ còn ~4h).

## TRẠNG THÁI 17/08 (sáng) — lịch sử

**Lượt 15/08 bị Kaggle CẮT ở 43.200,9s = đúng 12h** (trần cứng của commit). Tầng 1 xong
và đã cứu được `scores_public.json`; tầng 2 chạy dở, mất trắng. **Chưa nộp**, public LB
vẫn 0.8573.

### Thu được từ tầng 1 — nhiều hơn vẻ ngoài

1. `Ketqua_E/scores_public.json` (6,8MB, 1000 câu × 100 văn bản, không câu rỗng).
   **Lỗ hổng tồn từ 12/08 đã bịt.**
2. Đã kiểm chéo: dựng lại n=2 từ file này ra **trùng khít 1000/1000 câu, đúng cả thứ tự**
   với `submission_n2.zip` — bản đã ăn 0.8573. Tầng 1 lượt này = tầng 1 lượt 12/08.
3. `Ketqua_E/pred_public_tang1.json` — sẵn 4 bộ top-5 cho n=0..3, sinh trên CPU vài giây.
   Lệch so với n=2: n=0 → 639 câu, n=1 → 536, n=3 → 683.
4. Có thể nộp lại bản 0.8573 bất cứ lúc nào **không cần GPU**.

### ĐÃ GIẢI THÍCH ĐƯỢC — thiếu 22 phút, và nguyên nhân là NHỊP GPU chứ không phải tầng 2

Đọc log lượt 15/08:

| mốc | số |
|---|---|
| setup + tầng 1 | 14.687s = **4,08h** (tầng 1 ~3,37h + ~43 phút pip/đọc 335MB/load model/đếm) |
| nhịp tầng 2 | **0,4975 phút/câu**, tuyến tính tăm tắp từ câu 100 đến câu 900 |
| tầng 2 trọn gói | 497,5 phút = **8,29h** |
| **tổng cần** | **12,37h** — trần 12h → **thiếu đúng 22 phút, đã xong 97%** |

**Thông lượng thật: 12,9 đoạn/s, cho CẢ hai tầng.** Tầng 2 không hề chậm bất thường —
157.008 đoạn tầng 1 ở nhịp đó ra đúng 3,37h, khớp log. Đoạn của E còn ngắn hơn của D
(686 vs 1.387 ký tự) và điều đó không giúp gì: chi phí bị chi phối bởi padding + overhead,
không phải độ dài thật.

**Cái sai là MỐC NEO.** "dev300 = 47.240 đoạn ≈ 30 phút" tương đương **26 đoạn/s** —
gấp đôi nhịp thật của lượt 15/08. Hai lượt chạy trên phần cứng khác nhau (Kaggle cấp
T4 hay P100 tuỳ lúc), chênh ~2x. → **Quy tắc 6 sửa lại: ước bằng 13 đoạn/s, không quy
đổi từ lượt dev.** Muốn chắc thì lấy nhịp từ chính dòng tiến độ của lượt đang chạy.

### Ba phương án, tính ở nhịp 12,9 đoạn/s (setup ~40 phút, KHÔNG chạy lại tầng 1)

| | số đoạn | chạy | + setup | dư so với trần 12h |
|---|---|---|---|---|
| lượt A, hạng 1-10 | 193.243 | 4,1h | **4,8h** | 7,2h |
| lượt B, hạng 11-20 | 193.243 | 4,1h | **4,8h** | 7,2h |
| gộp M=20 một lượt | 386.486 | 8,3h | **9,0h** | 3,0h |

Gộp một lượt **vừa đủ** nhưng dư chỉ 33% — GPU lần sau chậm hơn 33% là chết y hệt lần này,
và mất trắng vì Kaggle cancel là cắt cứng, `try/except` không đỡ được.
Tách hai lượt tốn thêm đúng ~40 phút setup mà dư tới 2,5x, và **lượt A đã nộp được**.
→ **Tách. Chạy A trước, nộp, rồi tính B.**

**Quota còn 9h (17/08) → chỉ đủ MỘT lượt.** A = 4,8h, B = 4,8h, tổng 9,6h > 9h.
Gộp M=20 (9,0h) là đốt sạch quota với dư 0 — cấm. Chạy A, giữ 4,2h làm đệm.

**B chưa chắc đáng chạy tuần sau.** M=10 → M=20 chỉ +0,66 trên dev300, bootstrap 77,8% —
**dưới ngưỡng ≥2,0 của quy tắc 4**, chính CLAUDE.md đã ghi "một mình thì không đủ tin".
Đổi 4,8h GPU lấy chừng đó là đắt. Quyết định sau khi có public LB của lượt A:
nếu A ăn đúng dự báo thì 4,8h tuần sau nên dồn cho hướng bi-encoder chọn đoạn
(nhắm 16 câu đã chấm sâu vẫn kẹt), upside lớn hơn nhiều.

### VIỆC TIẾP THEO — tách tầng 2 làm HAI lượt bằng `skip`. Notebook đã sửa xong.

`finalAnswer_run.ipynb` giờ đọc lại điểm cũ thay vì chạy lại tầng 1:

| | `SKIP, M_DOC` | `SCORES_TANG1` | ra file |
|---|---|---|---|
| lượt A | `0, 10` | `scores_public.json` | `scores_public_deep_M10_K20.json` |
| lượt B | `10, 20` | `scores_public_deep_M10_K20.json` | `scores_public_deep_M20_K20.json` |

Mỗi lượt tự chạy nốt phần chốt top-5 + đóng gói, nên **lượt A đã nộp được** (M=10 trên
dev300 = 0.9017, +1,34 so với baseline). Lượt B chỉ để lấy nốt +0,66.

**Upload lên dataset `project-ir` trước lượt A:** `Ketqua_E/scores_public.json`.
Trước lượt B: `scores_public_deep_M10_K20.json`. Không có file đó thì tầng 1 chạy lại,
mất thêm ~1h45m.

Bỏ tầng 1 rồi thì cả hai lượt còn dư ~10h/12h cho riêng tầng 2 — gấp đôi chỗ so với
lượt 15/08 đã có.

## TRẠNG THÁI 15/08 — lịch sử

**DEEPCHUNK ĂN, ĐÃ CHẠM TRẦN. Mốc dev300 mới: 0.9083** (`max` + `n_bm25=2`,
**M=20**, K=20). Baseline cũ 0.8883 → **Δ +2,00 điểm**, cứu 8 hỏng 2,
bootstrap `P(> base) = 96,6%`. Chưa nộp, public LB vẫn đang là 0.8573.

| biến thể | n=0 | n=1 | n=2 | n=3 |
|---|---|---|---|---|
| base | 0.8650 | 0.8633 | 0.8883 | 0.8683 |
| max, M=10 | 0.8850 | 0.8950 | 0.9017 | 0.8933 |
| **max, M=20** | 0.8983 | 0.9017 | **0.9083** ← chốt | 0.9033 |
| replace, M=20 | 0.8883 | 0.9017 | 0.9033 | 0.8950 |

`base` cột `n=2` ra **đúng 0.8883** ở CẢ HAI lượt → chốt tự kiểm khớp hai lần.

**M=10 → M=20 chỉ đáng +0,66** (cứu 3 hỏng 1, bootstrap 77,8% — một mình thì
không đủ tin). Thứ cứu nó là nhất quán: M=20 thắng M=10 ở **cả bốn** giá trị n.

### ĐỪNG NỚI M NỮA — đã chạm trần, bản chất phần hụt đã đổi

| Nhóm (sau M=20) | Gold | % |
|---|---|---|
| Đã vào top-5 | 283 | 90,1% |
| **Đã chấm sâu 20 đoạn mà VẪN kẹt (hạng 6-20)** | **16** | **5,1%** |
| Hạng 21+, chưa chấm sâu | 8 | 2,5% |
| Ngoài top-100 BM25 (D chịu) | 7 | 2,2% |

Nhóm lớn nhất giờ là 16 câu **đã được xem 20 đoạn mà vẫn thua** — thêm đoạn không
cứu được, đây là vấn đề CHẤM chứ không còn là vấn đề LƯỢNG. Nhóm chưa chấm sâu chỉ
còn 8 câu → M=30 gần như vô nghĩa.

→ Đây đúng là địa hạt **bi-encoder D4**: chọn đúng 20 đoạn trong 125, thay vì chọn
nhiều hơn. Hoặc E tự dựng bằng model embedding tiếng Việt có sẵn, không cần D.

**Vì sao tin được dù +1,34 < ngưỡng +2,0 của quy tắc 4:** ngưỡng đó viết cho so sánh
KHÔNG cặp. Đây là so sánh cặp — cùng câu, cùng model, chỉ đổi bằng chứng đưa vào.
Số liệu cặp: **cứu 5 câu, hỏng 1 câu**, bootstrap `P(max > base) = 93,2%`.
Mạnh hơn nữa: **`max` thắng `base` ở CẢ BỐN giá trị n** (+2,00 / +3,17 / +1,34 / +2,50),
trung bình +2,25. Nhiễu thì hướng phải ngẫu nhiên, không thể cùng dấu bốn lần.
Và cơ chế đã được dự đoán TRƯỚC khi đo, không phải bới ra sau.

`max` thắng `replace` ở mọi n → giữ chunk của D bên cạnh chunk của mình là đúng.
Rủi ro "chấm nhiều đoạn làm phồng điểm mọi văn bản" có thật nhưng không lấn át.

### Còn hụt ở đâu — đã đo, quyết định bước sau dựa vào đây

| Nhóm | Số gold | % |
|---|---|---|
| Đã vào top-5 | 281 | 89,5% |
| **Hạng 11+, CHƯA chấm sâu (ngoài M=10)** | **16** | **5,1%** |
| Hạng 6-10, đã chấm sâu — 20 đoạn vẫn chưa đủ | 10 | 3,2% |
| Ngoài top-100 BM25 (D chịu) | 7 | 2,2% |

**Nhóm lớn nhất còn lại là 16 gold nằm ngoài M=10, chưa từng được chấm sâu.**
→ Bước sau là **tăng M**, không phải tăng K. Tăng M còn sửa được một bất đối xứng
của thiết kế hiện tại: văn bản hạng 11-20 đang phải đấu với văn bản hạng 1-10 đã
được cộng điểm từ 20 đoạn, trong khi bản thân chúng chỉ có 3 đoạn của D.

### Lượt sau RẺ HƠN NHIỀU nhờ đã có scores — đây là phần thưởng của quy tắc 2

Đã có `Ketqua_E/scores_dev300_AITeamVN_Vietnamese_Reranker.json` (tầng 1, model gốc)
và `Ketqua_E/scores_dev300_deep_M10_K20.json`. Lượt tới **không cần chạy lại tầng 1**
(47.240 đoạn ≈ 30 phút) — chỉ chấm sâu hạng 11-20 rồi gộp offline với ce_deep cũ.
Ước **~40 phút** thay vì ~1h50m.

### VIỆC TIẾP THEO — chạy `finalAnswer_run.ipynb` rồi NỘP (~6h)

Notebook ĐÃ chỉnh sẵn, không phải sửa gì: `M_DOC, K_CHUNK = 20, 20`, `VARIANT="max"`,
`N_BM25=2`, candidate trỏ đúng `bm25_top100_public.json` của D (trước 15/08 vẫn trỏ
`candidates_public_FB.json` — file đã xoá khỏi repo, chạy là chết ngay cell đọc).

**Upload lên dataset `project-ir` trước:** `deep_chunk.py` (bản có `skip`).

Chi phí đã đếm trên CPU: 157.008 (tầng 1) + 384.400 (tầng 2) = **541.408 đoạn
= 3,45x → ~6h**. Đừng để `M_DOC=20` mà tưởng vẫn 3,9h như M=10.

Luồng: tầng 1 → **lưu `scores_public.json` NGAY** → tầng 2 → `DC.rank_by(..,"max")`
→ blend n=2 → 7 chốt chặn cũ (guard chống nộp nhầm dev, validate zip, soi lại file).

### Tiền kiểm trên CPU 15/08 — đã xong, đừng làm lại

- Dựng lại **cả bảng 3 biến thể × 4 giá trị n** từ `scores_dev300_deep_M20_K20.json`
  + candidate + gold, chạy bằng đúng `DC.rank_by` + `blend_bm25_first` mà notebook gọi.
  Khớp từng số với `deepchunk_M20_eval.json`; `base n=2` ra **0.8883** lần thứ ba.
  Mọi câu đều có đúng 20/20 văn bản mang khoá `ce_deep` → tầng 2 không sót câu nào.
- `CTX_DIR = f"{INPUT_DIR}/selected-contexts"` **đúng**, không dính bẫy `Input/`:
  hai lượt deepchunk trên Kaggle đã chạy được với chính chuỗi này.
- Đã thêm `assert os.path.isdir(CTX_DIR)` vào cell Config của `finalAnswer_run.ipynb`
  (copy từ `deepchunk_run.ipynb`). Trước đó CTX_DIR chỉ bị chạm SAU ~3h tầng 1 → trỏ sai
  là mất 3h. **Nhớ upload lại notebook bản mới**, đừng chạy bản cũ trên Kaggle.
- **Chạy bằng commit (Save & Run All) thì commit LỖI = Kaggle không xuất bản output.**
  Tức "tầng 2 hỏng vẫn còn scores_public.json" của quy tắc 2 KHÔNG đúng ở chế độ commit —
  file lưu ở giờ thứ 3 mất theo. Đã bọc tầng 2 trong `try/except`: hỏng thì `scores` giữ
  nguyên tầng 1, `VARIANTS["max"]` tự rơi về `ce`, notebook chạy hết và ra submission
  baseline 0.8573 thay vì mất cả lượt GPU. Bắt được `MemoryError`; **không** bắt được
  OOM-killer giết cả tiến trình — chống cái đó bằng mục RAM dưới đây.
- Đã bỏ `top_chunks` của `test_candidates` ngay sau tầng 1 (phần sau chỉ cần `doc_id`) —
  bớt ~2GB đúng lúc tầng 2 phình cache.
- **RAM là chỗ chật nhất của lượt này.** `_cache` trong `deep_chunk` giữ text + set token
  của mọi đoạn đã băm; `count_deep_chunks` làm nóng cache trước khi chấm. Đo thật trên máy:
  200 văn bản = 148MB → phủ hết corpus 8532 văn bản ≈ **6,3GB**, cộng ~2GB cho
  `test_candidates` (file 335MB). Kaggle GPU ~29GB nên qua được. Nếu vẫn OOM: sau tầng 1
  dựng `bm25_rank` xong thì bỏ text trong `test_candidates` — bớt ~2GB, sửa một dòng.

**Tải về trước khi đóng phiên:** `scores_public.json` VÀ
`scores_public_deep_M20_K20.json`. Có hai file này thì mọi thí nghiệm chốt top-5
trên đề thi làm được trên CPU — lỗ hổng tồn từ 12/08 mới bịt được một nửa.

Dự báo public: dev 0.9083, độ lệch dev→public lâu nay ~−3 điểm → ước **~0,875-0,88**
(đang là 0.8573).

### SAU KHI NỘP — hướng duy nhất còn lại

16 gold đã chấm sâu 20 đoạn mà vẫn kẹt = chọn nhầm 20 đoạn trong 125. Hai cách:

1. **D4 của D** — bi-encoder mức đoạn, thay tiêu chí sắp xếp trong `pick_chunks`
2. **E tự dựng** — model embedding tiếng Việt có sẵn trên HF, không cần huấn luyện,
   nhúng đoạn rẻ hơn cross-encoder nhiều và cache được. Không phải chờ ai

Cách cắm vào: đổi đúng dòng `sorted(parts, key=lambda p: -len(qs & p[1]))` trong
`deep_chunk.pick_chunks`. Cấu trúc hai tầng và cách gộp `max` giữ nguyên.
Nhớ bài học `max > replace`: **cộng** đoạn của bi-encoder vào, đừng thay thế.

## TRẠNG THÁI 13/08 — lịch sử

**Public LB tốt nhất vẫn là 0.8573** (AITeamVN **gốc** + `blend_bm25_first(n_bm25=2)`).

**FINE-TUNE ĐÃ CHẠY XONG VÀ THUA. Đừng chạy lại cấu hình đó.**
Kết quả trong `results (1).zip` → đã bóc ra `Ketqua_E/ft_eval.json` +
`Ketqua_E/scores_dev300_ft.json`. Chi tiết ở mục "E3 — fine-tune" bên dưới.

**Việc tiếp theo: KHÔNG chạy `finalAnswer_run.ipynb` với `ft_model`.** Giữ model gốc.

### VIỆC NGÀY MAI — chạy `deepchunk_run.ipynb` (~1h15m–1h45m)

E5: chấm sâu vùng ranh giới. Đã viết xong, đã dry-run trên CPU với model giả.
Nhắm vào 17 câu có gold ở hạng 6-10 — trần +5,4, kỳ vọng +2..+3.

**Upload lên Kaggle dataset `locdovan211/project-ir` — chỉ MỘT file mới:**

| File | Vì sao |
|---|---|
| `deep_chunk.py` | **MỚI**, chưa từng upload. Không có nó là notebook chết ở cell import |
| `finetune_rerank.py` | không cần cho lượt này, nhưng đồng bộ luôn bản `bs=8` + AMP |

Mọi thứ khác notebook cần đã có sẵn trong dataset (lượt fine-tune 12/08 chạy được):
`make_candidates_fallback.py`, `rerank.py`, `rerank_from_d.py`, `metrics.py`,
`dev_300_locked.json`, `bm25_top100_dev300.json`, `selected-contexts/`.

**Upload `deepchunk_run.ipynb` dưới dạng NOTEBOOK** (không phải dataset), gắn dataset
`project-ir`, bật **GPU T4**, **Internet: On**, rồi **Save & Run All (Commit)**.

**Ba chốt kiểm khi chạy:**

1. Cell 2 in `!ls /kaggle/input` — thấy `project-ir` mới chạy tiếp
2. Bước 4 in `tổng ~106.000 đoạn = 2.25x` — lệch nhiều là `M_DOC`/`K_CHUNK` sai
3. Bước 5: hàng `base` cột `n=2` **phải ra 0.8883**. Lệch quá 0,002 là thiết lập sai,
   dừng lại, đừng đọc mấy dòng dưới

**Tải về trước khi đóng phiên (quy tắc 2):** toàn bộ `outputs/`, đặc biệt
`scores_dev300_AITeamVN_Vietnamese_Reranker.json` — file scores model gốc đang thiếu.
Notebook lưu nó **ngay sau tầng 1**, nên kể cả tầng 2 hỏng thì lượt GPU vẫn lãi.

**Đọc kết quả:** cần **≥ +2,0 điểm** mới tính là thắng (quy tắc 4 — dưới ngưỡng đó
dev300 không phân giải được). Thắng → chạy `finalAnswer_run.ipynb` với cấu hình đó.
Thua → kết luận chọn đoạn theo từ trùng đã hết đường, giục D làm **bi-encoder D4**.

Notebook lưu `ce_deep` vào khoá riêng, **không ghi đè `ce`** → một lượt GPU cho ba
biến thể (`base` / `max` / `replace`) × 4 giá trị `n_bm25`, quét lại được trên CPU.

**Ngân sách GPU thực tế (đếm lại 12/08, con số "~3h"/"~5h" cũ là ước tính thừa):**

| Việc | Ước tính | Căn cứ |
|---|---|---|
| `finetune_run.ipynb` trọn gói | **1h20m – 1h45m** | dựng dữ liệu 449s (đo thật) + train 3.819 step bs=8 AMP + chấm dev300 ~30 phút |
| `finalAnswer_run.ipynb` | **1h40m – 2h** | 157.008 chunk đề thi = 3,32x của dev300 (47.240 chunk) |

Tức hai lượt gộp lại ~3,5h — **vừa một phiên quota 5h**, không cần chia hai tuần.
Nếu OOM lại thì chỉ mất ~9 phút chứ không mất cả buổi: lần trước chết đúng 21 giây sau
khi vào Bước 2. Qua được `step 100` (in kèm VRAM đỉnh) là an toàn tới hết.

**Bẫy `hard negative: 0/24,000` — ĐÃ KIỂM Ở MÁY 12/08, sạch.** Chạy lại `build_pairs`
trên CPU với đúng file trên máy: `24,000/24,000`, 0 câu thiếu candidate, 0 doc_id ngoài
corpus, key qid của candidate khớp key của `train.json` (đều là chuỗi). Nghĩa là logic
đã đúng — **rủi ro còn lại chỉ là đường dẫn trên Kaggle**. Nếu Bước 1 vẫn in `0/24,000`
thì lỗi ở `HARD_NEG` trỏ sai chỗ (Kaggle thường giữ nguyên cấu trúc thư mục khi upload:
file nằm dưới `Input/` sẽ ra `/kaggle/input/project-ir/Input/…`). Xem output của
`!ls /kaggle/input` ở cell 2 trước khi chạy tiếp — đừng phí 3 tiếng.

**File hard negative đã kiểm:** 7000 câu, 20 candidate/câu, recall@20 = 0.9202,
mọi doc_id thuộc corpus, 6000 câu huấn luyện đều có ≥16 negative.

### E3 — FINE-TUNE: ĐÃ CHẠY XONG, THUA. ĐÓNG HƯỚNG NÀY.

Cấu hình: AITeamVN gốc, hard negative thật (`hard_negative: true`), `n_neg=4`,
`epochs=1`, `lr=2e-5`, `max_length=512`. Đo trên dev300, cùng candidate của D.

| n_bm25 | fine-tune | gốc | Δ |
|---|---|---|---|
| 0 | 0.8700 | 0.8650 | +0,50 |
| 1 | 0.8800 | 0.8633 | +1,67 |
| **2** ← cấu hình chốt | **0.8833** | **0.8883** | **−0,50** |
| 3 | 0.8750 | 0.8683 | +0,67 |

**Đọc cho đúng: đây KHÔNG phải "fine-tune làm hỏng model".** −0,50 điểm trên 300 câu
= **1,5 câu**. Bootstrap: `P(ft n=2 > mốc 0.8883) = 41,6%` — đúng nghĩa tung đồng xu.
Kết luận đúng là **fine-tune 1 epoch không đổi được gì**, không phải nó có hại.

Điều đáng chú ý hơn con số tổng: **fine-tune làm phẳng đường cong `n_bm25`.**
Model tự xếp hạng khá hơn chút (n=0: +0,50) nhưng phần thưởng từ blend BM25 teo lại,
nên đỉnh n=2 tụt xuống. Bốn giá trị n giờ nằm trong khoảng 0.870–0.883 thay vì
0.863–0.888. Nghĩa là nó học được một ít, nhưng học chồng lên đúng thứ mà blend
đang bù sẵn — không cộng thêm thông tin mới.

**Đừng thử lại bằng cách vặn siêu tham số** (thêm epoch, đổi lr, tăng n_neg). Mỗi lượt
~1,5h GPU để đổi lấy dao động ±1,5 câu. Trần candidate còn cách 9 điểm (0.8883 vs
0.9783) — chỗ đó không nằm ở reranker.

Tài sản để lại, dùng được offline: `Ketqua_E/scores_dev300_ft.json` (điểm CE của
ft_model trên toàn bộ dev300). Đây là **file scores đầu tiên có trên máy** — mọi thí
nghiệm về cách chốt top-5 với model này làm được trên CPU, không cần GPU.
Model `ft_model` (2,3GB) nằm trong `results (1).zip`, không giải nén vào repo.

### Lần chạy fine-tune 12/08 — một lượt HỎNG vì OOM, ĐÃ SỬA

Log: dữ liệu **đúng hết** — `hard negative: 24,000/24,000`, dựng 30.550 cặp trong 449s,
`[ok] không câu dev nào lọt`. Chết ở Bước 2 sau 21 giây:

```
OutOfMemoryError: CUDA out of memory. Tried to allocate 128.00 MiB.
GPU 0 has a total capacity of 14.56 GiB of which 90.81 MiB is free.
```

Nguyên nhân: `bs=16`, fp32, XLM-R large 568M tham số. Chỉ riêng weight (2,3GB) +
gradient (2,3GB) + hai moment của AdamW (4,5GB) đã **9,1GB**, còn ~5,4GB cho
activation của 16×512 token qua 24 lớp → không đủ. **Không liên quan dữ liệu.**

Đã sửa (12/08 tối):

- `bs` 16 → **8**, cả trong `finetune_run.ipynb` lẫn default của `finetune_rerank.py`
- Thêm **AMP fp16** (`autocast` + `GradScaler`) vào `train_model` — giảm nửa activation
  và nhanh ~3x nhờ tensor core T4. Có `scaler.unscale_` trước `clip_grad_norm_`
- Thêm `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` ở cell cài đặt
- In VRAM đỉnh mỗi 100 step → biết ngay còn dư bao nhiêu

**Giữ `max_length=512`.** Cắt xuống 256 tiết kiệm bộ nhớ nhưng ViRanker trần 256 token
chỉ được ~0.76 — đừng đánh đổi.

Lưu ý: notebook ghi "bật T4 x2" nhưng `train_model` chỉ dùng `device="cuda"`, tức
**một GPU**. Con thứ hai nằm không. Không đáng thêm DataParallel.

**D chỉ còn MỘT việc: bi-encoder (D4).** Đã bỏ yêu cầu dev1000 (chạy nó tốn đúng
bằng nộp một bài thật) và bỏ yêu cầu tăng top_chunks (xem mục dưới).
`bm25_top100_public.json` D đã giao (335MB, 12/08 11:01) — mục "đang chờ D" số 1 XONG.

## VIỆC NGÀY 12/08 — đã xong, giữ để tham chiếu

**Trước khi chạy (ở máy, 2 phút):**
- ✅ Đổi tên `bm25_top100_dev.json` → `bm25_top100_dev300.json` — XONG
- Xoá rác: ✅ `fb.log`, `Claude_Output/`, `candidates_public_FB.rar` đã sạch.
  Còn `__pycache__/` (3 file .pyc, Claude không xoá được — tự xoá tay)
- Upload lên Kaggle dataset: `bm25_top100_dev300.json`, `dev_300_locked.json`,
  `dev_1000_locked.json`, `finetune_rerank.py`, `make_candidates_fallback.py`,
  `finalAnswer_run.ipynb`, `run_pipeline_kaggle.ipynb`, và `Input/selected-contexts/` +
  `Input/train.json` (cần cho fine-tune, nhiều khả năng chưa có)

**1. NỘP BÀI — ✅ XONG 12/08 10:58. Public LB = 0.8440 (precision 0.1812), hạng 29.**

**2. MỐC MỚI TRÊN DEV300 — ~30 phút**
`run_pipeline_kaggle.ipynb` → Run All. Config đã trỏ dev300.
Tải về, đổi tên thành `scores_dev300_AITeamVN.json`, gửi Claude.
Mục đích: kiểm `N_BM25=1` (chọn trên dev150, dev300 gần như độc lập — chỉ 44 câu chung).

**3. THỬ FINE-TUNE — ~1h**
`!python /kaggle/input/project-ir/finetune_rerank.py --out /kaggle/working/ft_model`
Negative ngẫu nhiên, chưa cần hard negative. Chỉ để biết fine-tune có ăn không.
Đo lại bằng `RERANKER_MODEL = "/kaggle/working/ft_model"`. Nhớ tải model về máy.

Tổng ~4h GPU. Quota 30h/tuần. Đừng chạy song song.

## Quy ước làm việc

- **Câu đầu tiên luôn là kết luận** — ngắn, rõ, trực tiếp. Chi tiết để sau.
- Trả lời ngắn gọn, bỏ phần giải thích thừa.
- **CLAUDE.md thì cập nhật liên tục, không cần hỏi.** `BaoCao_E.md` thì **CHỈ sửa khi
  Khim yêu cầu** — đừng tự động đồng bộ báo cáo theo CLAUDE.md.

> ⚠️ **`BaoCao_E.md` đang CŨ, dừng ở 12/08.** Vẫn ghi cấu hình chốt là `n_bm25=1`,
> dev150 = 0.8900, LB = 0.8440. Thiếu toàn bộ: chuyển sang dev300, chốt `n=2`,
> LB 0.8573, deepchunk (0.9083 / LB 0.8840), lượt A M=10 (LB 0.8713), lượt oracle,
> BM25 chọn đoạn. Khi Khim yêu cầu cập nhật báo cáo thì lấy số từ CLAUDE.md — **đừng
> tự làm trước.**

### BẮT BUỘC: gọi skill `ponytail` mức `full` TRƯỚC MỌI VIỆC CODE

Không phải "nhớ tinh thần ponytail" — là **gọi skill thật**, trước khi gõ dòng code
đầu tiên. Áp dụng cho: viết file mới, sửa file cũ, viết notebook, refactor, review
code, chọn thư viện. Không áp dụng cho: phân tích số liệu, đọc log, viết CLAUDE.md.

Vì sao gắt: repo này đã có sẵn `chunks_of`, `tok`, `read_passage`, `blend_bm25_first`,
`evaluate`, `score_all_from_d`, `load_reranker`. Gần như mọi việc mới đều là ghép lại
đồ có sẵn chứ không phải viết mới. Ponytail tồn tại để chặn phản xạ viết lại từ đầu.

**Đã bỏ sót một lần:** 13/08 viết `deep_chunk.py` mà không gọi skill. Code ra vẫn gọn
(dùng lại `chunks_of`/`tok`, không thêm dependency), nhưng đó là may chứ không phải
quy trình. Lần sau gọi skill trước.

### NHẮC MỞ CHAT MỚI khi ngữ cảnh phồng

Trong một phiên, mọi thứ đã đọc đều được gửi lại ở **mỗi lượt** — đọc 3 notebook
với 2 file log rồi thì câu hỏi thứ 30 vẫn đang kéo theo toàn bộ chỗ đó.

**Claude tự nhắc Khim mở chat mới khi chạm bất kỳ dấu hiệu nào:**

1. Đã đọc **≥ 5 file lớn** (notebook, log, `.py` dài, dump JSON) trong phiên
2. Hội thoại vượt **~25 lượt**
3. **Đổi việc** — xong deepchunk chuyển sang D4, xong phân tích chuyển sang viết báo cáo
4. Vừa đóng một hạng mục và đã ghi kết luận vào CLAUDE.md

Cách nhắc: một câu ở cuối câu trả lời, không phải cả đoạn. Kiểu *"Phiên này đã đọc
nhiều file rồi — ghi xong mục này thì mở chat mới cho việc sau."* Nhắc xong thì
thôi, đừng lặp lại mỗi lượt.

**Điều kiện bắt buộc trước khi nhắc: đã cập nhật CLAUDE.md.** Mở chat mới mà file
chưa ghi thì phiên sau bắt đầu từ số không. Nhắc mở chat mới **luôn đi kèm** việc
chốt lại những gì cần ghi.

Muốn xem con số thật thay vì ước đoán thì gọi skill `explain-usage`.

### QUOTA GPU — 6 quy tắc, NHƯNG TRỌNG SỐ ĐÃ ĐỔI TỪ 17/08

**Chỗ chật nhất không còn là quota tuần.** ⚠️ **SỬA 23/08: quota là 60h/tuần, không phải
30h** → 4 tuần tới 15/09 ≈ **240h**, trong khi cả kế hoạch chỉ ăn ~78h. Quota **dư gấp ba**.
Cái chật thật là **trần cứng 12h/lượt commit** (đã giết lượt 15/08), **số lượt nộp/ngày**,
và **độ phân giải của dev300** — không thứ nào trong ba cái đó mua được bằng giờ máy.

→ Đánh giá đóng góp của D bằng câu *"cái này nhét thêm được gì vào MỘT lượt 12h?"*,
đừng bằng *"cái này tiết kiệm bao nhiêu giờ trong tuần?"* — hai câu giờ cho đáp án khác nhau.

→ Quy tắc **1** (làm hết CPU trước) và **2** (luôn cứu `scores_*.json`) **quan trọng hơn
bao giờ hết**: mất một lượt giờ là mất một tuần lịch, không phải mất vài giờ quota.
Còn "đừng chạy vì tốn quota" thì nới được — chạy dev300 để đo là rẻ, cứ chạy.

Sáu quy tắc vẫn đúng về nguyên tắc. Áp dụng không ngoại lệ:

1. **Làm hết phần CPU trước khi chạm GPU.** Kiểm đường dẫn, kiểm key qid, dry-run
   `build_pairs`, đếm số chunk để ước chi phí — tất cả chạy được ở máy trong vài giây.
   Ngày 12/08 chạy `build_pairs` trên CPU đã loại trừ được bẫy `0/24,000` trước khi
   đốt 3 tiếng. Ngày 13/08 đếm chunk trên CPU đã bác bỏ phương án chấm sâu toàn bộ
   (13x chi phí) trước khi ai kịp đề xuất nó lên Kaggle.

2. **Mỗi lượt GPU BẮT BUỘC sinh `scores_*.json` và BẮT BUỘC tải về trước khi đóng
   phiên.** Không có scores = mọi thí nghiệm về cách chốt top-5 phải chạy lại GPU.
   Đây là lỗi đắt nhất đã mắc: `scores_public.json` và `scores_dev300_AITeamVN.json`
   đều mất, nên quy tắc "mỗi model một lượt GPU" không thực thi được.

3. **Mỗi lượt chỉ đổi MỘT biến.** Chồng nhiều thay đổi rồi đo một lần thì thắng cũng
   không biết công của ai, thua cũng không biết lỗi tại đâu — và phải chạy lại để tách.

4. **Chỉ chạy thí nghiệm kỳ vọng đổi ≥2 điểm.** dev300 có 300 câu, 1,05 gold/câu →
   một câu đáng 0,33 điểm, nhiễu ~±1,5 câu. Hiệu ứng dưới ~1,5 điểm **không đo được
   về mặt nguyên tắc**, dù chạy bao nhiêu lượt. Đây là lý do fine-tune "thua 0,50"
   không có nghĩa gì, và là lý do đừng vặn siêu tham số.

5. **Gộp việc vào một phiên.** `finetune_run.ipynb` gộp train + chấm dev là đúng mẫu:
   một lần khởi động, một lần tải model. Đừng tách thành hai notebook chạy hai lượt.

7. **Trước MỌI lượt chạy trên 1 giờ, hỏi thành viên kia có đang làm việc đó không.**
   Chi phí 2 phút, cứu được cả lượt GPU. **19/08 mất 4 giờ** dựng bi-encoder trong khi
   D đã làm xong khâu đó. Log ghi việc này đã chuyển sang E từ 17/08 nên tưởng là của
   mình — nhưng một câu hỏi đã đủ để biết. Quy tắc 1-6 đều là kỹ thuật; đây là quy tắc
   phối hợp, và nó vừa đắt ngang bất kỳ quy tắc nào ở trên.

6. **Ước chi phí bằng SỐ CHUNK trước khi chạy**, đừng ước bằng cảm giác. Mốc đã đo:
   dev300 = 47.240 chunk ≈ 30 phút · đề thi = 157.008 chunk ≈ 1h45m. Quy đổi tuyến
   tính. Con số "~3h"/"~5h" ghi trong notebook cũ là ước tính thừa, đã sửa.

## Vai trò

Khim = **thành viên E** — Xếp hạng & Chốt top-5. Sở hữu `recall@5`.
D lo hạ tầng + sinh ứng viên (top-100), E tiêu thụ và chốt submission.

## Bẫy đã dính, đừng dính lại

### ĐƯỜNG DẪN KAGGLE — hai chỗ, tuỳ cách gắn dataset (19/08)

```python
INPUT_DIR = "/kaggle/input/project-ir"                        # hoặc:
INPUT_DIR = "/kaggle/input/datasets/locdovan211/project-ir"

CTX = f"{INPUT_DIR}/selected-contexts"                        # hoặc LỒNG HAI LẦN:
CTX = f"{INPUT_DIR}/selected-contexts/selected-contexts"      # khi Kaggle tự giải nén zip
```

**Đừng hardcode. Tự dò** — mọi notebook mới dùng khuôn này:

```python
INPUT_DIR = next(p for p in ("/kaggle/input/project-ir",
                             "/kaggle/input/datasets/locdovan211/project-ir")
                 if os.path.isdir(p))
CTX = next(p for p in (f"{INPUT_DIR}/selected-contexts/selected-contexts",
                       f"{INPUT_DIR}/selected-contexts")
           if os.path.isdir(p) and any(f.startswith("context_") for f in os.listdir(p)))
```

Kiểm bằng **có file `context_*.json` bên trong**, không phải bằng `isdir` — thư mục ngoài
vẫn tồn tại khi bị lồng, nên `isdir` một mình sẽ trỏ vào chỗ rỗng. Thứ tự phải để bản
LỒNG trước.

### GUARD KIỂM BẰNG TEXT TỰ BẮN VÀO CHÂN (19/08)

`finetune_v2_run` chết ở cell 2 với `AssertionError: best_chunk vẫn đếm từ trùng` — mà
file trên dataset **đúng bản mới**. Nguyên nhân: docstring bản mới **trích dẫn code cũ**
để giải thích, nên `inspect.getsource` chứa đúng chuỗi mà assert đi tìm.

→ **Kiểm bằng CHỮ KÝ HÀM hoặc hành vi, đừng kiểm bằng chuỗi trong source.**

```python
sig = list(inspect.signature(FT.best_chunk).parameters)
assert sig == ["question", "ctx_dir", "doc_id"]     # docstring không giả được cái này
```

Cùng họ với bài học `print` số cứng: **thứ trông giống phép kiểm mà không kiểm đúng đối
tượng thì tệ hơn không có, vì nó tạo cảm giác an toàn.** Ở đây nó còn giết oan một lượt.

`dev_150_locked.json` (150 câu, cắt từ `train.json`) **không phải** đề thi.
Đề thi là `Input/public-official.json` — **1000 câu**, `answer: null`, giao với train = 0.

Bài nộp 09/08 bị BTC từ chối vì nộp dự đoán của 150 câu dev. Định dạng đúng hoàn toàn,
chỉ sai bộ `question_id`. `build_submission(expected_qids=...)` vẫn pass vì kỳ vọng
truyền vào cũng là dev — guard không tự biết bạn nộp nhầm đề.

→ Mọi file dev phải giữ hậu tố `_dev` trong tên.

## Dữ liệu

| File | Nội dung |
|---|---|
| `Input/public-official.json` | 1000 câu đề thi, `answer: null` |
| `Input/train.json` | 7000 câu có nhãn |
| `Input/selected-contexts/` | corpus 8532 document, `context_<id>.json` → `{link, passage, id}` |
| `dev_1000_locked.json` | **toà án cuối** cho bake-off. Bao trùm dev300 + dev150 |
| `dev_300_locked.json` | thử nhanh hàng ngày. Lồng trong dev1000 |
| `dev_150_locked.json` | **ĐÃ KHAI TỬ** — 256/300 câu giờ nằm trong tập huấn luyện |
| `bm25_top100_dev300.json` | candidate của D cho dev300, 100MB |
| `bm25_top100_dev1000.json` | **CHƯA CÓ** — D còn thiếu 700 câu. Không cần nữa, xem mục n_bm25 |
| `bm25_top100_public.json` | ✅ **ĐÃ CÓ** (335MB, D giao 12/08) — candidate đề thi, recall@100 = 0.9875 |
| `bm25_ids_train_FALLBACK.json` | 5,6MB — hard negative cho fine-tune, 7000 câu × 20 doc_id |
| `candidates_public_FB.json` | candidate **dự phòng** của E — **ĐÃ XOÁ khỏi repo**, D đã giao bản thật |

### Cấu trúc dev (D giao 12/08, đã kiểm)

```
train.json 7000
 ├─ dev1000 ⊃ dev300 ,  dev1000 ⊃ dev150      (đã xác minh bằng code)
 └─ 6000 câu còn lại → fine-tune E3
```

Giao với đề thi = 0. Loại `dev_1000_locked.json` khỏi huấn luyện là loại hết mọi tập dev.

`recall@100` của D: dev300 = 0.9783 · dev150 = 0.9700. BM25 thô recall@5: dev300 = 0.7533.

Corpus dùng chung cho dev và đề thi → chunker + index BM25 của D dùng lại được,
chỉ cần chạy lại bước truy vấn.

## BASELINE — mốc so sánh cho mọi cải tiến sau này

Mọi thí nghiệm mới **phải báo cáo dạng Δ so với hai con số này**, không báo cáo số trần trụi:

> **dev300 = 0.8883** · **public LB = 0.8573**
> (AITeamVN/Vietnamese_Reranker gốc + `blend_bm25_first(n_bm25=2)`, candidate của D)

### Chuỗi tăng tiến trên dev300 (300 câu, 1,05 gold/câu)

| Bước | recall@5 | Δ so với bước trước |
|---|---|---|
| BM25 thô của D (top-100, giữ nguyên thứ tự) | 0.7533 | — |
| + rerank AITeamVN, `n_bm25=0` | 0.8650 | **+11,17** |
| + `blend_bm25_first(n_bm25=2)` | **0.8883** | +2,33 |
| *trần: `recall@100` của candidate* | *0.9783* | *còn 9,00 dư địa* |

### Chuỗi tăng tiến trên đề thi (public LB, 1000 câu)

| Bước | recall@5 | Δ |
|---|---|---|
| BM25 thô | **CHƯA ĐO** — `answer: null`, chỉ đo được bằng một lượt nộp. Không đáng |
| rerank AITeamVN, `n_bm25=0` | 0.8350 | — |
| + `blend_bm25_first(n_bm25=2)` | 0.8573 | +2,23 |
| + deepchunk M=20, K=20, `max` | 0.8840 | +2,67 |
| + BM25 chọn đoạn + gộp 1800 | 0.8871 | +0,31 |
| + **RỔ FUSION** (M=10, n=3) | 0.9063 | **+1,92** |
| + **M=20, n=2 ← BÀI CHỐT 23/08** | **0.9109** | **+0,46** |
| *trần: `recall@50` của rổ fusion* | *0.9817 (đo trên dev300)* | *còn ~7 dư địa* |

**Đọc bảng:** reranker đem về +11 điểm · cách chốt top-5 +2 · đọc sâu +2,7 · chọn đoạn
+0,3 · **rổ tốt hơn +2,4**. Hai đòn lớn nhất đều là **đổi thứ nạp vào**, không phải tinh
chỉnh cái đang có. Dư địa còn lại vẫn nằm gần trọn ở **thứ tự trong rổ** — 13 câu dev300
có gold trong rổ mà trượt top-5 = 4,33 điểm, toàn bộ thuộc khâu xếp hạng.

### Tái lập baseline (CPU, vài giây)

Hai con số BM25 kiểm lại được bất cứ lúc nào, không cần GPU:

```python
dev  = json.load(open('dev_300_locked.json'))
cand = json.load(open('bm25_top100_dev300.json'))
gold = {q: {str(x) for x in v['answer']} for q, v in dev.items()}
rank = lambda q: [str(c['doc_id']) for c in cand[q] if c.get('doc_id')]
rec  = lambda k: sum(len(gold[q] & set(rank(q)[:k])) / len(gold[q]) for q in gold) / len(gold)
# rec(5) -> 0.7533   ·   rec(100) -> 0.9783   (đã xác minh 12/08)
```

Số của reranker thì KHÔNG tái lập được offline vì **`scores_dev300_AITeamVN.json` và
`scores_public.json` đều không có trên máy** — xem mục cảnh báo bên dưới.

## Số đã đo (dev_150_locked — ĐÃ KHAI TỬ, chỉ để tham chiếu lịch sử)

`recall@100 = 0.9700` — trần của D. Chỉ **3 câu** gold nằm ngoài top-100 hoàn toàn.
BM25 thuần recall@5 = 0.7578.

### Bảng ablation reranker — ĐÃ CHỐT, đừng thử lại

| Model | tham số | n_bm25=0 | n_bm25=1 | Ghi chú |
|---|---|---|---|---|
| **AITeamVN/Vietnamese_Reranker** | 567.755.777 | 0.8567 | **0.8900** | ← chốt |
| BAAI/bge-reranker-v2-m3 | 567.755.777 | 0.8467 | 0.8600 | model nền của AITeamVN |
| Qwen/Qwen3-Reranker-0.6B | 595.776.512 | 0.7711 | 0.7844 | cơ chế yes/no, không hợp |
| namdp-ptit/ViRanker | — | ~0.76 | — | PhoBERT, trần 256 token |
| BM25 thuần | 0 | 0.7578 | — | |

**Quy luật rút ra: fine-tune tiếng Việt quan trọng hơn kích thước.** AITeamVN chính là
bge-v2-m3 fine-tune tiếng Việt — cùng kiến trúc, cùng số tham số, hơn 3 điểm.
Ngân sách 3B là đường cụt: không có bằng chứng model to hơn thì tốt hơn.

Không thử: PhoRanker (PhoBERT trần 256 token + cần tách từ), Prism-2B (cùng cơ chế
yes/no với Qwen3), các MiniLM (quá nhỏ / tiếng Anh).

### E7 — độ lệch dev ↔ public LB (cập nhật mỗi lần nộp)

| Ngày | Cấu hình | dev | public LB |
|---|---|---|---|
| 12/08 | candidate **dự phòng**, n=1 | 0.8900 (dev150) | 0.8440 |
| 12/08 | candidate của D, n=1 | — | 0.8532 |
| 12/08 | candidate của D, **n=2** | 0.8883 (dev300) | 0.8573 |
| 12/08 | candidate của D, n=0 | 0.8650 (dev300) | 0.8350 |
| 12/08 | candidate của D, n=3 | 0.8683 (dev300) | 0.8424 |
| 17/08 | **deepchunk M=20/K=20, max, n=2** (`submission_B_M20`) | 0.9083 (dev300) | **0.8840** ← tốt nhất |
| 17/08 | deepchunk M=10/K=20, max, n=2 (`submission_A_M10`) | 0.9017 (dev300) | 0.8713 |
| 19/08 | **BM25 chọn đoạn + gộp 1800, M=20/K=20, n=2** (`submission_v2_M20_n2`) | 0.9183 (dev300) | **0.8871** ← tốt nhất |
| 19/08 | cùng cấu hình, n=0 (`submission_v2_M20_n0`) | 0.9217 (dev300) | 0.8851 |
| 19/08 | ⛔ *phép đo hỏng* — Gemini CHÉP lại `submission_B_M20`; bài lai = 725 câu B_M20 + 275 câu v2 | — | 0.8853 |
| 19/08 | ✅ Gemini xếp hạng SẠCH (rổ 50 BM25, 50 câu dev300) — hoà, 2-2 | 0.9000 *(mình 0.9100 cùng 50 câu)* | không nộp |
| 22/08 | rổ FUSION M=10, n=0 | 0.9283 (dev300) | 0.8775 |
| 22/08 | rổ FUSION M=10, n=1 | **0.9350** ← đỉnh dev | 0.8943 |
| 22/08 | rổ FUSION M=10, n=2 | 0.9283 | 0.9033 |
| 22/08 | rổ FUSION M=10, **n=3** | 0.9233 | **0.9063** ← đỉnh M=10 |
| 22/08 | rổ FUSION M=10, n=4 | — | 0.8962 |
| 23/08 | rổ FUSION M=20, n=1 | — | 0.9059 |
| 23/08 | **rổ FUSION M=20, n=2** (`submission_fusion_M20_n2`) | — | **0.9109** ← BÀI CHỐT |
| 23/08 | rổ FUSION M=20, n=3 | — | 0.9101 |
| 23/08 | rổ FUSION M=20, n=4 | — | 0.8980 |

**⛔ HẰNG SỐ −3,0 ĐÃ CHẾT. Đừng dùng nữa.** Ba điểm cũ (−3,10 · −3,04 · −2,43) trông ổn
định chỉ vì chúng đều đo ở `n=2`. Lượt fusion quét trọn dải `n` và lộ ra độ lệch **thay đổi
theo `n`**: −5,08 (n=0) · −4,07 (n=1) · −2,50 (n=2). Không có hằng số quy đổi nào cả.
→ dev300 dự báo được **thứ tự** khi hiệu ứng lớn, **không** dự báo được mức tuyệt đối, và
**không** đo được `n` (sai 3/3 lần). Với `n`: sinh cả dải offline, để public LB quyết.

### n_bm25 — ⚠️ KHÔNG CÓ GIÁ TRỊ CỐ ĐỊNH. Phải quét lại mỗi khi đổi rổ hoặc đổi M.

Lịch sử trên rổ BM25 (12/08):

```
            n=0      n=1      n=2      n=3
dev300    0.8650   0.8633   0.8883   0.8683
public    0.8350   0.8532   0.8573   0.8424
```

Lúc đó cả hai đỉnh ở n=2 và hình dạng khớp → kết luận "dev300 dự đoán đúng thứ tự".
**Kết luận đó chỉ đúng cho rổ đó.** Trên rổ fusion, dev300 báo đỉnh n=1 còn public nói
n=3 (M=10) rồi n=2 (M=20) — sai cả về vị trí lẫn hình dạng.

**Đỉnh `n` đã dời BA lần, và mỗi lần đều có cơ chế:**

| Cấu hình | Đỉnh `n` | Cơ chế |
|---|---|---|
| Rổ BM25, M=20 | n=2 | mốc |
| Rổ fusion, M=10 | **n=3** | rổ xếp hạng tốt hơn (recall@5 thô 0.8733 vs 0.7533) → nhường thêm suất thì đáng |
| Rổ fusion, M=20 | **n=2** | reranker khoẻ hơn → `blend` hết chỗ dụng võ, đỉnh dời ngược xuống |

→ **Quy tắc: đổi rổ hoặc đổi M thì BẮT BUỘC quét lại `n`.** Rẻ — sinh cả dải offline từ
file scores, 0 giờ GPU, chỉ tốn lượt nộp.

**Bốn điểm số này chỉ tốn MỘT lượt GPU.** `n_bm25` chỉ ảnh hưởng bước chọn 5 từ 100,
không ảnh hưởng điểm. Có `scores_public.json` là sinh lại submission trên CPU vài giây.
→ Quy tắc: mỗi **model** một lượt GPU; mọi thí nghiệm về cách chốt đều làm offline.

> ✅ **ĐÃ BỊT 15/08 — `Ketqua_E/scores_public.json` đã có trên máy** (6,8MB, tầng 1 của
> lượt 15/08, 1000 câu × 100 văn bản, không câu rỗng). Dựng lại n=2 từ file này ra
> **trùng khít 1000/1000 câu, đúng cả thứ tự**, với `submission_n2.zip` — tức bản đã
> ăn 0.8573 trên public LB. Tầng 1 lượt này = tầng 1 lượt 12/08, không cần bàn thêm.
> Bốn bộ dự đoán n=0..3 sinh sẵn ở `Ketqua_E/pred_public_tang1.json`.
> Số câu lệch so với n=2: n=0 → 639 câu, n=1 → 536, n=3 → 683. `n_bm25` đổi hơn nửa bài.
> Còn thiếu: `scores_dev300_AITeamVN.json` của model gốc trên dev (không gấp) và
> `scores_public_deep_M20_K20.json` (đang chờ tầng 2).

> ⚠️ **BỐI CẢNH CŨ (12/08-13/08).** Kiểm 13/08: `scores_public.json` và
> `scores_dev300_AITeamVN.json` (model **gốc**) vẫn không có trên máy. Chỉ còn 3 zip
> submission sinh sẵn (n0/n2/n3 — thiếu n1, chính là bản 0.8532).
> Đã có `Ketqua_E/scores_dev300_ft.json` nhưng đó là điểm của **ft_model**, không
> thay thế được scores của model gốc.
> → **Lượt GPU tới, việc đầu tiên sau khi chạy xong là tải `scores_*.json` về máy.**
> n0 và n2 khác nhau tới **894/1000 câu** — `n_bm25` không phải tinh chỉnh nhỏ.

Lệch -4,6 điểm, nhưng -3,75 trong đó giải thích được bằng trần candidate thấp hơn
(0.95 so với 0.9875 của D). Phần lệch thật của dev chỉ ~1 điểm → **dev đáng tin**.

Dự báo khi có candidate của D: **~0.87-0.88**, chỉ đổi một dòng đường dẫn.

### Chiến lược chốt top-5 — ĐÃ SỬA 12/08, dùng n_bm25=2

| tập | n=0 | n=1 | n=2 | n=3 |
|---|---|---|---|---|
| dev150 (150 câu) | 0.8567 | **0.8900** | 0.8733 | 0.8500 |
| dev300 (300 câu) | 0.8650 | 0.8633 | **0.8883** | 0.8683 |
| **GỘP 406 câu** | 0.8608 | 0.8719 | **0.8842** | 0.8621 |

Bootstrap trên 406 câu: `n=2 > n=0` **97,5%** · `n=2 > n=1` 90,9% · `n=1 > n=0` 88,4%.

**Bài học đắt giá:** ngày 11/08 tôi chốt `n=1` với bootstrap 96,9% — nhưng đó là
bootstrap trên CHÍNH 150 câu đã dùng để chọn. Nó đo độ ổn định trong mẫu, KHÔNG đo
được mẫu có đại diện không. dev300 gần như độc lập (chỉ 44 câu chung) đã lật ngược.
→ Chọn siêu tham số trên tập nào thì phải xác nhận trên tập khác.

Fusion theo điểm, RRF, ensemble 2 model: đều THUA, đã thử, đừng làm lại.

### Tăng top_chunks 3 → 5 — ĐÃ RÚT LẠI, đừng đề xuất lại

Ban đầu tôi ước +1,5-2,5 điểm. Sai. Đo kỹ 20 ca hỏng có gold chạm trần 3 chunk:
**văn bản gốc có trung vị 189 đoạn, tối đa 744** (Bộ luật Tố tụng Hình sự).

Vấn đề không phải "3 hay 5" mà là "chọn 3 trong 189". Nâng lên 5 gần như vô ích.
Chi tiết 20 ca: `Ketqua_E/cases_topchunk3_dev300.json`.

→ Giải pháp đúng là **bi-encoder mức đoạn (D4)**, chọn theo nghĩa thay vì từ trùng.
BM25 mức document vẫn tốt (`recall@100 = 0.9783`), không cần thay.

### Ghép tên văn bản (task #1 của D) — ĐÃ THỬ VÀ THUA

D gửi trường `name` dạng slug URL **không dấu** (`Luat-Pha-san-2014-238641`).
Ghép vào đầu chunk làm **tệ đi 2,0 điểm** (98,8% bootstrap, n=0). Câu hỏi có dấu,
slug không dấu → nhiễu nhiều hơn tín hiệu. `USE_DOC_NAME = False`.

Hàm `with_doc_name` vẫn giữ trong `rerank_from_d.py`.

**ĐÃ HẾT CHỜ D — 13/08 kiểm trên máy: bóc được tiêu đề CÓ DẤU cho 77% văn bản**
bằng một regex ~15 dòng, chạy CPU vài giây, không cần gì của D. Mẫu bóc ra:

```
THÔNG TƯ QUY ĐỊNH CHI TIẾT LẬP BÁO CÁO THẨM ĐỊNH TRONG QUÁ TRÌNH TỔ CHỨC LỰA CHỌN NHÀ THẦU
QUYẾT ĐỊNH QUY ĐỊNH VỀ CƠ CẤU BIỂU GIÁ BÁN LẺ ĐIỆN
```

Cách bóc: tìm dòng chỉ có loại văn bản (`LUẬT` / `NGHỊ ĐỊNH` / `THÔNG TƯ` /
`QUYẾT ĐỊNH` / `BỘ LUẬT` / `PHÁP LỆNH`) trong 4000 ký tự đầu, rồi gom các dòng
tiếp theo cho tới khi gặp `Căn cứ`, `Số`, `Điều` hoặc gạch ngang.

**Phân tích lại vụ thua 2,0 điểm.** Nếu slug chỉ vô dụng thì phải hòa, không phải
tệ đi rõ. Ba cơ chế, không loại trừ nhau:

1. **Mất dấu** — XLM-R băm `Luat Pha san` và `Luật Phá sản` thành hai chuỗi subword
   khác hẳn, câu hỏi có dấu nên không khớp gì. Điều kiện cần cho hai cái dưới.
2. **Chiếm vị trí đầu** — cross-encoder nặng trọng số phần đầu. Nhét slug lên trước
   là đẩy nội dung thật ra khỏi chỗ đắt nhất.
3. **Lệch phân phối** — chuỗi ASCII nối gạch ngang không phải thứ AITeamVN từng thấy.

→ Khi thử lại: dùng tiêu đề có dấu **và ghép vào CUỐI đoạn**, không phải đầu.
Bản cũ chưa thử vị trí cuối, nên chưa tách được cơ chế 1 khỏi cơ chế 2.

**Xếp sau deepchunk.** Đổi text đưa vào model là đổi biến khác, đừng gộp chung một
lượt (quy tắc 3).

## Notebook

- `run_pipeline_kaggle.ipynb` — đo recall trên dev. **Không dùng để nộp bài.**
- `finalAnswer_run.ipynb` — sinh submission thật từ `public-official.json`.
  Bước 2 chặn cứng nếu qid trùng dev.

## Đang chờ D

1. ~~`bm25_top100_public.json`~~ ✅ **ĐÃ GIAO 12/08 11:01** (335MB, recall@100 = 0.9875)
2. ~~Candidate cho 700 câu còn lại của dev1000~~ — **ĐÃ HUỶ YÊU CẦU.** n_bm25 chốt bằng
   public LB thật rồi, chạy dev1000 tốn đúng bằng nộp một bài
3. ~~Bi-encoder mức đoạn (D4)~~ — **ĐÃ CHUYỂN SANG E 17/08.** Chunk + `top_chunk` bàn
   giao trọn cho E, E toàn quyền. Không chờ D nữa. Xem mục "PHÂN VAI MỚI 17/08"
4. ~~Ghép tiêu đề văn bản CÓ DẤU~~ — cũng là việc của E rồi (13/08 đã bóc được tiêu đề
   có dấu cho 77% văn bản bằng regex trên CPU, không cần gì của D)

**Việc duy nhất còn lại của D: recall 100 → 50 → 25**, và chỉ tính là giao hàng nếu
vượt ngưỡng ở mục "Ngưỡng giao D" đầu file. Cắt mà không vượt = hạ trần của E.

## Bẫy vừa dính (12/08)

D đặt file candidate dev300 **trùng tên** `bm25_top100_dev.json`, đè mất file 150 câu.
Không mất mát thật vì dev150 ⊂ dev1000, nhưng đúng là kiểu lỗi đã ghi ở trên.
→ Mọi file candidate phải mang số lượng câu trong tên: `_dev300`, `_dev1000`, `_public`.

## Hành chính — đã xong, đừng nhắc lại

Đã đăng ký, đã đóng lệ phí. Hạn chót cuộc thi: **15/09**.

## Ghi chú về ràng buộc BTC

Vượt 5 id ở một câu → **chỉ câu đó** bị Recall/Precision = 0, không phải cả bài.
Tài liệu nhóm và comment trong `submission.py` đang nói quá mức này.
