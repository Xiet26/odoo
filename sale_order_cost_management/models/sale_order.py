# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cost_ids = fields.One2many('sale.order.cost', 'order_id', string='Costs')
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_total_cost', store=True)

    estimated_profit = fields.Monetary(string='Estimated Profit', compute='_compute_estimated_profit', store=True)

    @api.depends('cost_ids.amount')
    def _compute_total_cost(self):
        for order in self:
            order.total_cost = sum(order.cost_ids.mapped('amount'))

    @api.depends('amount_total', 'total_cost')
    def _compute_estimated_profit(self):
        for order in self:
            order.estimated_profit = order.amount_total - order.total_cost
