from odoo import models, fields, api

class ProductManufacturer(models.Model):
    _name = 'product.manufacturer'
    _description = 'Product Manufacturer'
    _order = 'name'

    name = fields.Char(string='Manufacturer Name', required=True, translate=True)
    code = fields.Char(string='Manufacturer Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Manufacturer name must be unique!')
    ]

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for record in self:
            if record.code:
                record.display_name = f'[{record.code}] {record.name}'
            else:
                record.display_name = record.name

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                name = f'[{record.code}] {record.name}'
            else:
                name = record.name
            result.append((record.id, name))
        return result 