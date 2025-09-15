# -*- coding: utf-8 -*-

import io
import logging
from datetime import datetime, timedelta

from odoo import http
from odoo.http import request, content_disposition
from odoo.exceptions import AccessError, UserError
from odoo.tools.misc import xlsxwriter

try:
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.shared import OxmlElement, qn
    from docx.enum.table import WD_TABLE_ALIGNMENT
    import base64
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

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

    @http.route('/sale_order/export_warranty_docx/<int:order_id>', type='http', auth='user')
    def export_warranty_docx(self, order_id, **kwargs):
        """Export warranty document to Word file"""
        try:
            # Get sale order and check permissions
            order = request.env['sale.order'].browse(order_id)
            if not order.exists():
                return request.not_found()

            # Check read access
            order.check_access_rights('read')
            order.check_access_rule('read')

            # Generate Word file (HTML format that Word can open)
            if DOCX_AVAILABLE:
                word_data = self._generate_warranty_document_docx(order)
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                extension = '.docx'
            else:
                word_data = self._generate_warranty_document_html(order)
                content_type = 'application/msword'
                extension = '.doc'

            # Prepare filename
            filename = f"Phieu_Bao_Hanh_{order.name.replace('/', '_')}_{datetime.now().strftime('%Y%m%d')}{extension}"

            # Return file response
            return request.make_response(
                word_data,
                headers=[
                    ('Content-Disposition', content_disposition(filename)),
                    ('Content-Type', content_type),
                    ('Content-Length', len(word_data))
                ]
            )

        except AccessError:
            return request.make_response(
                "Access Denied",
                status=403,
                headers=[('Content-Type', 'text/plain')]
            )
        except Exception as e:
            _logger.exception("Error exporting warranty document: %s", str(e))
            return request.make_response(
                f"Error: {str(e)}",
                status=500,
                headers=[('Content-Type', 'text/plain')]
            )

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
        self._create_commercial_terms_sheet(workbook, order, styles)
        
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

    def _create_commercial_terms_sheet(self, workbook, order, styles):
        """Create Commercial Terms sheet"""
        worksheet = workbook.add_worksheet('Commercial Terms')

        # Set column widths
        worksheet.set_column('A:A', 80)

        row = 0

        # Title
        worksheet.write(row, 0, f'ĐIỀU KHOẢN THƯƠNG MẠI - {order.name}', styles['title'])
        row += 2

        # Commercial terms content
        if order.commercial_terms:
            # Convert HTML to plain text for Excel
            import re
            from html import unescape

            # Remove HTML tags and convert to plain text
            text_content = re.sub('<[^<]+?>', '', order.commercial_terms)
            text_content = unescape(text_content)

            # Split by lines and write each line
            lines = text_content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    # Check if it's a header (contains numbers like "1.", "2.", etc.)
                    if re.match(r'^\d+\.', line) or line.isupper():
                        worksheet.write(row, 0, line, styles['subheader'])
                    else:
                        worksheet.write(row, 0, line, styles['normal'])
                    row += 1
        else:
            worksheet.write(row, 0, 'Chưa có điều khoản thương mại được thiết lập.', styles['normal'])

        # Set row height for better readability
        for i in range(row):
            worksheet.set_row(i, 20)

    def _generate_warranty_document_html(self, order):
        """Generate warranty document as HTML (Word-compatible)"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Phiếu Bảo Hành - {order.name}</title>
            <style>
                body {{
                    font-family: 'Times New Roman', serif;
                    font-size: 12pt;
                    line-height: 1.5;
                    margin: 1in;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .title {{
                    font-size: 18pt;
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                .company-info {{
                    font-size: 11pt;
                    margin-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f0f0f0;
                    font-weight: bold;
                    text-align: center;
                }}
                .section-title {{
                    font-size: 14pt;
                    font-weight: bold;
                    text-align: center;
                    margin: 20px 0 10px 0;
                }}
                .terms {{
                    margin: 10px 0;
                }}
                .signature-table {{
                    margin-top: 40px;
                }}
                .signature-table td {{
                    border: none;
                    text-align: center;
                    padding: 20px;
                }}
                @media print {{
                    body {{ margin: 0.5in; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">PHIẾU BẢO HÀNH SẢN PHẨM</div>
                <div class="company-info">
                    <strong>{order.company_id.name}</strong><br>
        """

        if order.company_id.street:
            html_content += f"Địa chỉ: {order.company_id.street}<br>"
        if order.company_id.phone:
            html_content += f"Điện thoại: {order.company_id.phone}<br>"
        if order.company_id.email:
            html_content += f"Email: {order.company_id.email}<br>"

        html_content += f"""
                </div>
            </div>

            <table>
                <tr><td><strong>Số đơn hàng:</strong></td><td>{order.name}</td></tr>
                <tr><td><strong>Khách hàng:</strong></td><td>{order.partner_id.name}</td></tr>
                <tr><td><strong>Ngày đặt hàng:</strong></td><td>{order.date_order.strftime('%d/%m/%Y') if order.date_order else ''}</td></tr>
                <tr><td><strong>Người bán:</strong></td><td>{order.user_id.name if order.user_id else ''}</td></tr>
                <tr><td><strong>Tổng giá trị:</strong></td><td>{order.amount_total:,.0f} {order.currency_id.name}</td></tr>
                <tr><td><strong>Ngày lập phiếu:</strong></td><td>{datetime.now().strftime('%d/%m/%Y')}</td></tr>
            </table>

            <div class="section-title">DANH SÁCH SẢN PHẨM BẢO HÀNH</div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 5%">STT</th>
                        <th style="width: 40%">Sản phẩm</th>
                        <th style="width: 10%">Số lượng</th>
                        <th style="width: 20%">Thời gian BH</th>
                        <th style="width: 15%">Hết hạn BH</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx, line in enumerate(order.order_line.filtered(lambda l: not l.display_type), 1):
            warranty_text = line.product_warranty or 'Không có thông tin'

            # Calculate warranty expiry
            expiry_text = 'N/A'
            if order.date_order:
                warranty_months = 12  # Default
                if 'month' in warranty_text.lower():
                    try:
                        import re
                        months_match = re.search(r'(\d+)', warranty_text)
                        if months_match:
                            warranty_months = int(months_match.group(1))
                    except:
                        pass

                expiry_date = order.date_order + timedelta(days=warranty_months * 30)
                expiry_text = expiry_date.strftime('%d/%m/%Y')

            html_content += f"""
                    <tr>
                        <td style="text-align: center">{idx}</td>
                        <td>{line.product_id.name or ''}</td>
                        <td style="text-align: center">{line.product_uom_qty:g}</td>
                        <td style="text-align: center">{warranty_text}</td>
                        <td style="text-align: center">{expiry_text}</td>
                    </tr>
            """

        html_content += f"""
                </tbody>
            </table>

            <div class="section-title">ĐIỀU KIỆN BẢO HÀNH</div>

            <div class="terms">
                <p><strong>1.</strong> Sản phẩm được bảo hành miễn phí trong thời gian quy định kể từ ngày mua.</p>
                <p><strong>2.</strong> Bảo hành không áp dụng cho các trường hợp:</p>
                <ul>
                    <li>Hư hỏng do sử dụng sai cách, va đập, rơi vỡ</li>
                    <li>Hư hỏng do thiên tai, hỏa hoạn, ngập nước</li>
                    <li>Sản phẩm đã được sửa chữa bởi bên thứ ba</li>
                    <li>Tem bảo hành bị rách, mờ hoặc không còn nguyên vẹn</li>
                </ul>
                <p><strong>3.</strong> Khi bảo hành, khách hàng cần mang theo phiếu bảo hành này.</p>
                <p><strong>4.</strong> Thời gian bảo hành có thể kéo dài 7-15 ngày tùy theo mức độ hư hỏng.</p>
                <p><strong>5.</strong> Công ty có quyền từ chối bảo hành nếu không đáp ứng các điều kiện trên.</p>
            </div>

            <table class="signature-table">
                <tr>
                    <td style="width: 50%">
                        <strong>KHÁCH HÀNG</strong><br>
                        <em>(Ký và ghi rõ họ tên)</em><br><br><br><br>
                    </td>
                    <td style="width: 50%">
                        <strong>NGƯỜI BÁN</strong><br>
                        <em>(Ký và ghi rõ họ tên)</em><br><br><br><br>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        return html_content.encode('utf-8')

    def _generate_warranty_document_docx(self, order):
        """Generate warranty document as Word file using python-docx"""
        if not DOCX_AVAILABLE:
            raise UserError("python-docx library is not available")

        # Create new document
        doc = Document()

        # Set document margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Title
        title = doc.add_heading('PHIẾU BẢO HÀNH SẢN PHẨM', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Company info
        company_info = doc.add_paragraph()
        company_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        company_run = company_info.add_run(f'{order.company_id.name}\n')
        company_run.bold = True
        company_run.font.size = Pt(12)

        if order.company_id.street:
            company_info.add_run(f'Địa chỉ: {order.company_id.street}\n')
        if order.company_id.phone:
            company_info.add_run(f'Điện thoại: {order.company_id.phone}\n')
        if order.company_id.email:
            company_info.add_run(f'Email: {order.company_id.email}\n')

        doc.add_paragraph()  # Empty line

        # Order information table
        order_table = doc.add_table(rows=6, cols=2)
        order_table.style = 'Table Grid'
        order_table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Set column widths
        order_table.columns[0].width = Inches(2.5)
        order_table.columns[1].width = Inches(4)

        # Fill order information
        order_info_data = [
            ('Số đơn hàng:', order.name),
            ('Khách hàng:', order.partner_id.name),
            ('Ngày đặt hàng:', order.date_order.strftime('%d/%m/%Y') if order.date_order else ''),
            ('Người bán:', order.user_id.name if order.user_id else ''),
            ('Tổng giá trị:', f'{order.amount_total:,.0f} {order.currency_id.name}'),
            ('Ngày lập phiếu:', datetime.now().strftime('%d/%m/%Y'))
        ]

        for i, (label, value) in enumerate(order_info_data):
            order_table.cell(i, 0).text = label
            order_table.cell(i, 0).paragraphs[0].runs[0].bold = True
            order_table.cell(i, 1).text = str(value)

        doc.add_paragraph()  # Empty line

        # Products table
        products_heading = doc.add_heading('DANH SÁCH SẢN PHẨM BẢO HÀNH', level=2)
        products_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Create products table
        products_table = doc.add_table(rows=1, cols=5)
        products_table.style = 'Table Grid'
        products_table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Set column widths
        products_table.columns[0].width = Inches(0.5)  # STT
        products_table.columns[1].width = Inches(3)    # Sản phẩm
        products_table.columns[2].width = Inches(1)    # Số lượng
        products_table.columns[3].width = Inches(1.5)  # Bảo hành
        products_table.columns[4].width = Inches(1.5)  # Hết hạn

        # Header row
        header_cells = products_table.rows[0].cells
        headers = ['STT', 'Sản phẩm', 'Số lượng', 'Thời gian BH', 'Hết hạn BH']
        for i, header in enumerate(headers):
            header_cells[i].text = header
            header_cells[i].paragraphs[0].runs[0].bold = True
            header_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Add product rows
        for idx, line in enumerate(order.order_line.filtered(lambda l: not l.display_type), 1):
            row_cells = products_table.add_row().cells
            row_cells[0].text = str(idx)
            row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            row_cells[1].text = line.product_id.name or ''
            row_cells[2].text = f'{line.product_uom_qty:g}'
            row_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Warranty info
            warranty_text = line.product_warranty or 'Không có thông tin'
            row_cells[3].text = warranty_text
            row_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Calculate warranty expiry (assuming 12 months if no specific info)
            if order.date_order:
                warranty_months = 12  # Default
                if 'month' in warranty_text.lower():
                    try:
                        import re
                        months_match = re.search(r'(\d+)', warranty_text)
                        if months_match:
                            warranty_months = int(months_match.group(1))
                    except:
                        pass

                expiry_date = order.date_order + timedelta(days=warranty_months * 30)
                row_cells[4].text = expiry_date.strftime('%d/%m/%Y')
            else:
                row_cells[4].text = 'N/A'
            row_cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph()  # Empty line

        # Warranty terms
        warranty_heading = doc.add_heading('ĐIỀU KIỆN BẢO HÀNH', level=2)
        warranty_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        warranty_terms = [
            '1. Sản phẩm được bảo hành miễn phí trong thời gian quy định kể từ ngày mua.',
            '2. Bảo hành không áp dụng cho các trường hợp:',
            '   - Hư hỏng do sử dụng sai cách, va đập, rơi vỡ',
            '   - Hư hỏng do thiên tai, hỏa hoạn, ngập nước',
            '   - Sản phẩm đã được sửa chữa bởi bên thứ ba',
            '   - Tem bảo hành bị rách, mờ hoặc không còn nguyên vẹn',
            '3. Khi bảo hành, khách hàng cần mang theo phiếu bảo hành này.',
            '4. Thời gian bảo hành có thể kéo dài 7-15 ngày tùy theo mức độ hư hỏng.',
            '5. Công ty có quyền từ chối bảo hành nếu không đáp ứng các điều kiện trên.'
        ]

        for term in warranty_terms:
            p = doc.add_paragraph(term)
            if term.startswith(('1.', '2.', '3.', '4.', '5.')):
                p.style = 'List Number'

        doc.add_paragraph()  # Empty line

        # Signatures
        signature_table = doc.add_table(rows=3, cols=2)
        signature_table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Remove borders
        for row in signature_table.rows:
            for cell in row.cells:
                cell._element.get_or_add_tcPr().append(
                    doc._element.xpath('//w:tblBorders')[0] if doc._element.xpath('//w:tblBorders') else None
                )

        # Signature content
        signature_table.cell(0, 0).text = 'KHÁCH HÀNG'
        signature_table.cell(0, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        signature_table.cell(0, 0).paragraphs[0].runs[0].bold = True

        signature_table.cell(0, 1).text = 'NGƯỜI BÁN'
        signature_table.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        signature_table.cell(0, 1).paragraphs[0].runs[0].bold = True

        signature_table.cell(1, 0).text = '(Ký và ghi rõ họ tên)'
        signature_table.cell(1, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        signature_table.cell(1, 1).text = '(Ký và ghi rõ họ tên)'
        signature_table.cell(1, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Add some space for signatures
        signature_table.cell(2, 0).text = '\n\n\n'
        signature_table.cell(2, 1).text = '\n\n\n'

        # Save to BytesIO
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)

        # Return the file
        return request.make_response(
            output.getvalue(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
                ('Content-Disposition', content_disposition(f'Warranty_{order.name}.docx'))
            ]
        )

    @http.route('/sale_order/export_quotation_docx/<int:order_id>', type='http', auth='user')
    def export_quotation_docx(self, order_id, **kwargs):
        """Export quotation to Word document with complete structure"""
        try:
            order = request.env['sale.order'].browse(order_id)
            if not order.exists():
                raise UserError("Sale order not found")

            # Create Word document
            doc = Document()

            # Set document margins
            sections = doc.sections
            for section in sections:
                section.top_margin = Inches(0.5)
                section.bottom_margin = Inches(0.5)
                section.left_margin = Inches(0.8)
                section.right_margin = Inches(0.8)

            # 1. THÔNG TIN CHUNG CỦA BÁO GIÁ
            self._add_quotation_header(doc, order)

            # 2. THÔNG TIN KHÁCH HÀNG
            self._add_customer_info(doc, order)

            # 3. THÔNG TIN CÔNG TY GỬI BÁO GIÁ
            self._add_company_info(doc, order)

            # 4. LỜI MỞ ĐẦU
            self._add_opening_message(doc, order)

            # 5. BẢNG CHI TIẾT SẢN PHẨM
            self._add_product_table(doc, order)

            # 6. TỔNG HỢP GIÁ TRỊ
            self._add_total_summary(doc, order)

            # 7. ĐIỀU KHOẢN THƯƠNG MẠI
            self._add_commercial_terms(doc, order)

            # 8. PHẦN XÁC NHẬN & CHỮ KÝ
            self._add_signature_section(doc, order)

            # Save to BytesIO
            output = io.BytesIO()
            doc.save(output)
            output.seek(0)

            # Return the file
            return request.make_response(
                output.getvalue(),
                headers=[
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
                    ('Content-Disposition', content_disposition(f'Quotation_{order.name}.docx'))
                ]
            )

        except Exception as e:
            _logger.error(f"Error exporting quotation to Word: {str(e)}")
            return request.not_found()

    def _add_quotation_header(self, doc, order):
        """1. Thông tin chung của báo giá"""
        # Company logo and header
        header_table = doc.add_table(rows=2, cols=2)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Logo cell
        logo_cell = header_table.cell(0, 0)
        logo_p = logo_cell.paragraphs[0]
        logo_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        logo_p.add_run("CÔNG TY TNHH IMALL VIỆT NAM").bold = True

        # Quote number and date
        info_cell = header_table.cell(0, 1)
        info_p = info_cell.paragraphs[0]
        info_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # Generate quote number
        quote_number = f"IMV-{order.name.replace('S', '').replace('Q', '')}"
        info_p.add_run(f"Số báo giá: {quote_number}").bold = True
        info_p.add_run(f"\nNgày: {datetime.now().strftime('%d/%m/%Y')}")

        # Title
        title_cell = header_table.cell(1, 0)
        title_cell.merge(header_table.cell(1, 1))
        title_p = title_cell.paragraphs[0]
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_p.add_run("BẢNG BÁO GIÁ")
        title_run.bold = True
        title_run.font.size = Pt(16)

        doc.add_paragraph()  # Add space

    def _add_customer_info(self, doc, order):
        """2. Thông tin khách hàng"""
        customer_p = doc.add_paragraph()
        customer_p.add_run("Kính gửi: ").bold = True
        customer_p.add_run(order.partner_id.name or "")

        if order.partner_id.vat:
            doc.add_paragraph(f"MST: {order.partner_id.vat}")

        if order.partner_id.street:
            doc.add_paragraph(f"Địa chỉ: {order.partner_id.street}")

        if order.partner_id.phone:
            doc.add_paragraph(f"Số điện thoại: {order.partner_id.phone}")

        if order.partner_id.email:
            doc.add_paragraph(f"Email: {order.partner_id.email}")

        doc.add_paragraph()  # Add space

    def _add_company_info(self, doc, order):
        """3. Thông tin công ty gửi báo giá"""
        company_p = doc.add_paragraph()
        company_p.add_run("Thông tin công ty:").bold = True

        doc.add_paragraph("Tên công ty: CÔNG TY TNHH IMALL VIỆT NAM")
        doc.add_paragraph("MST: 0316161476")
        doc.add_paragraph("Địa chỉ: 52/1A Huỳnh Văn Nghệ, P. Tân Sơn, TP. HCM")

        if order.user_id:
            doc.add_paragraph(f"Nhân viên phụ trách: {order.user_id.name}")
            if order.user_id.email:
                doc.add_paragraph(f"Email: {order.user_id.email}")
            if order.user_id.phone:
                doc.add_paragraph(f"Số điện thoại: {order.user_id.phone}")

        doc.add_paragraph("Website: www.imallvietnam.com")
        doc.add_paragraph()  # Add space

    def _add_opening_message(self, doc, order):
        """4. Lời mở đầu"""
        opening_p = doc.add_paragraph()
        opening_text = f"""Cảm ơn Quý khách hàng đã quan tâm đến sản phẩm và dịch vụ của chúng tôi.
Theo yêu cầu của Quý khách, chúng tôi xin gửi đến Quý khách bảng báo giá chi tiết như sau:"""
        opening_p.add_run(opening_text)
        doc.add_paragraph()  # Add space

    def _add_product_table(self, doc, order):
        """5. Bảng chi tiết sản phẩm/thiết bị"""
        # Create product table
        table = doc.add_table(rows=1, cols=7)
        table.style = 'Table Grid'

        # Header row
        header_cells = table.rows[0].cells
        headers = ['TT', 'Tên thiết bị', 'ĐVT', 'SL', 'Đơn giá', 'Thành tiền', 'Ghi chú']

        for i, header in enumerate(headers):
            cell = header_cells[i]
            cell.text = header
            # Make header bold
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.bold = True
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Add product rows
        stt = 1
        for line in order.order_line.filtered(lambda l: not l.display_type):
            row_cells = table.add_row().cells

            # STT
            row_cells[0].text = str(stt)
            row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Tên thiết bị với thông tin chi tiết
            product_info = f"{line.product_id.name}\n"
            if hasattr(line.product_id, 'default_code') and line.product_id.default_code:
                product_info += f"Model: {line.product_id.default_code}\n"
            if hasattr(line.product_id, 'barcode') and line.product_id.barcode:
                product_info += f"Part Number: {line.product_id.barcode}\n"
            if hasattr(line.product_id, 'country_of_origin') and line.product_id.country_of_origin:
                product_info += f"Xuất xứ: {line.product_id.country_of_origin.name}\n"
            if hasattr(line, 'product_warranty') and line.product_warranty:
                product_info += f"Bảo hành: {line.product_warranty}"

            row_cells[1].text = product_info.strip()

            # ĐVT
            row_cells[2].text = line.product_uom.name if line.product_uom else ''
            row_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Số lượng
            row_cells[3].text = f"{line.product_uom_qty:,.0f}"
            row_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Đơn giá
            row_cells[4].text = f"{line.price_unit:,.0f}"
            row_cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

            # Thành tiền
            row_cells[5].text = f"{line.price_subtotal:,.0f}"
            row_cells[5].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

            # Ghi chú (delivery time, etc.)
            note = ""
            if hasattr(line, 'delivery_time') and line.delivery_time:
                note = f"Giao hàng: {line.delivery_time}"
            row_cells[6].text = note

            stt += 1

        doc.add_paragraph()  # Add space

    def _add_total_summary(self, doc, order):
        """6. Tổng hợp giá trị"""
        # Create summary table
        summary_table = doc.add_table(rows=4, cols=2)
        summary_table.alignment = WD_TABLE_ALIGNMENT.RIGHT

        # Tổng tiền trước VAT
        summary_table.cell(0, 0).text = "Tổng tiền trước VAT:"
        summary_table.cell(0, 1).text = f"{order.amount_untaxed:,.0f} VNĐ"
        summary_table.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # VAT
        tax_amount = order.amount_total - order.amount_untaxed
        summary_table.cell(1, 0).text = "VAT (10%):"
        summary_table.cell(1, 1).text = f"{tax_amount:,.0f} VNĐ"
        summary_table.cell(1, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # Tổng tiền cần thanh toán
        summary_table.cell(2, 0).text = "Tổng tiền cần thanh toán:"
        total_cell = summary_table.cell(2, 1)
        total_cell.text = f"{order.amount_total:,.0f} VNĐ"
        total_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        # Make total bold
        for run in total_cell.paragraphs[0].runs:
            run.bold = True

        # Bằng chữ
        summary_table.cell(3, 0).text = "Bằng chữ:"
        amount_text = self._number_to_words(order.amount_total)
        summary_table.cell(3, 1).text = amount_text

        doc.add_paragraph()  # Add space

    def _add_commercial_terms(self, doc, order):
        """7. Điều khoản thương mại"""
        terms_p = doc.add_paragraph()
        terms_p.add_run("ĐIỀU KHOẢN THƯƠNG MẠI").bold = True
        terms_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph()

        # 1. Thời gian giao hàng
        delivery_p = doc.add_paragraph()
        delivery_p.add_run("1. Thời gian giao hàng: ").bold = True
        delivery_p.add_run("Theo cột ghi chú trong bảng sản phẩm.")

        # 2. Phương thức thanh toán
        payment_p = doc.add_paragraph()
        payment_p.add_run("2. Phương thức thanh toán:").bold = True

        doc.add_paragraph("   • Hàng có sẵn: thanh toán 100% trước khi giao hàng")
        doc.add_paragraph("   • Hàng đặt: 50% khi đặt hàng, 50% trước khi giao (trong vòng 15 ngày từ ngày thông báo)")
        doc.add_paragraph("   • Chuyển khoản ngân hàng: MB Bank - CN TP.HCM")
        doc.add_paragraph("     STK: 0316161476001 - CÔNG TY TNHH IMALL VIỆT NAM")

        # 3. Điều kiện bảo hành
        warranty_p = doc.add_paragraph()
        warranty_p.add_run("3. Điều kiện bảo hành: ").bold = True
        warranty_p.add_run("Theo tiêu chuẩn nhà sản xuất, được ghi trong cột bảo hành.")

        # 4. Hiệu lực báo giá
        validity_p = doc.add_paragraph()
        validity_p.add_run("4. Hiệu lực báo giá: ").bold = True
        validity_p.add_run("30 ngày kể từ ngày lập báo giá (hàng tồn thay đổi mỗi ngày).")

        doc.add_paragraph()

    def _add_signature_section(self, doc, order):
        """8. Phần xác nhận đặt hàng & chữ ký"""
        # Create signature table
        signature_table = doc.add_table(rows=4, cols=2)
        signature_table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Headers
        signature_table.cell(0, 0).text = "NGƯỜI BÁO GIÁ"
        signature_table.cell(0, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        signature_table.cell(0, 0).paragraphs[0].runs[0].bold = True

        signature_table.cell(0, 1).text = "GIÁM ĐỐC"
        signature_table.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        signature_table.cell(0, 1).paragraphs[0].runs[0].bold = True

        # Names
        if order.user_id:
            signature_table.cell(1, 0).text = order.user_id.name
        else:
            signature_table.cell(1, 0).text = "Nhân viên kinh doanh"
        signature_table.cell(1, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        signature_table.cell(1, 1).text = "Nguyễn Thị Minh Tâm"
        signature_table.cell(1, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Signature spaces
        signature_table.cell(2, 0).text = "\n\n\n(Ký tên)"
        signature_table.cell(2, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        signature_table.cell(2, 1).text = "\n\n\n(Ký tên, đóng dấu)"
        signature_table.cell(2, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Contact info
        contact_info = """
Liên hệ đặt hàng:
Địa chỉ: 52/1A Huỳnh Văn Nghệ, P. Tân Sơn, TP. HCM
Điện thoại: (028) 3844 6789
Email: sales@imallvietnam.com
Website: www.imallvietnam.com"""

        signature_table.cell(3, 0).merge(signature_table.cell(3, 1))
        signature_table.cell(3, 0).text = contact_info
        signature_table.cell(3, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _number_to_words(self, amount):
        """Convert number to Vietnamese words"""
        try:
            # Simple implementation - you can enhance this
            if amount == 0:
                return "Không đồng"

            # For now, return a simple format
            return f"{amount:,.0f} đồng (bằng chữ)"
        except:
            return "Số tiền bằng chữ"
