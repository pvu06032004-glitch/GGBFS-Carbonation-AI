# AI dự đoán cacbonat hóa bê tông dùng xỉ lò cao

Ứng dụng Streamlit nghiên cứu/minh họa dự đoán chiều sâu cacbonat hóa bê tông dùng xỉ lò cao, so sánh kịch bản, ước tính thời điểm mặt cacbonat hóa đạt lớp bảo vệ, xuất Excel/PDF.

## Cảnh báo khoa học quan trọng
Dữ liệu mặc định được sinh bằng công thức lập trình và đánh dấu `SYNTHETIC_DEMO`; đây **không phải dữ liệu thí nghiệm**. Các chỉ số R²/MAE/RMSE trên dữ liệu này không thể được báo cáo như độ chính xác của mô hình trên bê tông thực. Ước tính tuổi thọ dùng quan hệ đơn giản x=K√t, giả định điều kiện phơi nhiễm không đổi; không mô hình hóa đầy đủ khởi phát/lan truyền ăn mòn và không dùng cho thiết kế, nghiệm thu hoặc đánh giá an toàn kết cấu.

## Chạy trên Windows
Cần Python 3.10–3.12. Mở PowerShell tại thư mục dự án:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```
Mở URL mà Streamlit hiện ra, thường là http://localhost:8501.

## Chạy trên macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Định dạng dữ liệu CSV thực nghiệm
CSV phải có các cột: `W_B, Cement_kg_m3, GGBFS_pct, FA_pct, SF_pct, fc_28_MPa, Curing_days, Curing_type, CO2_pct, RH_pct, Temperature_C, Exposure_days, Exposure_condition, CO2_type, Carbonation_depth_mm`. Tên cột `GGBFS_pct` được giữ để tương thích với định dạng dữ liệu và mô hình hiện tại; cột này biểu thị tỷ lệ xỉ lò cao (%).
- W_B: tỷ lệ nước/chất kết dính (vd 0.45).
- GGBFS_pct (tỷ lệ xỉ lò cao), FA_pct (tro bay), SF_pct (silica fume): phần trăm chất kết dính.
- CO2_pct: phần trăm CO₂ (0.04 nghĩa là 0.04%).
- RH_pct: độ ẩm tương đối (%); Exposure_days: ngày; Carbonation_depth_mm: chiều sâu đo (mm).
- Curing_type: Water/Sealed/Air; Exposure_condition và CO2_type: Natural/Accelerated.
Kiểm tra nguồn, đơn vị, dữ liệu thiếu/trùng và phương pháp đo. Nghiên cứu thực tế nên chia tập theo mẻ/nghiên cứu và kiểm định ngoài độc lập, không chỉ chia ngẫu nhiên.

## Triển khai website trực tuyến
1. Tạo repository GitHub và tải toàn bộ nội dung thư mục lên.
2. Mở https://share.streamlit.io/ và đăng nhập bằng GitHub.
3. Chọn Create app, chọn repository/branch, file chính `app.py`, rồi Deploy.
4. Khi build thành công, Streamlit cấp URL dạng `https://ten-app.streamlit.app`; kiểm tra quyền truy cập rồi gửi link.

Đường link chưa tồn tại trước khi bạn thực hiện triển khai. Kiểm tra cài đặt quyền riêng tư và không commit dữ liệu nhạy cảm vào repository công khai.

## Kiểm thử
```bash
python -m unittest discover -s tests -v
```

## Cấu trúc
- `app.py`: giao diện web.
- `src/model.py`: tạo dữ liệu demo, huấn luyện, đánh giá, dự đoán.
- `src/lifetime.py`: phép ước tính tuổi thọ sàng lọc.
- `src/reports.py`: xuất Excel/PDF.
- `data/sample_data.csv`: dữ liệu mẫu mô phỏng.
- `tests/`: kiểm thử cơ bản.
