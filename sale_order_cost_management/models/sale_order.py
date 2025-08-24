# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cost_ids = fields.One2many('sale.order.cost', 'order_id', string='Costs')
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_total_cost', store=True)

    @api.depends('cost_ids.amount')
    def _compute_total_cost(self):
        for order in self:
            order.total_cost = sum(order.cost_ids.mapped('amount'))
