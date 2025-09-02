# Sale Order Cost Management - Development Guide

## Tổng quan dự án

Module **Sale Order Cost Management** được phát triển để quản lý chi phí và tính toán lợi nhuận cho Sale Order trong Odoo. Module này bao gồm:

- Quản lý chi phí bổ sung cho Sale Order
- Tính toán cost và margin cho từng Order Line
- Hiển thị thông tin bảo hành sản phẩm
- Báo cáo tổng hợp chi phí và lợi nhuận
- Hiển thị thông tin vị trí hàng trong kho

## Cấu trúc Module

```
sale_order_cost_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── sale_order.py
│   ├── sale_order_line.py
│   └── sale_order_cost_line.py
├── views/
│   ├── sale_order_views.xml
│   ├── sale_order_line_views.xml
│   └── sale_order_cost_line_views.xml
├── migrations/
│   ├── 1.0.1/post-migration.py
│   ├── 1.0.5/post-migration.py
│   ├── 1.0.6/post-migration.py
│   └── 1.0.7/post-migration.py
├── security/
│   └── ir.model.access.csv
└── doc/
    └── DEVELOPMENT_GUIDE.md
```

## 1. Khai báo Module (__manifest__.py)

```python
{
    'name': 'Sale Order Cost Management',
    'version': '1.0.9',
    'summary': 'Manage costs and calculate profit margins for sale orders',
    'description': """
        This module allows you to:
        - Add additional costs to sale orders
        - Calculate cost price and margins for order lines
        - Track profitability of sales
        - Display product warranty information
        - Show stock location information
    """,
    'depends': ['sale_management', 'custom_product_info'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_cost_line_views.xml',
        'views/sale_order_views.xml',
        'views/sale_order_line_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
```

### Lưu ý quan trọng:
- **depends**: Phải khai báo đầy đủ dependencies
- **data**: Thứ tự file quan trọng (security trước, views sau)
- **version**: Tăng version khi có thay đổi để trigger update

## 2. Models

### 2.1 Sale Order Cost Line (sale_order_cost_line.py)

```python
from odoo import models, fields, api

class SaleOrderCostLine(models.Model):
    _name = 'sale.order.cost.line'
    _description = 'Sale Order Cost Line'

    name = fields.Char(string='Description', required=True)
    description = fields.Text(string='Detailed Description')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    amount = fields.Float(string='Amount', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced')
    ], string='State', default='draft')
    order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')
```

### 2.2 Sale Order (sale_order.py)

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # One2many relationship
    cost_ids = fields.One2many('sale.order.cost.line', 'order_id', string='Additional Costs')
    
    # Computed fields với store=True
    total_cost = fields.Monetary(string='Total Additional Cost', compute='_compute_total_cost', store=True)
    order_lines_cost = fields.Monetary(string='Order Lines Cost', compute='_compute_order_lines_cost', store=True)
    total_all_costs = fields.Monetary(string='Total All Costs', compute='_compute_total_all_costs', store=True)
    final_profit = fields.Monetary(string='Final Profit', compute='_compute_final_profit', store=True)

    @api.depends('cost_ids.amount')
    def _compute_total_cost(self):
        for order in self:
            order.total_cost = sum(order.cost_ids.mapped('amount'))

    @api.depends('order_line.total_cost')
    def _compute_order_lines_cost(self):
        for order in self:
            order.order_lines_cost = sum(order.order_line.mapped('total_cost'))
```

### 2.3 Sale Order Line (sale_order_line.py)

```python
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Cost fields
    cost_price = fields.Float(string='Cost Price', compute='_compute_cost_price', store=True, readonly=True)
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True, readonly=True)
    line_margin = fields.Float(string='Margin', compute='_compute_line_margin', store=True, readonly=True)
    
    # Warranty field từ custom_product_info
    product_warranty = fields.Char(string='Warranty', compute='_compute_product_warranty', store=True, readonly=True)

    @api.depends('product_id')
    def _compute_cost_price(self):
        for line in self:
            if line.product_id:
                line.cost_price = line.product_id.standard_price
            else:
                line.cost_price = 0.0

    @api.depends('product_id', 'product_id.x_warranty_id')
    def _compute_product_warranty(self):
        for line in self:
            if line.product_id and line.product_id.x_warranty_id:
                warranty = line.product_id.x_warranty_id
                line.product_warranty = f"{warranty.name} ({warranty.duration} months)"
            else:
                line.product_warranty = "No warranty"
```

## 3. Views

### 3.1 Các loại View trong Odoo

#### Tree View (List View)
```xml
<record id="sale_order_line_view_tree_costing" model="ir.ui.view">
    <field name="name">sale.order.line.tree.costing</field>
    <field name="model">sale.order.line</field>
    <field name="type">list</field>
    <field name="arch" type="xml">
        <list string="Order Lines Costing" create="false" edit="false">
            <field name="product_id"/>
            <field name="cost_price" string="Cost Price"/>
            <field name="product_warranty" string="Warranty"/>
        </list>
    </field>
