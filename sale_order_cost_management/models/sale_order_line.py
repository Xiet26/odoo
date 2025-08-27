# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Fallback cost field if sale_margin is not installed
    cost_price = fields.Float(
        string='Cost Price',
        compute='_compute_cost_price',
        digits='Product Price',
        store=True,
        readonly=True
    )

    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_cost',
        digits='Product Price',
        store=True,
        readonly=True
    )

    line_margin = fields.Float(
        string='Margin',
        compute='_compute_line_margin',
        digits='Product Price',
        store=True,
        readonly=True
    )

    @api.depends('product_id')
    def _compute_cost_price(self):
        for line in self:
            if line.product_id:
                line.cost_price = line.product_id.standard_price
            else:
                line.cost_price = 0.0

    @api.depends('cost_price', 'product_uom_qty')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.cost_price * line.product_uom_qty

    @api.depends('price_subtotal', 'total_cost')
    def _compute_line_margin(self):
        for line in self:
            line.line_margin = line.price_subtotal - line.total_cost
