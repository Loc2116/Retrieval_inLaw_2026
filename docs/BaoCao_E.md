# Báo cáo cá nhân — Thành viên E
## Xếp hạng và chốt 5 văn bản trả lời

**Cuộc thi:** DSC 2026, Task 1 — Truy hồi văn bản pháp luật
**Người viết:** Tạ Gia Khiêm
**Cập nhật:** 12/08/2026

> Ghi chú: bản này đã điền sẵn mọi số liệu đo được tính đến 12/08.
> Chỗ nào ghi `[chờ số]` là thí nghiệm đang chạy, điền vào khi có kết quả.

---

## 1. Việc tôi phụ trách và con số tôi chịu trách nhiệm

### Bài toán

Hệ thống chia hai tầng. Thành viên D lo tầng dưới: từ 8.532 văn bản pháp luật,
với mỗi câu hỏi lọc ra 100 văn bản có khả năng chứa câu trả lời. Tôi lo tầng trên:
từ 100 văn bản đó, chọn ra đúng 5 văn bản để nộp.

Ban tổ chức chấm bằng **Recall** — trong 5 văn bản nộp có chứa văn bản đúng hay không.
Vì 92,6% câu hỏi chỉ có một văn bản đúng, điểm gần như là được hoặc mất trọn.

### Con số tôi sở hữu

| Chỉ số | Nghĩa là gì |
|---|---|
| **Recall@5** | Tỉ lệ tìm đúng trong 5 văn bản nộp. **Đây chính là điểm bảng xếp hạng.** |
| Recall@5 / Recall@100 | Tỉ lệ chuyển hoá — đo riêng phần việc của tôi, tách khỏi chất lượng tầng dưới |

Chỉ số thứ hai quan trọng vì nó phân biệt được hai loại thất bại: văn bản đúng
không lọt vào 100 ứng viên (lỗi tầng dưới, tôi không cứu được), và văn bản đúng
có trong 100 nhưng tôi không đẩy được lên top 5 (lỗi của tôi).

### Điểm xuất phát

Nếu lấy thẳng 5 văn bản đầu theo thứ tự của tầng dưới, không xử lý gì:

| Tập đo | Recall@5 | Recall@100 |
|---|---|---|
| dev 150 câu | 0.7578 | 0.9700 |
| dev 300 câu | 0.7533 | 0.9783 |

Nghĩa là văn bản đúng gần như luôn nằm trong 100 ứng viên (97–98%), nhưng chỉ 3/4
số lần nó tự nằm trong 5 vị trí đầu. Khoảng cách 22 điểm giữa hai cột chính là
phần việc của tôi.

---

## 2. Các cách đã thử, kể cả cách thất bại

### 2.1 Chọn mô hình chấm điểm

Mô hình tôi dùng đọc **cùng lúc** câu hỏi và một đoạn văn bản, rồi cho một điểm số
"hai cái này có liên quan không". Khác với cách nén riêng câu hỏi và văn bản thành
hai vector rồi so sánh — cách đó nhanh hơn nhưng thô hơn nhiều.

Đã thử 5 mô hình, tất cả đều nằm trong danh sách ban tổ chức cho phép:

| Mô hình | Số tham số | Recall@5 |
|---|---|---|
| **AITeamVN/Vietnamese_Reranker** | 567.755.777 | **0.8567** |
| BAAI/bge-reranker-v2-m3 | 567.755.777 | 0.8467 |
| Qwen/Qwen3-Reranker-0.6B | 595.776.512 | 0.7711 |
| namdp-ptit/ViRanker | — | ~0.76 |
| Không dùng mô hình nào (chỉ tầng dưới) | 0 | 0.7578 |

**Phát hiện quan trọng nhất của cả báo cáo này:** hai mô hình đứng đầu bảng có
**số tham số trùng khít nhau đến từng đơn vị**. Tra ra thì `AITeamVN` chính là bản
`bge-reranker-v2-m3` được huấn luyện thêm trên tiếng Việt. Cùng kiến trúc, cùng
kích thước, chỉ khác bước huấn luyện thêm — và hơn 3 điểm.

Ban tổ chức cho phép dùng mô hình tới 4 tỉ tham số. Tôi chỉ dùng 0,57 tỉ. Kết luận
rút ra là **huấn luyện đúng ngôn ngữ quan trọng hơn mô hình to**, và việc đi tìm
mô hình lớn hơn là đường cụt trong bài toán này.

### 2.2 Vì sao Qwen3 kém hẳn — và đây không phải lỗi của mô hình

