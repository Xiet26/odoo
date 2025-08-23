from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cost_line_ids = fields.One2many('sale.order.cost.line', 'order_id', string='Chi phí đơn hàng')
    internal_note = fields.Text(string='Ghi chú nội bộ')