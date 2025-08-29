# Các lỗi đã gặp và cách khắc phục

## 1. Lỗi XML Views

### 1.1 ParseError: Label tag must contain a "for"
**Lỗi:**
```
Label tag must contain a "for". To match label style without corresponding field or button, use 'class="o_form_label"'.
```

**Nguyên nhân:** Sử dụng `<label>` tag không đúng cách

**Code SAI:**
```xml
<label string="Costs Breakdown:"/>
```

**Code ĐÚNG:**
```xml
<span class="o_form_label">Costs Breakdown:</span>
<!-- HOẶC -->
<label for="field_name" string="Label Text"/>
```

### 1.2 View reference not found
**Lỗi:**
```
External ID not found in the system: sale.view_order_line_form
```

**Nguyên nhân:** XML ID không tồn tại hoặc sai tên

**Code SAI:**
```xml
<field name="inherit_id" ref="sale.view_order_line_form"/>
```

**Code ĐÚNG:**
```xml
<field name="inherit_id" ref="sale.sale_order_line_view_form_readonly"/>
```

**Cách kiểm tra XML ID:**
1. Developer mode → Edit View
2. Hoặc search trong source code: `grep -r "view_order_line_form" addons/sale/`

### 1.3 Inherit view không hoạt động với sol_o2m widget
**Lỗi:** Thêm cột vào Order Lines table nhưng không hiển thị

**Nguyên nhân:** Widget `sol_o2m` không sử dụng view tree thông thường

**Code SAI:**
```xml
<!-- Inherit view riêng biệt -->
<record id="view_order_line_tree_inherit" model="ir.ui.view">
    <field name="inherit_id" ref="sale.view_order_line_tree"/>
    ...
</record>
```

**Code ĐÚNG:**
```xml
<!-- Inherit trực tiếp vào sale order form -->
<record id="view_order_form_inherit_warranty" model="ir.ui.view">
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='order_line']//list//field[@name='price_subtotal']" position="after">
            <field name="product_warranty" string="Warranty" optional="show"/>
        </xpath>
    </field>
</record>
```

## 2. Lỗi Database

### 2.1 Column does not exist
**Lỗi:**
```
psycopg2.errors.UndefinedColumn: column sale_order.order_lines_cost does not exist
```

**Nguyên nhân:** Computed field có `store=True` nhưng database chưa có column

**Giải pháp:**
1. **Tạo migration script:**
```python
# migrations/1.0.x/post-migration.py
def migrate(cr, version):
    cr.execute("""
        ALTER TABLE sale_order 
        ADD COLUMN IF NOT EXISTS order_lines_cost NUMERIC
    """)
```

2. **Hoặc restart + reinstall module:**
   - Restart Odoo server
   - Apps → Uninstall module
   - Apps → Install module

### 2.2 Relation does not exist
**Lỗi:**
```
psycopg2.errors.UndefinedTable: relation "sale_order_cost_line" does not exist
```

**Nguyên nhân:** Model mới chưa được tạo table trong database

**Giải pháp:**
1. Restart Odoo server
2. Install/Upgrade module
3. Kiểm tra `__init__.py` có import model không

## 3. Lỗi Dependencies

### 3.1 Module not found
**Lỗi:**
```
No module named 'custom_product_info'
```

**Nguyên nhân:** Thiếu dependency trong `__manifest__.py`

**Code SAI:**
```python
'depends': ['sale_management'],
```

**Code ĐÚNG:**
```python
'depends': ['sale_management', 'custom_product_info'],
```

### 3.2 Field not found
**Lỗi:**
```
Field 'x_warranty_id' does not exist
```

**Nguyên nhân:** Dependency module chưa được install

**Giải pháp:**
1. Install `custom_product_info` module trước
2. Sau đó install `sale_order_cost_management`

## 4. Lỗi Computed Fields

### 4.1 Field not computed
**Lỗi:** Field luôn có giá trị 0 hoặc False

**Nguyên nhân:** Thiếu `@api.depends` hoặc depends sai

**Code SAI:**
```python
def _compute_total_cost(self):
    for line in self:
        line.total_cost = line.cost_price * line.product_uom_qty
```

**Code ĐÚNG:**
```python
@api.depends('cost_price', 'product_uom_qty')
def _compute_total_cost(self):
    for line in self:
        line.total_cost = line.cost_price * line.product_uom_qty
```

### 4.2 Infinite recursion
**Lỗi:**
```
RecursionError: maximum recursion depth exceeded
```

**Nguyên nhân:** Computed field depends vào chính nó

**Code SAI:**
```python
@api.depends('total_cost')  # SAI: depends vào chính nó
def _compute_total_cost(self):
    ...
```

**Code ĐÚNG:**
```python
@api.depends('cost_price', 'product_uom_qty')  # ĐÚNG: depends vào fields khác
def _compute_total_cost(self):
    ...
```

## 5. Lỗi Security

### 5.1 Access denied
**Lỗi:**
```
You do not have the rights to access this document
```

