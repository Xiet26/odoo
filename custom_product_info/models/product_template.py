from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_manufacturer_id = fields.Many2one('product.manufacturer', string='Manufacturer')
    x_manufacturer_display = fields.Char(string='Manufacturer Display', compute='_compute_manufacturer_display', store=True)
    x_model = fields.Char(string='Model')
    x_part_number = fields.Char(string='Part Number')
    x_warranty_id = fields.Many2one('product.warranty', string='Warranty')
    x_warranty_display = fields.Char(string='Warranty Display', compute='_compute_warranty_display', store=True)
    x_origin_id = fields.Many2one('product.origin', string='Origin')
    x_origin_display = fields.Char(string='Origin Display', compute='_compute_origin_display', store=True)
    
    @api.depends('x_manufacturer_id')
    def _compute_manufacturer_display(self):
        for record in self:
            record.x_manufacturer_display = record.x_manufacturer_id.name if record.x_manufacturer_id else False

    @api.depends('x_warranty_id')
    def _compute_warranty_display(self):
        for record in self:
            record.x_warranty_display = record.x_warranty_id.name if record.x_warranty_id else False

    @api.depends('x_origin_id')
    def _compute_origin_display(self):
        for record in self:
            record.x_origin_display = record.x_origin_id.name if record.x_origin_id else False

    x_specifications_vi = fields.Html(string='Technical Specifications (Vietnamese)')
    x_specifications_en = fields.Html(string='Technical Specifications (English)')
    x_package_includes_vi = fields.Html(string='Package Includes (Vietnamese)')
    x_package_includes_en = fields.Html(string='Package Includes (English)')
    
    x_custom_document = fields.Binary(string='Additional Documents', attachment=True)
    x_custom_document_filename = fields.Char(string='Document Filename')
    
    x_custom_hs_code = fields.Char(string='Custom HS Code')
    x_customs_description = fields.Text(string='Customs Description')
    x_estimated_import_tax = fields.Float(string='Estimated Import Tax (%)', digits=(5,2)) 