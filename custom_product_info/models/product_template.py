from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_manufacturer_id = fields.Many2one('product.manufacturer', string='Manufacturer')
    x_manufacturer_display = fields.Char(string='Manufacturer Display', compute='_compute_manufacturer_display', store=True)
    x_model = fields.Char(string='Model', translate=True)
    x_part_number = fields.Char(string='Part Number')
    x_internal_code = fields.Char(string='Internal Code', compute='_compute_internal_code', store=True)
    x_warranty_id = fields.Many2one('product.warranty', string='Warranty')
    x_warranty_display = fields.Char(string='Warranty Display', compute='_compute_warranty_display', store=True)
    x_origin_id = fields.Many2one('product.origin', string='Origin')
    x_origin_display = fields.Char(string='Origin Display', compute='_compute_origin_display', store=True)
    
    @api.depends('x_manufacturer_id', 'x_model', 'x_part_number')
    def _compute_internal_code(self):
        for record in self:
            parts = []
            if record.x_manufacturer_id and record.x_manufacturer_id.name:
                parts.append(record.x_manufacturer_id.name)
            if record.x_model:
                parts.append(record.x_model)
            if record.x_part_number:
                parts.append(record.x_part_number)
            record.x_internal_code = ' - '.join(parts) if parts else False

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

    x_specifications = fields.Html(string='Technical Specifications', translate=True)
    x_package_includes = fields.Html(string='Package Includes', translate=True)
    
    x_custom_document = fields.Binary(string='Additional Documents', attachment=True)
    x_custom_document_filename = fields.Char(string='Document Filename', translate=True)
    
    x_custom_hs_code = fields.Char(string='Custom HS Code')
    x_customs_description = fields.Text(string='Customs Description', translate=True)
    x_estimated_import_tax = fields.Float(string='Estimated Import Tax (%)', digits=(5,2)) 