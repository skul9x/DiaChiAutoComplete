# 🏠 Address Autocomplete - Python Recreation

Tái tạo thuật toán **Autocomplete Địa chỉ** từ hệ thống HIS (C#) bằng Python + Tkinter.

## 📋 Mô tả

Ứng dụng cho phép tra cứu địa chỉ Việt Nam bằng **mã viết tắt** (shortcut). Dữ liệu được load từ file CSV xuất từ SQL Server.

### Ví dụ sử dụng:
| Nhập | Kết quả |
|------|---------|
| `bnbn` | Thành Phố Bắc Ninh, Tỉnh Bắc Ninh |
| `hnbdpx` | Phường Phúc Xá, Quận Ba Đình, Thành phố Hà Nội |
| `hcmq1bng` | Phường Bến Nghé, Quận 1, Thành phố Hồ Chí Minh |

## 🚀 Cài đặt & Chạy

### Yêu cầu
- Python 3.6+
- Tkinter (có sẵn trong Python)

### Bước 1: Xuất dữ liệu từ SQL Server

Chạy query sau trong SQL Server Management Studio:

```sql
SELECT 
    ma_diachinh,
    ten_diachinh,
    ISNULL(ma_cha, '') as ma_cha,
    loai_diachinh,
    ISNULL(mota_them, '') as mota_them
FROM dbo.dmuc_diachinh
ORDER BY loai_diachinh, ma_diachinh;
```

**Lưu kết quả:**
1. Right-click vào kết quả → **Save Results As...**
2. Chọn định dạng CSV
3. Lưu với tên: `dmuc_diachinh.csv`
4. Đặt cùng thư mục với file Python

### Bước 2: Chạy ứng dụng

```bash
python address_autocomplete.py
```

Ứng dụng sẽ tự động load file `dmuc_diachinh.csv` nếu có.

## 📊 Cấu trúc dữ liệu

### Bảng `dmuc_diachinh`

| Cột | Mô tả |
|-----|-------|
| `ma_diachinh` | Mã địa chính (PK) |
| `ten_diachinh` | Tên địa danh |
| `ma_cha` | Mã địa chính cấp trên |
| `loai_diachinh` | 0: Tỉnh/TP, 1: Quận/Huyện, 2: Xã/Phường |
| `mota_them` | Mã viết tắt (shortcut) |

### Thuật toán tạo Shortcut

Shortcut được ghép theo thứ tự: **Tỉnh + Huyện + Xã**

```
Tỉnh Bắc Ninh      → mota_them = "bn"
├── TP Bắc Ninh    → mota_them = "bn"  → combined = "bnbn"
│   ├── P. Vũ Ninh → mota_them = "vn"  → combined = "bnbnvn"
│   └── P. Tiền An → mota_them = "ta"  → combined = "bnbnta"
└── H. Quế Võ      → mota_them = "qv"  → combined = "bnqv"
    └── X. Việt Hùng → mota_them = "vh" → combined = "bnqvvh"
```

## 🎯 Tính năng

- ✅ Load dữ liệu từ CSV
- ✅ Autocomplete theo mã viết tắt
- ✅ Tìm kiếm: exact match → startswith → contains
- ✅ Hỗ trợ tất cả các cấp (Tỉnh, Huyện+Tỉnh, Xã+Huyện+Tỉnh)
- ✅ Copy địa chỉ vào clipboard
- ✅ Điều hướng bàn phím (↑↓ Enter)

## 📁 Cấu trúc thư mục

```
Python Logic/
├── address_autocomplete.py   # Code chính
├── dmuc_diachinh.csv         # Dữ liệu (xuất từ SQL)
└── README.md                 # File này
```

## 🔧 Debug

Nhấn nút **"🔍 Debug"** để xem danh sách shortcuts của các địa chỉ chứa keyword.

## 📝 License

Code tái tạo từ hệ thống HIS để mục đích học tập và nghiên cứu.
