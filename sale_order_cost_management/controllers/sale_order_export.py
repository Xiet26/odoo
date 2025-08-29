# -*- coding: utf-8 -*-

import io
import logging
from datetime import datetime

from odoo import http
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError, UserError
from odoo.tools.misc import xlsxwriter

_logger = logging.getLogger(__name__)


class SaleOrderExportController(http.Controller):

    @http.route('/sale_order/export_xlsx/<int:order_id>', type='http', auth='user')
    def export_order_xlsx(self, order_id, **kwargs):
        """Export sale order data to Excel file with multiple sheets"""
        try:
            # Get sale order and check permissions
            order = request.env['sale.order'].browse(order_id)
            if not order.exists():
                raise UserError("Sale Order not found")
            
            # Check read access
            order.check_access_rights('read')
            order.check_access_rule('read')
            
            # Generate Excel file
            excel_data = self._generate_excel_file(order)
            
            # Prepare filename
            filename = f"{order.name.replace('/', '_')}_Export_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
            # Return file response
            return request.make_response(
                excel_data,
                headers=[
                    ('Content-Disposition', content_disposition(filename)),
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Length', len(excel_data))
                ]
            )
            
        except AccessError:
            return request.render('http_routing.http_error', {
                'status_code': 403,
                'status_message': 'Access Denied'
            })
        except Exception as e:
            _logger.exception("Error exporting sale order to Excel: %s", str(e))
            return request.render('http_routing.http_error', {
                'status_code': 500,
                'status_message': 'Internal Server Error'
            })

    def _generate_excel_file(self, order):
        """Generate Excel file with multiple sheets"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Define styles
        styles = self._get_excel_styles(workbook)
        
        # Create sheets
        self._create_order_summary_sheet(workbook, order, styles)
        self._create_order_lines_sheet(workbook, order, styles)
        self._create_additional_costs_sheet(workbook, order, styles)
        
        workbook.close()
        output.seek(0)
        return output.read()

    def _get_excel_styles(self, workbook):
        """Define Excel styles"""
        return {
            'header': workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True
            }),
            'subheader': workbook.add_format({
                'bold': True,
                'bg_color': '#D9E2F3',
                'border': 1,
                'align': 'left',
                'font_size': 12
            }),
            'title': workbook.add_format({
                'bold': True,
                'font_size': 16,
                'bg_color': '#2F5597',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            }),
            'currency': workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
                'align': 'right'
            }),
            'percentage': workbook.add_format({
                'num_format': '0.00%',
                'border': 1,
                'align': 'right'
            }),
            'normal': workbook.add_format({
                'border': 1,
                'valign': 'top',
                'text_wrap': True
            }),
            'bold': workbook.add_format({
                'bold': True,
                'border': 1
            }),
            'total': workbook.add_format({
                'bold': True,
                'bg_color': '#F2F2F2',
                'num_format': '#,##0.00',
                'border': 2,
                'top': 2
            }),
            'date': workbook.add_format({
                'num_format': 'yyyy-mm-dd',
                'border': 1
            }),
            'profit_positive': workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
                'font_color': '#008000',
                'bold': True
            }),
            'profit_negative': workbook.add_format({
                'num_format': '#,##0.00',
                'border': 1,
                'font_color': '#FF0000',
                'bold': True
            })
        }

    def _create_order_summary_sheet(self, workbook, order, styles):
        """Create Order Summary sheet"""
        worksheet = workbook.add_worksheet('Order Summary')

        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:C', 15)

        row = 0

        # Title
        worksheet.merge_range(row, 0, row, 2, f'SALE ORDER EXPORT - {order.name}', styles['title'])
        row += 2

        # Order Information
        worksheet.merge_range(row, 0, row, 2, 'ORDER INFORMATION', styles['subheader'])
        row += 1

        order_info = [
            ('Order Number:', order.name),
            ('Customer:', order.partner_id.name),
            ('Order Date:', order.date_order.strftime('%Y-%m-%d') if order.date_order else ''),
            ('Status:', dict(order._fields['state'].selection).get(order.state, order.state)),
            ('Salesperson:', order.user_id.name if order.user_id else ''),
            ('Company:', order.company_id.name),
            ('Currency:', order.currency_id.name if order.currency_id else ''),
        ]

        for label, value in order_info:
            worksheet.write(row, 0, label, styles['bold'])
            if label == 'Order Date:' and value:
                worksheet.write(row, 1, value, styles['date'])
            else:
                worksheet.write(row, 1, value, styles['normal'])
            row += 1

        row += 1

        # Financial Summary
        worksheet.merge_range(row, 0, row, 2, 'FINANCIAL SUMMARY', styles['subheader'])
        row += 1

        financial_data = [
            ('Total Revenue:', order.amount_total, 'currency'),
            ('Product Costs:', order.order_lines_cost, 'currency'),
            ('Additional Costs:', order.total_cost, 'currency'),
            ('Total All Costs:', order.total_all_costs, 'currency'),
        ]

        for label, value, format_type in financial_data:
            worksheet.write(row, 0, label, styles['bold'])
            worksheet.write(row, 1, value, styles[format_type])
            row += 1

        # Final Profit with color coding
        profit_style = styles['profit_positive'] if order.final_profit >= 0 else styles['profit_negative']
        worksheet.write(row, 0, 'Final Profit:', styles['bold'])
        worksheet.write(row, 1, order.final_profit, profit_style)
        row += 1

        # Profit Margin
        if order.amount_total:
            margin_pct = (order.final_profit / order.amount_total) if order.amount_total else 0
            margin_style = styles['profit_positive'] if margin_pct >= 0 else styles['profit_negative']
            worksheet.write(row, 0, 'Profit Margin %:', styles['bold'])
            worksheet.write(row, 1, margin_pct, styles['percentage'])
            row += 2

        # Order Statistics
        worksheet.merge_range(row, 0, row, 2, 'ORDER STATISTICS', styles['subheader'])
        row += 1

        stats_data = [
            ('Number of Lines:', len(order.order_line)),
            ('Total Quantity:', sum(order.order_line.mapped('product_uom_qty'))),
            ('Number of Additional Costs:', len(order.cost_ids)),
        ]

        for label, value in stats_data:
            worksheet.write(row, 0, label, styles['bold'])
            worksheet.write(row, 1, value, styles['normal'])
            row += 1

    def _create_order_lines_sheet(self, workbook, order, styles):
        """Create Order Lines Detail sheet"""
        worksheet = workbook.add_worksheet('Order Lines')
        
        # Headers
        headers = [
            'Product Code', 'Product Name', 'Quantity', 'UoM', 
            'Unit Price', 'Cost Price', 'Total Cost', 'Subtotal', 
            'Margin', 'Margin %', 'Warranty'
        ]
        
        # Set column widths
        col_widths = [15, 30, 10, 8, 12, 12, 12, 12, 12, 10, 20]
        for i, width in enumerate(col_widths):
            worksheet.set_column(i, i, width)
        
        # Write headers
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, styles['header'])
        
        # Write data
        row = 1
        total_subtotal = 0
        total_cost = 0
        total_margin = 0
        
        for line in order.order_line:
            worksheet.write(row, 0, line.product_id.default_code or '', styles['normal'])
            worksheet.write(row, 1, line.product_id.name or '', styles['normal'])
            worksheet.write(row, 2, line.product_uom_qty, styles['normal'])
            worksheet.write(row, 3, line.product_uom.name if line.product_uom else '', styles['normal'])
            worksheet.write(row, 4, line.price_unit, styles['currency'])
            worksheet.write(row, 5, line.cost_price, styles['currency'])
            worksheet.write(row, 6, line.total_cost, styles['currency'])
            worksheet.write(row, 7, line.price_subtotal, styles['currency'])
            worksheet.write(row, 8, line.line_margin, styles['currency'])
            
            # Margin percentage
            margin_pct = (line.line_margin / line.price_subtotal) * 100 if line.price_subtotal else 0
            worksheet.write(row, 9, margin_pct / 100, styles['percentage'])
            
            worksheet.write(row, 10, line.product_warranty or '', styles['normal'])
            
            total_subtotal += line.price_subtotal
            total_cost += line.total_cost
            total_margin += line.line_margin
            row += 1
        
        # Totals row
        worksheet.write(row, 0, 'TOTAL', styles['total'])
        for col in range(1, 6):
            worksheet.write(row, col, '', styles['total'])
        worksheet.write(row, 6, total_cost, styles['total'])
        worksheet.write(row, 7, total_subtotal, styles['total'])
        worksheet.write(row, 8, total_margin, styles['total'])
        
        # Total margin percentage
        total_margin_pct = (total_margin / total_subtotal) * 100 if total_subtotal else 0
        worksheet.write(row, 9, total_margin_pct / 100, styles['total'])
        worksheet.write(row, 10, '', styles['total'])

    def _create_additional_costs_sheet(self, workbook, order, styles):
        """Create Additional Costs sheet"""
        worksheet = workbook.add_worksheet('Additional Costs')
        
        # Headers
        headers = ['Cost Code', 'Description', 'Partner', 'Amount', 'Status', 'Responsible']
        
        # Set column widths
        col_widths = [15, 40, 25, 15, 15, 20]
        for i, width in enumerate(col_widths):
            worksheet.set_column(i, i, width)
        
        # Write headers
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, styles['header'])
        
        # Write data
        row = 1
        total_amount = 0
        
        for cost in order.cost_ids:
            worksheet.write(row, 0, cost.name or '', styles['normal'])
            worksheet.write(row, 1, cost.description or '', styles['normal'])
            worksheet.write(row, 2, cost.partner_id.name if cost.partner_id else '', styles['normal'])
            worksheet.write(row, 3, cost.amount, styles['currency'])
            worksheet.write(row, 4, dict(cost._fields['state'].selection).get(cost.state, cost.state), styles['normal'])
            worksheet.write(row, 5, cost.user_id.name if cost.user_id else '', styles['normal'])
            
            total_amount += cost.amount
            row += 1
        
        # Total row
        if order.cost_ids:
            worksheet.write(row, 0, 'TOTAL', styles['total'])
            for col in range(1, 3):
                worksheet.write(row, col, '', styles['total'])
            worksheet.write(row, 3, total_amount, styles['total'])
            for col in range(4, 6):
                worksheet.write(row, col, '', styles['total'])
