# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrderCost(models.Model):
    _name = 'sale.order.cost'
    _description = 'Sale Payment Voucher'

    name = fields.Char(string='Mã', required=True, readonly=True, copy=False, default='New')
    description = fields.Text(string='Nội dung')
    user_id = fields.Many2one('res.users', string='Người tạo', default=lambda self: self.env.user, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Đối tác')
    amount = fields.Monetary(string='Số tiền', required=True)
    state = fields.Selection([
        ('draft', 'Đang chờ TT'),
        ('paid', 'Đã thanh toán')
    ], string='Tình trạng', default='draft', required=True)

    order_id = fields.Many2one('sale.order', string='Sales Order', ondelete='cascade', required=True)
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id', store=True, readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.cost') or _('New')
        return super().create(vals_list)
