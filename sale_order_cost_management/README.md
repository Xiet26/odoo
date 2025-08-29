# Sale Order Cost Management

## Mô tả

Module **Sale Order Cost Management** cho phép quản lý chi phí và tính toán lợi nhuận cho Sale Order trong Odoo.

## Tính năng chính

### 1. 📊 Quản lý chi phí bổ sung
- Thêm các chi phí phát sinh cho Sale Order
- Theo dõi trạng thái chi phí (Draft, Confirmed, Invoiced)
- Gán người chịu trách nhiệm cho từng chi phí

### 2. 💰 Tính toán Cost và Margin
- Tự động tính cost price từ `product.standard_price`
- Tính total cost cho từng order line
- Tính margin (lợi nhuận) cho từng line

### 3. 🛡️ Thông tin bảo hành
- Hiển thị thông tin bảo hành từ `custom_product_info` module
- Format: "Warranty Name (Duration months)"
- Hiển thị "No warranty" nếu sản phẩm không có bảo hành

### 4. 📈 Báo cáo tổng hợp
- **Total Revenue**: Tổng doanh thu
- **Product Costs**: Chi phí sản phẩm từ order lines
- **Additional Costs**: Chi phí bổ sung
- **Total All Costs**: Tổng tất cả chi phí
- **Final Profit**: Lợi nhuận cuối cùng

### 5. 📦 Thông tin kho hàng
- Hiển thị vị trí hàng trong kho cho từng sản phẩm
- Tự động cập nhật theo warehouse của Sale Order

### 6. 📊 Export Excel
- **One-click export**: Button "Export to Excel" trên Sale Order form
- **Multi-sheet Excel**: 3 sheets với thông tin chi tiết
  - **Order Summary**: Thông tin đơn hàng, tổng hợp tài chính, thống kê
  - **Order Lines**: Chi tiết từng line với cost, margin, warranty
  - **Additional Costs**: Breakdown chi phí bổ sung
- **Professional formatting**: Colors, borders, currency formatting
- **Smart styling**: Profit/loss color coding, auto-fit columns

## Cài đặt

### Yêu cầu
- Odoo 16.0+
- Module `sale_management`
- Module `custom_product_info` (cho tính năng warranty)

### Các bước cài đặt
1. Copy module vào thư mục addons
2. Restart Odoo server
3. Vào **Apps** → tìm "Sale Order Cost Management"
4. Click **Install**

## Sử dụng

### 1. Thêm chi phí bổ sung
1. Vào **Sales** → **Orders** → chọn Sale Order
2. Click tab **"Costs"**
3. Thêm các chi phí bổ sung (vận chuyển, bảo hiểm, etc.)

### 2. Xem cost analysis
1. Vào Sale Order
2. Click tab **"Costing"** để xem chi tiết cost từng line
3. Click tab **"Summary"** để xem tổng hợp

### 3. Xem thông tin bảo hành
- Thông tin bảo hành hiển thị ở:
  - Tab "Order Lines" (cột Warranty - optional)
  - Tab "Costing" 
  - Form view của từng order line

### 4. Theo dõi lợi nhuận
- **Line Margin**: Lợi nhuận từng line (Subtotal - Total Cost)
- **Final Profit**: Lợi nhuận tổng (Revenue - All Costs)

### 5. Export Excel
1. Mở Sale Order cần export
2. Click button **"Export to Excel"** (chỉ hiện với orders đã confirm)
3. File Excel sẽ tự động download với tên: `SO001_Export_20240829.xlsx`
4. Mở file để xem 3 sheets:
   - **Order Summary**: Tổng quan đơn hàng và tài chính
   - **Order Lines**: Chi tiết từng sản phẩm
   - **Additional Costs**: Chi phí bổ sung

## Cấu trúc dữ liệu

### Models mới
- **sale.order.cost.line**: Chi phí bổ sung cho Sale Order

### Fields mới trên Sale Order
- `cost_ids`: Danh sách chi phí bổ sung
- `total_cost`: Tổng chi phí bổ sung
- `order_lines_cost`: Chi phí từ order lines
- `total_all_costs`: Tổng tất cả chi phí
- `final_profit`: Lợi nhuận cuối cùng
- `stock_location_info`: Thông tin vị trí kho

### Fields mới trên Sale Order Line
- `cost_price`: Giá cost của sản phẩm
- `total_cost`: Tổng cost (cost_price × quantity)
- `line_margin`: Margin của line
- `product_warranty`: Thông tin bảo hành

## Views mới

### 1. Tab "Costs"
- Quản lý chi phí bổ sung
- Hiển thị tổng chi phí bổ sung

### 2. Tab "Costing" 
- List view với các cột: Product, Qty, Cost Price, Unit Price, Total Cost, Subtotal, Margin, Warranty

### 3. Tab "Summary"
- Báo cáo tổng hợp doanh thu, chi phí, lợi nhuận

### 4. Tab "Vị trí hàng trong kho"
- Thông tin vị trí hàng cho từng sản phẩm

### 5. Cột "Warranty" trong Order Lines
- Thêm cột warranty vào bảng order lines chính (optional)

## Cấu hình

### 1. Set Cost Price cho Products
1. Vào **Inventory** → **Products**
2. Chọn product → tab **General Information**
3. Set giá trị cho field **Cost**

### 2. Set Warranty cho Products
1. Vào **Inventory** → **Products**  
2. Chọn product → set field **Warranty**
3. Warranty sẽ tự động hiển thị trong order lines

## Troubleshooting

### Lỗi "column does not exist"
- **Nguyên nhân**: Database chưa được update
- **Giải pháp**: Restart server và upgrade module

### Không thấy cột Warranty
- **Nguyên nhân**: Cột bị ẩn
- **Giải pháp**: Click icon ⚙️ trong bảng order lines và enable cột "Warranty"

### Cost Price = 0
- **Nguyên nhân**: Product chưa có standard_price
- **Giải pháp**: Set Cost cho product trong Inventory

## Phát triển

Xem file `doc/DEVELOPMENT_GUIDE.md` để biết chi tiết về:
- Cấu trúc code
- Cách extend module
- Best practices
- Troubleshooting

## Changelog

### v1.0.9 (Latest)
- ✅ Thêm warranty column vào Order Lines table
- ✅ Fix view inheritance cho sol_o2m widget
- ✅ Cải thiện user experience

### v1.0.8
- ✅ Thêm warranty field vào order line detail
- ✅ Thêm warranty vào tab Costing

### v1.0.7
- ✅ Thêm product warranty field
- ✅ Integration với custom_product_info module

### v1.0.6
- ✅ Thêm cost breakdown vào tab Summary
- ✅ Fix XML label errors

### v1.0.5
- ✅ Thêm computed fields cho cost analysis
- ✅ Tạo migration scripts

### v1.0.1-1.0.4
- ✅ Tạo models và views cơ bản
- ✅ Thêm tabs Costs, Costing, Summary
- ✅ Fix various bugs

## Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra file `doc/DEVELOPMENT_GUIDE.md`
2. Kiểm tra Odoo logs
3. Restart server và upgrade module
4. Liên hệ developer team

## License

This module is licensed under LGPL-3.

---

**Developed by**: Odoo Development Team  
**Version**: 1.0.9  
**Compatible**: Odoo 16.0+
