# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_cost = fields.Float(
        string='Cost',
        compute='_compute_product_cost',
        digits='Product Price',
        store=True,
        readonly=True
    )

    @api.depends('product_id')
    def _compute_product_cost(self):
        for line in self:
            line.product_cost = line.product_id.standard_price