**Nguyên nhân:** Thiếu access rights trong `ir.model.access.csv`

**Giải pháp:**
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sale_order_cost_line_user,sale.order.cost.line.user,model_sale_order_cost_line,sales_team.group_sale_salesman,1,1,1,1
```

## 6. Lỗi Performance

### 6.1 Slow loading
**Lỗi:** View load chậm, timeout

**Nguyên nhân:** Computed field không có `store=True`

**Code SAI:**
```python
total_cost = fields.Float(compute='_compute_total_cost')  # Không store
```

**Code ĐÚNG:**
```python
total_cost = fields.Float(compute='_compute_total_cost', store=True)  # Có store
```

### 6.2 Too many records
**Lỗi:** List view hiển thị quá nhiều records

**Giải pháp:**
```xml
<list string="Order Lines" limit="200">
    ...
</list>
```

## 7. Lỗi User Interface

### 7.1 Column không hiển thị
**Lỗi:** Thêm field vào list view nhưng không thấy

**Nguyên nhân:** Column bị ẩn mặc định

**Giải pháp:**
```xml
<field name="product_warranty" string="Warranty" optional="show"/>
```

**Hoặc user tự enable:**
1. Click icon ⚙️ trong list view
2. Check vào column cần hiển thị

### 7.2 Field readonly không mong muốn
**Lỗi:** Field không thể edit

**Nguyên nhân:** Computed field mặc định readonly

**Giải pháp:**
```python
# Nếu muốn user có thể edit computed field
total_cost = fields.Float(compute='_compute_total_cost', store=True, readonly=False)
```

## 8. Lỗi Migration

### 8.1 Migration không chạy
**Lỗi:** Migration script không được execute

**Nguyên nhân:** 
- Tên thư mục migration sai
- Version không match

**Cấu trúc đúng:**
```
migrations/
├── 1.0.1/
│   └── post-migration.py
├── 1.0.5/
│   └── post-migration.py
```

**Version trong `__manifest__.py` phải match với thư mục migration**

### 8.2 SQL syntax error
**Lỗi:**
```
psycopg2.errors.SyntaxError: syntax error at or near "IF"
```

**Nguyên nhân:** PostgreSQL không hỗ trợ `ADD COLUMN IF NOT EXISTS` trong version cũ

**Code SAI:**
```python
cr.execute("ALTER TABLE sale_order ADD COLUMN IF NOT EXISTS order_lines_cost NUMERIC")
```

**Code ĐÚNG:**
```python
# Kiểm tra column tồn tại trước
cr.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='sale_order' AND column_name='order_lines_cost'
""")

if not cr.fetchone():
    cr.execute("ALTER TABLE sale_order ADD COLUMN order_lines_cost NUMERIC")
```

## 9. Debugging Tips

### 9.1 Kiểm tra XML ID
```bash
# Tìm XML ID trong source code
grep -r "view_order_line_form" addons/sale/

# Hoặc trong Odoo shell
self.env.ref('sale.view_order_line_form')
```

### 9.2 Kiểm tra Database Schema
```sql
-- Kiểm tra columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name='sale_order_line';

-- Kiểm tra data
SELECT product_warranty FROM sale_order_line LIMIT 5;
```

### 9.3 Debug Computed Fields
```python
# Thêm logging
import logging
_logger = logging.getLogger(__name__)

@api.depends('product_id')
def _compute_cost_price(self):
    for line in self:
        _logger.info(f"Computing cost for product: {line.product_id.name}")
        line.cost_price = line.product_id.standard_price
```

### 9.4 Kiểm tra View Inheritance
1. Developer mode → Edit View
2. Xem "Inherited Views" section
3. Kiểm tra XPath có đúng không

## 10. Prevention Best Practices

### 10.1 Luôn backup trước khi deploy
```bash
pg_dump odoo_db > backup_$(date +%Y%m%d).sql
```

### 10.2 Test trên development environment
- Không test trực tiếp trên production
- Sử dụng separate database cho development

### 10.3 Version control
- Commit thường xuyên
- Tăng version trong `__manifest__.py` khi có thay đổi
- Tạo migration script cho breaking changes

### 10.4 Code review
- Kiểm tra XML syntax
- Kiểm tra computed field dependencies
- Kiểm tra security access rights
- Test install/uninstall/upgrade

## Kết luận

Hầu hết các lỗi trong Odoo development đều có thể tránh được bằng cách:

1. **Hiểu rõ Odoo framework** (models, views, inheritance)
2. **Kiểm tra kỹ XML syntax** và references
3. **Test thoroughly** trước khi deploy
4. **Sử dụng migration scripts** cho database changes
5. **Follow best practices** về naming, security, performance

Khi gặp lỗi, hãy:
1. Đọc error message cẩn thận
2. Kiểm tra Odoo logs (`/var/log/odoo/odoo.log`)
3. Search documentation và community forums
4. Debug step by step
5. Backup trước khi thử fix
