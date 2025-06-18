from odoo import models, fields, api

class SaleOrderCostLine(models.Model):
    _name = 'sale.order.cost.line'
    _description = 'Sale Order Cost Line'

    name = fields.Char(string='Số phiếu', required=True)
    description = fields.Text(string='Nội dung')
    user_id = fields.Many2one('res.users', string='Người tạo', default=lambda self: self.env.user)
    amount = fields.Monetary(string='Số tiền', required=True)
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối')
    ], string='Trạng thái', default='draft')
    order_id = fields.Many2one('sale.order', string='Đơn bán hàng', ondelete='cascade')
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id', store=True, readonly=True) 