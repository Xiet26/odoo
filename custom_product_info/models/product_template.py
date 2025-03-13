from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_manufacturer_id = fields.Many2one('product.manufacturer', string='Manufacturer')
    x_model = fields.Char(string='Model')
    x_part_number = fields.Char(string='Part Number')
    x_warranty_id = fields.Many2one('product.warranty', string='Warranty')
    x_origin_id = fields.Many2one('product.origin', string='Origin')
    
    x_specifications_vi = fields.Html(string='Technical Specifications (Vietnamese)')
    x_specifications_en = fields.Html(string='Technical Specifications (English)')
    x_package_includes_vi = fields.Html(string='Package Includes (Vietnamese)')
    x_package_includes_en = fields.Html(string='Package Includes (English)')
    
    x_custom_document = fields.Binary(string='Additional Documents', attachment=True)
    x_custom_document_filename = fields.Char(string='Document Filename')
    
    x_custom_hs_code = fields.Char(string='Custom HS Code')
    x_customs_description = fields.Text(string='Customs Description')
    x_estimated_import_tax = fields.Float(string='Estimated Import Tax (%)', digits=(5,2)) 