</record>
```

#### Form View
```xml
<record id="view_order_line_form_inherit_cost" model="ir.ui.view">
    <field name="name">sale.order.line.form.inherit.cost</field>
    <field name="model">sale.order.line</field>
    <field name="inherit_id" ref="sale.sale_order_line_view_form_readonly"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='price_unit']" position="after">
            <field name="cost_price" string="Cost Price"/>
            <field name="product_warranty" string="Warranty"/>
        </xpath>
    </field>
</record>
```

### 3.2 Inherit Views

#### Thêm Tab mới vào Sale Order
```xml
<record id="view_order_form_inherit_costs" model="ir.ui.view">
    <field name="name">sale.order.form.inherit.costs</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <xpath expr="//notebook" position="inside">
            <page string="Costs" name="order_costs">
                <field name="cost_ids"/>
                <group class="oe_subtotal_footer oe_right">
                    <field name="total_cost"/>
                </group>
            </page>
        </xpath>
    </field>
</record>
```

#### Thêm cột vào Order Lines table
```xml
<record id="view_order_form_inherit_warranty" model="ir.ui.view">
    <field name="name">sale.order.form.inherit.warranty</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='order_line']//list//field[@name='price_subtotal']" position="after">
            <field name="product_warranty" string="Warranty" optional="show"/>
        </xpath>
    </field>
</record>
```

## 4. Security (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sale_order_cost_line_user,sale.order.cost.line.user,model_sale_order_cost_line,sales_team.group_sale_salesman,1,1,1,1
access_sale_order_cost_line_manager,sale.order.cost.line.manager,model_sale_order_cost_line,sales_team.group_sale_manager,1,1,1,1
```

## 5. Migration Scripts

### Tại sao cần Migration?
- Khi thêm field mới vào model, database cần được update
- Odoo không tự động tạo column cho computed fields có store=True
- Migration script đảm bảo database schema đúng

### Ví dụ Migration Script (migrations/1.0.7/post-migration.py)
```python
def migrate(cr, version):
    """Migration script to add missing columns"""

    # Add columns to sale_order table
    columns_to_add_order = [
        ('order_lines_cost', 'NUMERIC'),
        ('total_all_costs', 'NUMERIC'),
        ('final_profit', 'NUMERIC')
    ]

    for column_name, column_type in columns_to_add_order:
        cr.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='sale_order' AND column_name=%s
        """, (column_name,))

        if not cr.fetchone():
            cr.execute(f"""
                ALTER TABLE sale_order
                ADD COLUMN {column_name} {column_type}
            """)
```

## 6. Các lỗi thường gặp và cách khắc phục

### 6.1 Lỗi XML View

#### Lỗi: "Label tag must contain a 'for'"
```xml
<!-- SAI -->
<label string="Costs Breakdown:"/>

<!-- ĐÚNG -->
<span class="o_form_label">Costs Breakdown:</span>
<!-- HOẶC -->
<label for="field_name" string="Label Text"/>
```

#### Lỗi: "View reference not found"
```xml
<!-- SAI -->
<field name="inherit_id" ref="sale.view_order_line_form"/>

<!-- ĐÚNG - Kiểm tra XML ID có tồn tại -->
<field name="inherit_id" ref="sale.sale_order_line_view_form_readonly"/>
```

### 6.2 Lỗi Database

#### Lỗi: "column does not exist"
- **Nguyên nhân**: Computed field có store=True nhưng chưa có migration
- **Giải pháp**: Tạo migration script hoặc restart + reinstall module

#### Lỗi: "relation does not exist"
- **Nguyên nhân**: Model mới chưa được tạo table
- **Giải pháp**: Restart Odoo server và install lại module

### 6.3 Lỗi Dependencies

#### Lỗi: "Module not found"
```python
# SAI - Thiếu dependency
'depends': ['sale_management'],

# ĐÚNG - Đầy đủ dependencies
'depends': ['sale_management', 'custom_product_info'],
```

### 6.4 Lỗi Computed Fields

#### Lỗi: "Field not computed"
```python
# SAI - Thiếu @api.depends
def _compute_total_cost(self):
    for line in self:
        line.total_cost = line.cost_price * line.product_uom_qty

# ĐÚNG - Có @api.depends
@api.depends('cost_price', 'product_uom_qty')
def _compute_total_cost(self):
    for line in self:
        line.total_cost = line.cost_price * line.product_uom_qty
```

### 6.5 Lỗi Odoo 17+ View Syntax

#### Lỗi: "attrs" and "states" attributes are no longer used
**Nguyên nhân**: Từ Odoo 17.0, syntax `attrs` và `states` đã bị deprecated

**Code SAI (Odoo 16 syntax):**
```xml
<button name="action_export_xlsx"
        string="Export Excel"
        type="object"
        attrs="{'invisible': [('state', 'in', ['draft', 'cancel'])]}"/>
```

