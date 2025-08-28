# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cost_ids = fields.One2many('sale.order.cost', 'order_id', string='Costs')
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_total_cost', store=True)

    estimated_profit = fields.Monetary(string='Estimated Profit', compute='_compute_estimated_profit', store=True)

    # Cost from order lines
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

    @api.depends('total_cost', 'order_lines_cost')
    def _compute_total_all_costs(self):
        for order in self:
            order.total_all_costs = order.total_cost + order.order_lines_cost

    stock_location_info = fields.Html(string='Stock Location Info', compute='_compute_stock_location_info')

    @api.depends('amount_total', 'total_cost')
    def _compute_estimated_profit(self):
        for order in self:
            order.estimated_profit = order.amount_total - order.total_cost

    @api.depends('amount_total', 'total_all_costs')
    def _compute_final_profit(self):
        for order in self:
            order.final_profit = order.amount_total - order.total_all_costs

    @api.depends('order_line.product_id', 'warehouse_id')
    def _compute_stock_location_info(self):
        for order in self:
            if not order.warehouse_id or not order.order_line:
                order.stock_location_info = False
                continue

            location = order.warehouse_id.view_location_id
            child_locations = self.env['stock.location'].search([('id', 'child_of', location.id)])
            product_ids = order.order_line.product_id.ids

            quants = self.env['stock.quant'].search([
                ('product_id', 'in', product_ids),
                ('location_id', 'in', child_locations.ids),
                ('quantity', '>', 0)
            ])

            quant_data = {}
            for quant in quants:
                if quant.product_id.id not in quant_data:
                    quant_data[quant.product_id.id] = []
                quant_data[quant.product_id.id].append({
                    'location_id': quant.location_id.id,
                    'location': quant.location_id.display_name,
                    'quantity': quant.quantity
                })

            html = '<table class="table table-sm"><thead><tr><th>Product</th><th>Ordered Qty</th><th>Location</th><th>On Hand Qty</th></tr></thead><tbody>'
            for line in order.order_line.filtered(lambda l: l.display_type == False):
                locations_info = ''
                if line.product_id.id in quant_data:
                    for loc_data in quant_data[line.product_id.id]:
                        action_url = f"/web#id={loc_data['location_id']}&model=stock.location&view_type=form"
                        locations_info += f"<li><a href='{action_url}' target='_blank'>{loc_data['location']}</a>: <strong>{loc_data['quantity']}</strong></li>"

                if locations_info:
                    locations_info = f"<ul class='list-unstyled mb-0'>{locations_info}</ul>"
                else:
                    locations_info = '<span class="text-muted">Not Available</span>'

                html += f"<tr><td>{line.product_id.display_name}</td><td>{line.product_uom_qty}</td><td colspan='2'>{locations_info}</td></tr>"
            html += '</tbody></table>'
            order.stock_location_info = html
