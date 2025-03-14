from odoo import models, fields, api

class ProductWarranty(models.Model):
    _name = 'product.warranty'
    _description = 'Product Warranty'
    _order = 'duration'

    name = fields.Char(string='Warranty Name', required=True, translate=True)
    duration = fields.Integer(string='Duration (Months)', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Warranty name must be unique!')
    ]

    @api.depends('name', 'duration')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f'{record.name} ({record.duration} months)'

    def name_get(self):
        result = []
        for record in self:
            name = f'{record.name} ({record.duration} months)'
            result.append((record.id, name))
        return result 