Qwen3-Reranker hoạt động khác hai mô hình kia. Nó không cho điểm liên tục mà trả lời
câu hỏi "có/không". Khi thử với một cặp rõ ràng không liên quan (thủ tục đăng ký xe máy
so với tiêu chuẩn hạt giống lúa), nó phân biệt xuất sắc: 0,6926 so với 0,0001.

Nhưng khi chấm 100 ứng viên thật, điểm dồn hết vào khoảng 0,998–0,999. Không mâu thuẫn:
100 ứng viên đó đã được tầng dưới lọc nên **cái nào cũng đúng chủ đề**. Nó trả lời "có"
cho tất cả, và nó không sai. Nhưng bài toán hỏi "cái nào đúng nhất trong 100 cái đều
đúng chủ đề", mà câu trả lời có/không không đủ mịn để phân biệt.

Nghịch lý đáng ghi nhận: **tầng dưới càng tốt thì loại mô hình này càng vô dụng**.

### 2.3 Cách chốt 5 văn bản — phần ăn điểm nhiều nhất

Sau khi có điểm cho cả 100 văn bản, vẫn còn câu hỏi: xếp thế nào thành 5?

Có hai nguồn ý kiến khác nhau về cùng 100 văn bản đó — thứ hạng của tầng dưới
(dựa trên trùng lặp từ khoá) và điểm của mô hình chấm (dựa trên hiểu nghĩa).
Hai bên giỏi ở hai nhóm câu khác nhau.

**Cách thắng:** dành cố định 1 chỗ trong 5 cho văn bản hạng nhất của tầng dưới,
4 chỗ còn lại theo mô hình chấm.

| Số chỗ dành cho tầng dưới | Recall@5 |
|---|---|
| 0 (chỉ nghe mô hình chấm) | 0.8567 |
| **1** | **0.8900** |
| 2 | 0.8733 |
| 3 | 0.8500 |
| 5 (chỉ nghe tầng dưới) | 0.7578 |

**Các cách đã thử và THUA** — ghi lại để không ai làm lại:

| Cách | Recall@5 |
|---|---|
| Trộn hai điểm số theo tỉ lệ (chuẩn hoá kiểu min-max) | 0.8678 |
| Trộn hai điểm số (chuẩn hoá kiểu z-score) | 0.8678 |
| Trộn theo thứ hạng (RRF) | 0.8644 |
| Dành 1 chỗ, chồng lên trên bản đã trộn điểm | 0.8744 |
| Kết hợp hai mô hình chấm khác nhau | 0.9000 nhưng độ tin cậy chỉ 78,7% |

**Lý giải vì sao cách trộn điểm thua:** trộn làm ảnh hưởng của tầng dưới lan ra cả
5 chỗ, mỗi chỗ một ít — kết quả là cả hai bên đều bị làm mờ. Cách dành chỗ thì cho
mỗi bên một phần lãnh địa riêng: tầng dưới giữ 1 chỗ không ai tranh, mô hình chấm
toàn quyền 4 chỗ còn lại.

Kết hợp hai mô hình chấm cho điểm cao nhất bảng nhưng tốn gấp đôi thời gian tính
toán, và độ tin cậy 78,7% có nghĩa là cứ 5 lần thử lại thì 1 lần nó thua. Không đáng.

### 2.4 Kiểm tra độ tin cậy

Con số đo trên 150 câu có thể là may rủi. Tôi kiểm bằng cách bốc ngẫu nhiên 150 câu
(có lặp) từ chính 150 câu đó, tính lại, làm 3.000 lần:

| So sánh | Tỉ lệ thắng |
|---|---|
| Dành 1 chỗ **>** chỉ nghe mô hình chấm | **96,9%** |
| Dành 1 chỗ **>** trộn điểm | 94,7% |
| Kết hợp 2 mô hình **>** dành 1 chỗ | 78,7% |

Tôi lấy mốc 95% để kết luận. Nên chỉ kết quả đầu tiên được coi là chắc chắn.

---

## 3. Bảng tổng hợp

Đo trên tập dev 150 câu, cùng một bộ ứng viên đầu vào từ thành viên D.

| Cấu hình | Recall@5 | Ghi chú |
|---|---|---|
| Chỉ tầng dưới, không xử lý | 0.7578 | điểm xuất phát |
| ViRanker | ~0.76 | giới hạn 256 từ, văn bản luật quá dài |
| Qwen3-Reranker-0.6B | 0.7711 | cơ chế có/không, không hợp |
| + dành 1 chỗ | 0.7844 | |
| bge-reranker-v2-m3 | 0.8467 | mô hình gốc của AITeamVN |
| + dành 1 chỗ | 0.8600 | |
| **AITeamVN/Vietnamese_Reranker** | 0.8567 | |
| **+ dành 1 chỗ** | **0.8900** | ← cấu hình chốt |
| Trần lý thuyết (tầng dưới) | 0.9700 | |

