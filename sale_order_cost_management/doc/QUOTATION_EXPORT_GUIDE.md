# Hướng dẫn xuất báo giá Word (v1.3.0)

## Tổng quan

Module đã được cập nhật với chức năng xuất báo giá dạng Word (.docx) với cấu trúc chuyên nghiệp gồm 8 thành phần chính theo tiêu chuẩn doanh nghiệp.

## Cách sử dụng

1. **Truy cập Sale Order**: Mở đơn hàng/báo giá cần xuất
2. **Tìm button "Quotation Word"**: Trong phần button box (góc trên bên phải)
3. **Click xuất**: File Word sẽ được tải xuống tự động

## Cấu trúc báo giá Word

### 1. **Thông tin chung của báo giá**
- Số báo giá: IMV-[số_thứ_tự] (tự động từ order name)
- Ngày: DD/MM/YYYY (ngày hiện tại)
- Logo và tên công ty IMALL Việt Nam

### 2. **Thông tin khách hàng**
- Tên khách hàng/công ty
- MST (nếu có)
- Địa chỉ
- Số điện thoại
- Email

### 3. **Thông tin công ty gửi báo giá**
- Tên công ty: CÔNG TY TNHH IMALL VIỆT NAM
- MST: 0316161476
- Địa chỉ: 52/1A Huỳnh Văn Nghệ, P. Tân Sơn, TP. HCM
- Nhân viên phụ trách (từ user_id của order)
- Website và thông tin liên hệ

### 4. **Lời mở đầu**
Đoạn cảm ơn và giới thiệu báo giá theo yêu cầu khách hàng.

### 5. **Bảng chi tiết sản phẩm/thiết bị**
Bảng 7 cột:
- **TT**: Số thứ tự
- **Tên thiết bị**: Bao gồm tên sản phẩm, model, part number, xuất xứ, bảo hành
- **ĐVT**: Đơn vị tính
- **SL**: Số lượng
- **Đơn giá**: Giá đơn vị
- **Thành tiền**: Tổng tiền từng dòng
- **Ghi chú**: Thời gian giao hàng và ghi chú khác

### 6. **Tổng hợp giá trị**
- Tổng tiền trước VAT
- VAT (10%)
- Tổng tiền cần thanh toán
- Bằng chữ (số tiền viết bằng chữ)

### 7. **Điều khoản thương mại**
- Thời gian giao hàng
- Phương thức thanh toán (hàng có sẵn/hàng đặt)
- Thông tin tài khoản ngân hàng
- Điều kiện bảo hành
- Hiệu lực báo giá (30 ngày)

### 8. **Phần xác nhận & chữ ký**
- Người báo giá (nhân viên phụ trách)
- Giám đốc (Nguyễn Thị Minh Tâm)
- Chỗ ký tên và đóng dấu
- Thông tin liên hệ đặt hàng

## Yêu cầu kỹ thuật

- **Thư viện**: python-docx
- **Format**: .docx (Microsoft Word)
- **Encoding**: UTF-8
- **Font**: Mặc định của Word (Calibri)

## Lưu ý

1. **Điều kiện hiển thị**: Button chỉ hiện khi order không ở trạng thái 'draft' hoặc 'cancel'
2. **Dữ liệu**: Lấy từ thông tin order, customer, và order lines
3. **Tên file**: Format `Quotation_[Order_Name].docx`
4. **Tự động tải**: File được tải xuống trực tiếp, không cần lưu trên server

## Tùy chỉnh

Để tùy chỉnh template, chỉnh sửa các method trong `controllers/sale_order_export.py`:
- `_add_quotation_header()`: Header và tiêu đề
- `_add_customer_info()`: Thông tin khách hàng  
- `_add_company_info()`: Thông tin công ty
- `_add_opening_message()`: Lời mở đầu
- `_add_product_table()`: Bảng sản phẩm
- `_add_total_summary()`: Tổng hợp giá trị
- `_add_commercial_terms()`: Điều khoản thương mại
- `_add_signature_section()`: Phần chữ ký
