from odoo import models, fields

class ProductFAQ(models.Model):
    _name = 'product.faq'
    _description = 'Product FAQ'
    _order = 'question'

    question = fields.Char(string='Question', required=True, translate=True)
    answer = fields.Text(string='Answer', required=True, translate=True)
    product_tmpl_ids = fields.Many2many(
        'product.template',
        'product_faq_product_template_rel',
        'faq_id',
        'product_tmpl_id',
        string='Products'
    ) 