**Code ĐÚNG (Odoo 17+ syntax):**
```xml
<button name="action_export_xlsx"
        string="Export Excel"
        type="object"
        invisible="state in ['draft', 'cancel']"/>
```

**Các thay đổi chính:**
- `attrs="{'invisible': [...]}"` → `invisible="..."`
- `attrs="{'readonly': [...]}"` → `readonly="..."`
- `attrs="{'required': [...]}"` → `required="..."`
- Domain syntax đơn giản hơn: `[('field', '=', 'value')]` → `field == 'value'`

**Ví dụ khác:**
```xml
<!-- SAI -->
<field name="amount" attrs="{'readonly': [('state', '=', 'done')]}"/>

<!-- ĐÚNG -->
<field name="amount" readonly="state == 'done'"/>
```

## 7. Best Practices

### 7.1 Naming Convention
- **Model**: `snake_case` (sale_order_cost_line)
- **Field**: `snake_case` (total_cost, product_warranty)
- **XML ID**: `snake_case` (view_order_form_inherit_costs)
- **Method**: `snake_case` với prefix (_compute_, _onchange_)

### 7.2 Performance
- Sử dụng `store=True` cho computed fields được query thường xuyên
- Sử dụng `@api.depends()` chính xác để tránh recompute không cần thiết
- Limit số lượng record trong list view: `limit="200"`

### 7.3 User Experience
- Sử dụng `optional="show"` cho columns không bắt buộc
- Sử dụng `readonly="True"` cho computed fields
- Thêm `string` attribute để có label rõ ràng

### 7.4 Odoo Version Compatibility
- **Odoo 17+**: Sử dụng `invisible="condition"` thay vì `attrs="{'invisible': [...]}"`
- **Domain syntax**: `field == 'value'` thay vì `[('field', '=', 'value')]`
- **Multiple conditions**: `field1 == 'value' and field2 != 'other'`
- **In operator**: `field in ['val1', 'val2']` thay vì `[('field', 'in', ['val1', 'val2'])]`

### 7.4 Security
- Luôn định nghĩa access rights trong ir.model.access.csv
- Sử dụng groups phù hợp (sales_team.group_sale_salesman)
- Kiểm tra permissions cho các operations (read, write, create, unlink)

## 8. Testing và Debugging

### 8.1 Kiểm tra Module
1. **Install**: Apps → Search module → Install
2. **Update**: Apps → Find module → Upgrade
3. **Uninstall/Reinstall**: Nếu có lỗi database nghiêm trọng

### 8.2 Debug Views
1. **Developer mode**: Settings → Activate Developer Mode
2. **Edit View**: Click "Edit View" trên form
3. **View inheritance**: Kiểm tra view hierarchy

### 8.3 Debug Database
```sql
-- Kiểm tra columns có tồn tại
SELECT column_name FROM information_schema.columns
WHERE table_name='sale_order_line';

-- Kiểm tra data
SELECT product_warranty FROM sale_order_line LIMIT 5;
```

## 9. Deployment

### 9.1 Version Control
- Tăng version trong `__manifest__.py` khi có thay đổi
- Tạo migration script cho version mới nếu có thay đổi database
- Commit code với message rõ ràng

### 9.2 Production Deployment
1. **Backup database** trước khi deploy
2. **Test trên staging** environment trước
3. **Update module** trên production: `odoo -u module_name`
4. **Restart server** nếu cần thiết

## 10. Kết luận

Module Sale Order Cost Management đã được phát triển thành công với các tính năng:

✅ **Quản lý chi phí bổ sung** cho Sale Order
✅ **Tính toán cost và margin** cho từng Order Line
✅ **Hiển thị thông tin bảo hành** từ custom_product_info
✅ **Báo cáo tổng hợp** chi phí và lợi nhuận
✅ **Hiển thị vị trí hàng** trong kho
✅ **Export Excel chuyên nghiệp** với 4 sheets chi tiết
✅ **Export Word phiếu bảo hành** với fallback HTML
✅ **Mark as Sent button** không gửi email
✅ **Migration scripts** để đảm bảo database consistency
✅ **Proper view inheritance** cho Order Lines table
✅ **Odoo 17+ compatibility** với modern view syntax

### Tính năng Export & Actions (v1.2.1):
- **Excel Export**: Multi-sheet với Order Summary, Lines, Costs, Commercial Terms
- **Word Export**: Phiếu bảo hành professional với smart fallback
- **Mark as Sent**: Button đổi trạng thái không gửi email
- **Professional formatting**: Colors, borders, currency formatting
- **Smart styling**: Profit/loss color coding, auto-fit columns
- **Security compliant**: Permission checks và error handling

Module này có thể được mở rộng thêm với các tính năng như:
- Dashboard analytics
- Email notifications
- Workflow approval cho costs
- Integration với accounting module
- Batch export multiple orders
```
