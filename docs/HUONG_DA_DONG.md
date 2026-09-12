# Sổ hướng đã đóng — mỗi dòng là một phép đo đã trả tiền

> Tài liệu này chép lại **kết quả âm**. Chúng đắt hơn kết quả dương: gần như toàn bộ
> giờ GPU của dự án nằm ở đây. Cập nhật 12/09/2026.
> Bài nộp cuối: **precision 0,711 · hạng 3/84** — đúng trần kiến trúc đã ước (0,71–0,72).

---

## 1. Quy luật quan trọng nhất — cái gì CHUYỂN được từ dev sang tập thi

Bốn can thiệp, cùng một hệ thống, cùng một tập dev:

| can thiệp | bản chất | dev | **tập thi thật** |
|---|---|---|---|
| cộng `λ·RRF` vào điểm CE | **phân xử top-2** | +0,6…+2,3 (p≥0,109) | **−0,9** |
| `replace` thay cho `max(ce, ce_deep)` | **phân xử top-2** | −2,00 | **−3,1** |
| **bộ phân xử cặp** | **phân xử top-2** | **+2,33 · p<0,05 · vượt ngưỡng khoá trước** | **−1,4** |
| **tinh chỉnh listwise** | **đổi hàm chấm** | +1,4…+1,9 | **+1,0** ✅ |

> **Mọi can thiệp vào *quyết định* hạng 1 vs hạng 2 đều không chuyển được.
> Can thiệp vào *hàm chấm* thì chuyển được.**

**Ba lần trên ba lần**, kể cả lần vượt ngưỡng ý nghĩa thống kê đã khoá **trước** khi chạy.

Giá trị của quy luật này: nó đóng cả một **họ** phương pháp bằng bốn điểm dữ liệu —
bộ phân xử cặp, thang điểm kiểu Elo, MLP trên đặc trưng thủ công, khớp phạm vi pháp lý —
chứ không phải đóng từng cái một.

**Giả thuyết cơ chế (chưa có phép đo đứng sau):** tập dev được tách ra từ `train.json`, cùng
quy trình gán nhãn với tập huấn luyện; tập thi là bộ riêng (giao với `train` = 0). Hàm chấm học
đặc trưng ngữ nghĩa **chung** nên chuyển được. Bộ phân xử top-2 học vào **đặc thù của các cặp
gần-hoà**, và đặc thù đó không chung giữa hai tập.

---

## 2. Sáu thí nghiệm cuối (10–12/09) — tất cả âm

