# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, UserError


class TestExcelExport(TransactionCase):

    def setUp(self):
        super().setUp()
        
        # Create test partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'test@example.com',
        })
        
        # Create test product
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'default_code': 'TEST001',
            'standard_price': 100.0,
            'list_price': 150.0,
        })
        
        # Create test sale order
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'price_unit': 150.0,
            })]
        })
        
        # Create test cost
        self.cost = self.env['sale.order.cost'].create({
            'name': 'TEST-COST-001',
            'description': 'Test additional cost',
            'amount': 50.0,
            'order_id': self.sale_order.id,
        })

    def test_action_export_xlsx(self):
        """Test the action_export_xlsx method returns correct action"""
        action = self.sale_order.action_export_xlsx()
        
        self.assertEqual(action['type'], 'ir.actions.act_url')
        self.assertEqual(action['target'], 'self')
        self.assertIn(f'/sale_order/export_xlsx/{self.sale_order.id}', action['url'])

    def test_excel_export_controller_access_denied(self):
        """Test controller access control"""
        # This would require HTTP test setup which is more complex
        # For now, we just test the model method
        pass

    def test_sale_order_with_costs_and_lines(self):
        """Test sale order has proper cost calculations"""
        # Confirm the order to trigger computations
        self.sale_order.action_confirm()
        
        # Check computed fields
        self.assertEqual(self.sale_order.total_cost, 50.0)  # Additional cost
        self.assertEqual(self.sale_order.order_lines_cost, 200.0)  # 2 * 100 cost price
        self.assertEqual(self.sale_order.total_all_costs, 250.0)  # 50 + 200
        self.assertEqual(self.sale_order.final_profit, 50.0)  # 300 revenue - 250 costs

    def test_order_line_computations(self):
        """Test order line cost computations"""
        line = self.sale_order.order_line[0]
        
        self.assertEqual(line.cost_price, 100.0)
        self.assertEqual(line.total_cost, 200.0)  # 100 * 2 qty
        self.assertEqual(line.line_margin, 100.0)  # 300 subtotal - 200 cost