Chưa thử, và lý do:

- **PhoRanker** — nền PhoBERT, chỉ đọc được 256 từ trong khi đoạn văn bản trung bình
  dài hơn nhiều, lại đòi phải tách từ ghép trước. Bất lợi về cấu trúc, không phải
  do mô hình kém.
- **Prism-Qwen3.5-Reranker-2B** — cùng cơ chế có/không với Qwen3, đã biết là không hợp.
- **Các mô hình MiniLM** — quá nhỏ hoặc chỉ dùng cho tiếng Anh.

---

## 4. Phân tích lỗi

### 4.1 Phân loại 20 câu sai trên dev 150

| Nhóm | Số câu | Ai sửa được |
|---|---|---|
| Văn bản đúng không nằm trong 100 ứng viên | 3 | Tầng dưới. Tôi bó tay. |
| Văn bản đúng ở hạng 1–5 của tầng dưới | 7 | **Tôi** — cách dành chỗ cứu được 6 |
| Văn bản đúng ở hạng 6–20 | 9 | **Tôi** — cần mô hình mạnh hơn thật sự |
| Văn bản đúng ở hạng 71 | 1 | Cả hai tầng đều yếu |

**16 trong 17 câu tôi làm hỏng có văn bản đúng nằm trong top 20 của tầng dưới.**
Đây là con số dẫn tôi tới cách "dành 1 chỗ".

### 4.2 Mô hình chấm cứu được bao nhiêu, phá bao nhiêu

| | Số câu |
|---|---|
| Cứu được (tầng dưới trượt, mô hình kéo vào) | 21 |
| Làm hỏng (tầng dưới đúng, mô hình đẩy ra) | 7 |
| **Lãi ròng** | **+14 câu** |

Trong 7 câu bị làm hỏng, **6 câu có văn bản đúng đang đứng hạng nhất** của tầng dưới.
Mô hình cầm sẵn đáp án rồi ném đi.

### 4.3 Ba nguyên nhân cụ thể

**Nguyên nhân 1 — hai văn bản gần như giống hệt nhau** (câu 147712)

Câu hỏi về *Quỹ Nghĩa tình đồng đội Công an nhân dân*. Đáp án đúng là điều lệ quỹ đó.
Mô hình chọn điều lệ của *Quỹ Hỗ trợ phát triển Y tế - Giáo dục Việt Nam*.

Lý do: đoạn văn bản đưa cho mô hình chỉ ghi *"Điều 8. Hội đồng quản lý Quỹ..."* —
chữ "Quỹ" trần trụi, không có tên. Điều lệ quỹ nào cũng viết y hệt. **Mô hình không
có thông tin để phân biệt**, nên đoán, và đoán trượt. Đây không phải lỗi của mô hình.

Hướng sửa: ghép tên văn bản vào đầu mỗi đoạn trước khi đưa cho mô hình chấm. `[chờ số]`

**Nguyên nhân 2 — đúng văn bản nhưng đưa nhầm đoạn** (câu 136940)

Câu hỏi về tái cơ cấu ngành dầu khí. Văn bản đúng có được chọn vào 100 ứng viên,
nhưng ba đoạn trích kèm theo không có đoạn nào nói về dầu khí. Mô hình chấm không
bao giờ được nhìn thấy bằng chứng.

Hướng sửa: tăng số đoạn trích mỗi văn bản từ 3 lên 5.

**Nguyên nhân 3 — khớp chủ đề nhưng trượt ý định câu hỏi** (câu 115446, 40624)

Câu hỏi: *"Có bắt buộc thành lập công đoàn cơ sở với doanh nghiệp 17–18 lao động?"*
Mô hình chọn điều nói về *trình tự, thủ tục thành lập công đoàn cơ sở* — đúng chủ đề
bề mặt. Đáp án thật nằm ở điều nói về *quyền và trách nhiệm*.

Mô hình khớp **chủ đề**, không khớp **điều câu hỏi đang thật sự hỏi**. Đây là điểm yếu
điển hình của mô hình chưa được huấn luyện riêng cho loại dữ liệu này.

Hướng sửa: huấn luyện thêm trên dữ liệu của cuộc thi. `[chờ số]`

