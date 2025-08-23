# -*- coding: utf-8 -*-

from odoo import models, fields

class SaleOrderCost(models.Model):
    _name = 'sale.order.cost'
    _description = 'Sale Order Cost'

    name = fields.Char(string='Cost Title', required=True)
    description = fields.Text(string='Description')
    amount = fields.Monetary(string='Amount', required=True)

    order_id = fields.Many2one('sale.order', string='Sales Order', ondelete='cascade', required=True)
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id', store=True, readonly=True)
