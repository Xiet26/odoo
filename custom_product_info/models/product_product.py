from odoo import models, fields

class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    x_configuration_content = fields.Text(string='Configuration Content', translate=True) 