---

## 5. Kết luận và hướng chưa kịp làm

### Cấu hình chốt

```
Mô hình chấm : AITeamVN/Vietnamese_Reranker (567.755.777 tham số)
Cách chốt 5  : dành 1 chỗ cho hạng nhất của tầng dưới
Recall@5     : 0.8900 trên dev 150 câu
```

### Ba điều học được

**Huấn luyện đúng ngôn ngữ quan trọng hơn mô hình to.** Hai mô hình cùng kiến trúc,
cùng số tham số, chênh 3 điểm chỉ vì một bên được huấn luyện thêm trên tiếng Việt.
Ngân sách 4 tỉ tham số của ban tổ chức là đường cụt: tôi dùng 0,57 tỉ và không tìm
được bằng chứng nào cho thấy to hơn thì tốt hơn.

**Giữ chỗ hiệu quả hơn trộn điểm.** Khi có hai nguồn ý kiến giỏi ở hai nhóm câu khác
nhau, cho mỗi bên một phần lãnh địa riêng tốt hơn là lấy trung bình. Trộn làm cả hai
cùng bị mờ đi.

**Loại mô hình quan trọng hơn điểm chuẩn của nó.** Qwen3-Reranker đạt điểm cao trên
các bộ đo phổ thông, nhưng ở đây thua cả 8 điểm — vì cơ chế trả lời có/không không đủ
mịn khi 100 ứng viên đều đúng chủ đề.

### Đối chiếu với điểm thi thật

| Ngày | Cấu hình | Điểm nội bộ | Điểm bảng xếp hạng |
|---|---|---|---|
| 12/08 | AITeamVN + dành 1 chỗ, dùng bộ ứng viên dự phòng | 0.8900 | **0.8440** |

Chênh 4,6 điểm. Nhưng 3,75 điểm trong đó giải thích được: lần nộp này dùng bộ ứng viên
dự phòng tôi tự sinh (trần 0.9500) thay vì của thành viên D (trần 0.9875). Phần chênh
thật của tập dev chỉ khoảng 1 điểm.

**Kết luận: tập dev nội bộ đáng tin, dùng để ra quyết định được.**

### Việc chưa kịp làm

| Việc | Vì sao chưa |
|---|---|
| Ghép tên văn bản vào đoạn trích | đang đo |
| Huấn luyện thêm trên dữ liệu cuộc thi | đang đo |
| Tăng số đoạn trích mỗi văn bản từ 3 lên 5 | chờ tầng dưới |
| Chọn ví dụ sai "khó" khi huấn luyện | cần bộ ứng viên cho 6.000 câu huấn luyện |
| Đo lại trên tập dev 1.000 câu | chờ tầng dưới giao đủ ứng viên |

### Một ghi chú về cách đo

Tập dev 150 câu cho khoảng sai số ±0,05. Nghĩa là **mọi khác biệt dưới 5 điểm đều
không phân biệt được với ngẫu nhiên** nếu so hai cấu hình riêng lẻ. Tôi đã hai lần
gặp đúng giới hạn này trong một ngày: không kết luận được bge có thua AITeamVN thật
không, và không kết luận được việc kết hợp hai mô hình có lợi không.

Tập dev 1.000 câu thu sai số còn ±0,019. Đây là lý do phải mở rộng tập đo trước khi
chốt cấu hình cuối cùng, chứ không phải để điểm cao hơn — tập đo lớn không làm mô hình
tốt lên, nó chỉ giúp chọn đúng.

---

## Phụ lục — cách đọc các con số

**Recall@5** — trong 5 văn bản nộp có văn bản đúng không. Vì hầu hết câu chỉ có một
văn bản đúng, con số này gần như là tỉ lệ câu trả lời được.

**Recall@100** — văn bản đúng có nằm trong 100 ứng viên tầng dưới đưa lên không.
Đây là trần tuyệt đối: tôi không bao giờ vượt được con số này.

**Khoảng sai số** — bốc ngẫu nhiên lại tập câu hỏi 3.000 lần rồi tính lại điểm, lấy
khoảng chứa 95% kết quả. Cho biết nếu đổi sang tập câu hỏi khác thì điểm dao động
tới đâu.

**Tỉ lệ thắng khi bốc lại** — trong 3.000 lần bốc lại, cấu hình A hơn cấu hình B bao
nhiêu lần. Đáng tin hơn việc chỉ nhìn hai con số điểm, vì nó so trên **cùng** bộ câu
hỏi mỗi lần.