| thử gì | chi phí | kết quả | vì sao âm |
|---|---|---|---|
| **Hạ trục `k`** 50 → 20/10 | 0 GPU | trần ~17 câu/1000 | `k=50` đã đọc **trọn** văn bản; hạ `k` gần như không đổi lựa chọn (83,4% đoạn thắng nằm trong top-10 BM25) |
| **Nhét điểm BM25 vào input** ([ECIR 2023](https://arxiv.org/abs/2301.09728)) | 0 GPU | **53,7%** trên tập cần cứu = tung xu | BM25 **đã được tiêu thụ hai lần** (dựng rổ qua RRF + chọn đoạn qua `pick_chunks`); nhét lần ba không thêm bit nào. Sâu hơn: hai ứng viên top-2 **đều đã được chính điểm đó chọn vào rổ** ⇒ phương sai còn lại là nhiễu |
| **Thêm BGE-M3** | 0 GPU | — | **đã đang dùng rồi**: nó là nền của cả bi-encoder truy hồi lẫn cross-encoder xếp hạng. Ensemble với bản gốc đã đo **−2,67** (chồng lấp 100% với tầng đọc sâu) |
| **Khớp thẩm quyền / phạm vi pháp lý** | 0 GPU | trần **1,60 điểm** | dưới sàn nhiễu bảng xếp hạng (1,45). Và thứ bậc trỏ **ngược dấu**: gold thường là văn bản bậc **thấp** (Thông tư/Quyết định hướng dẫn), không phải Luật khung — vì câu hỏi đời thường cần quy định thi hành cụ thể |
| **Negative hạng 2–10** thay 10–20 | 1,4h GPU | **thắng 4 · thua 4 · hoà 4** | dải hạng của negative **không phải nút thắt**. Val nội bộ tăng đẹp (0,7300→0,8150) mà không chuyển thành điểm |
| **Bộ phân xử cặp** | 1,7h GPU + 1 lượt nộp | dev **+2,33** → LB **−1,4** | xem mục 1 |

**Tổng: ~3,1 giờ GPU · 1 lượt nộp · 0 điểm tăng.**

### Ghi chú về bộ phân xử cặp — đã loại trừ hai lời giải thích dễ dãi
- **Không phải lệch cấu hình dải margin.** Ngưỡng `0,005` rơi vào phân vị 26,3% (dev, K=20),
  28,0% (thi, K=20), 28,0% (thi, K=50). Dải trên tập thi: K=20 ∩ K=50 = **277/280,
  Jaccard 0,98**. Dải được hiệu chuẩn đúng.
- **Không giải thích được bằng nhiễu phía tập thi.** Dự báo +25 câu, thực nhận −14 câu,
  lệch **6,6 SE**. Chiều ngược: nếu độ chính xác thật chỉ 60% thì quan sát 53/65 trên dev có
  p≈0,0003.

⇒ **Ghi lại là chưa giải thích được.** Không ép vào một câu chuyện gọn gàng.

---

## 3. Hướng đã đóng trước đó

| hướng | số liệu đóng nó |
|---|---|
| nộp 2–5 doc_id | `precision@m` giảm đơn điệu: 0,7100 → 0,4300 → 0,3056 → 0,1933 |
| `replace` thay `max(ce, ce_deep)` | **−3,1 điểm** trên 133 câu bất đồng |
| góc nhìn tiêu đề / phần đầu văn bản | đứng riêng **+3,67** nhưng ghép vào pipeline **âm mạnh** (p<0,001) — `ce_deep` bao trùm hoàn toàn |
| model to hơn (4B / 7B / 8B) | 15 câu khó, đúng ở hạng 1: **CE 0,568B = 5/15** · 4B 4/15 · 8B 4/15 · **7B 1/15**. Quy mô mua RECALL, không mua PRECISION |
| chưng cất từ model 8B | ròng **−16** nhóm/600. **Thầy 0,5417 THUA trò 0,5683** |
| tinh chỉnh pointwise (2 lần) | **−0,50** rồi **−6,50**. Nguyên nhân: negative lấy từ BM25 top-20 = trong kho pháp luật, top-20 đầy văn bản **trả lời được** mà không được gán nhãn |
| học lại đầu phân loại (đóng băng encoder) | Δ tốt nhất +0,67; **18 câu sai → vẫn 18 câu sai**, không đổi câu nào |
| ưu tiên văn bản mới / theo năm | gold là văn bản mới nhất đúng **2,0%** = ngẫu nhiên (p=0,000) |
| ưu thế theo loại văn bản / thẩm quyền (toàn cục) | âm, **kể cả khi ước tham số ngay trên chính tập dev** |
| ensemble nhiều bộ chấm / trộn hai pipeline | âm ở mọi trọng số. Ví dụ đắt nhất: **+4,00 ở tầng 1 nhưng chồng lấp 100%** ⇒ ròng −2,67 |
| gộp điểm z-score / min-max / RRF ở khâu chốt | thua quy tắc giữ chỗ ở **mọi** tham số đã quét |
| chọn `n` thích nghi theo câu | trần oracle chỉ +1,17 |
| ghép tên văn bản vào truy vấn | slug không dấu −2,0; tiêu đề có dấu +1,00 nhưng **83% trùng** tín hiệu sẵn có |
| hướng trích dẫn / số hiệu văn bản | câu hỏi chứa số hiệu kiểu `100/2019`: **3/300**. Đề bài là ngôn ngữ đời thường |
| mở rộng `M` cho tầng sâu | gold đã nằm trong top-M ở **290/295** câu ⇒ trần +1,7 |
| cải tiến `pick_chunks` | `K=20` đã bắt **90%** giá trị oracle |
| Gemini / LLM thương mại | hoà, **và thể lệ cấm** |

---

## 4. Quy tắc phương pháp — đã trả giá để học

1. **Ngưỡng phải TƯƠNG ĐỐI so với mốc hiện có**, không bao giờ là số tuyệt đối bốc ra.
2. **Mọi phép đo bộ chấm phải in kèm dòng "rổ trần, không xếp lại".** Thua dòng đó thì dừng.
3. **Không đánh giá model B trên mẫu được chọn bằng LỖI của model A.** Hồi quy về trung bình.
4. **Mọi con số dư địa phải đo ở ĐÚNG cấu hình bài đang nộp.**
5. **"Có tín hiệu thô" ≠ "cộng vào được".** Ưu thế TOÀN CỤC không thắng nổi bộ chấm đã đọc nội
   dung, trừ khi nó nói được điều gì **riêng cho từng câu**.
6. **"Không thấy hiệu ứng ở MỘT điểm đo" ≠ "hiệu ứng không tồn tại".**
7. **Nhiều "giải pháp" hoá ra là một — kiểm chồng lấn TRƯỚC khi cộng.** Đo thật: hai cần gạt
   cộng dồn ngây thơ +2,33, gộp lại chỉ **+1,33** — bằng đúng cần gạt tốt nhất đứng một mình.
8. **Chỉ chạy thí nghiệm kỳ vọng đổi ≥2 điểm.**
9. **Đo trần TRƯỚC khi chạy.** Đã cứu `M=30` (~4h), chưng cất (~18h), trục `k` (16 phút + 2 lượt nộp).
10. **Ước chi phí trên phân bố của VĂN BẢN ĐƯỢC TRUY HỒI, không phải toàn kho.** Đã ước sai gấp
    đôi, rồi sai 3,7× theo chiều ngược lại. **Đừng mượn thông lượng đo ở cấu hình khác.**
11. **Cổng đặt trước phải neo vào LỊCH HỌC, không vào số bước tuyệt đối.** Dính hai lần: cổng
    đặt ở bước 500 trong khi warmup dài 512 rồi 2.112 bước ⇒ cắt oan hai lượt chạy đang tốt.
    **Một cổng đo sai thứ còn tệ hơn không có cổng.**
12. **Tập dev KHÔNG dùng được để quyết định can thiệp nào chỉ tác động lên quyết định hạng 1 vs
    hạng 2.** Không phải vì cỡ mẫu — mà vì hiệu ứng **không tồn tại ngoài tập dev**. Loại can
    thiệp đó phải quyết bằng **một lượt nộp**.

### Ba bẫy kỹ thuật đáng ghi
- **Nhận diện dữ liệu vào bằng RUỘT, không bằng TÊN.** Một lượt chạy hỏng đúng một nửa vì
  `find()` bắt được file **trùng tên nhưng khác ruột**. `assert` trên tên file không bảo vệ được
  gì — phải chốt **md5 + hình dạng**, và **đặt vân tay vào tên file**.
- **`N=1` là dây tín hiệu.** Nếu bài dựng ở `N=1` không trùng khít bài cơ sở thì rổ sai, dừng ngay.
- **Đầu phân loại của model nền là TẠ, không phải điểm khởi đầu, khi đổi nhiệm vụ.** Dùng lại đầu
  chấm-liên-quan cho nhiệm vụ so-sánh-cặp ⇒ BCE khởi đầu ở loss **2,5** thay vì `ln2 = 0,693`.
  Kiểm loss ở bước 1 so với giá trị lý thuyết trước khi để nó chạy hết epoch.

---

## 5. Lỗ tái lập đã biết — phải đọc cùng `REPRODUCE.md`

Notebook tinh chỉnh seed thứ tự dữ liệu (`random.Random(0).shuffle`) nhưng **không seed
torch/CUDA**. Chạy lại cho ra một model *khác*. Với hiệu ứng chỉ **+0,9 điểm** và sai số lớn hơn
thế, một lượt huấn luyện lại có thể trả về 0,705 hoặc 0,715 mà **không có gì sai**. Bản vá:

```python
torch.manual_seed(0); torch.cuda.manual_seed_all(0); random.seed(0); np.random.seed(0)
torch.use_deterministic_algorithms(True, warn_only=True)
```
