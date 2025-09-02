# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cost_ids = fields.One2many('sale.order.cost', 'order_id', string='Costs')
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_total_cost', store=True)

    estimated_profit = fields.Monetary(string='Estimated Profit', compute='_compute_estimated_profit', store=True)

    # Cost from order lines
    order_lines_cost = fields.Monetary(string='Order Lines Cost', compute='_compute_order_lines_cost', store=True)
    total_all_costs = fields.Monetary(string='Total All Costs', compute='_compute_total_all_costs', store=True)
    final_profit = fields.Monetary(string='Final Profit', compute='_compute_final_profit', store=True)

    # Commercial terms
    commercial_terms = fields.Html(
        string='Điều khoản thương mại',
        help='Các điều khoản và điều kiện thương mại cho đơn hàng này',
        default=lambda self: self._get_default_commercial_terms()
    )

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

    def _get_default_commercial_terms(self):
        """Get default commercial terms content"""
        return """
        <h3>ĐIỀU KHOẢN THƯƠNG MẠI</h3>

        <h4>1. ĐIỀU KIỆN THANH TOÁN</h4>
        <ul>
            <li><strong>Phương thức thanh toán:</strong> Chuyển khoản ngân hàng</li>
            <li><strong>Thời hạn thanh toán:</strong> 30 ngày kể từ ngày xuất hóa đơn</li>
            <li><strong>Tạm ứng:</strong> 50% giá trị đơn hàng trước khi sản xuất</li>
        </ul>

        <h4>2. ĐIỀU KIỆN GIAO HÀNG</h4>
        <ul>
            <li><strong>Thời gian giao hàng:</strong> 15-20 ngày làm việc kể từ khi nhận đặt cọc</li>
            <li><strong>Địa điểm giao hàng:</strong> Theo địa chỉ khách hàng cung cấp</li>
            <li><strong>Phí vận chuyển:</strong> Miễn phí trong nội thành, tính phí cho các tỉnh khác</li>
        </ul>

        <h4>3. BẢO HÀNH & HỖ TRỢ</h4>
        <ul>
            <li><strong>Thời gian bảo hành:</strong> 12 tháng kể từ ngày giao hàng</li>
            <li><strong>Phạm vi bảo hành:</strong> Lỗi do nhà sản xuất, không bao gồm hư hỏng do sử dụng sai cách</li>
            <li><strong>Hỗ trợ kỹ thuật:</strong> 24/7 qua hotline và email</li>
        </ul>

        <h4>4. ĐIỀU KHOẢN KHÁC</h4>
        <ul>
            <li><strong>Hủy đơn hàng:</strong> Phải thông báo trước 48h, có thể áp dụng phí hủy</li>
            <li><strong>Thay đổi đơn hàng:</strong> Chỉ được phép trước khi bắt đầu sản xuất</li>
            <li><strong>Tranh chấp:</strong> Được giải quyết thông qua thương lượng, hòa giải</li>
        </ul>

        <p><em>Điều khoản này có hiệu lực kể từ ngày ký hợp đồng và có thể được điều chỉnh theo thỏa thuận của hai bên.</em></p>
        """

    def action_export_xlsx(self):
        """Export sale order to Excel file"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sale_order/export_xlsx/{self.id}',
            'target': 'self',
        }

    def action_export_warranty_docx(self):
        """Export warranty document to Word file"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/sale_order/export_warranty_docx/{self.id}',
            'target': 'self',
        }

    def action_mark_as_sent(self):
        """Mark quotation as sent without sending email"""
        if any(order.state != 'draft' for order in self):
            raise UserError(_("Only draft orders can be marked as sent directly."))

        for order in self:
            order.message_subscribe(partner_ids=order.partner_id.ids)
            # Post a message to track the action
            order.message_post(
                body=_("Quotation marked as sent manually (without email)."),
                message_type='notification',
                subtype_xmlid='mail.mt_note'
            )

        self.write({'state': 'sent'})
