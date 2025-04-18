from odoo import models, fields, api

class ProductManufacturer(models.Model):
    _name = 'product.manufacturer'
    _description = 'Product Manufacturer'
    _order = 'name'

    name = fields.Char(string='Manufacturer Name', required=True, translate=True)
    code = fields.Char(string='Manufacturer Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    logo = fields.Image(string='Logo')  # Thêm trường logo
    content = fields.Html(string='Content', translate=True)  # Thêm trường content
    x_slug = fields.Char(string='Slug', compute='_compute_x_slug', store=True)  # Thêm trường slug

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Manufacturer name must be unique!')
    ]

    @api.depends('name')
    def _compute_x_slug(self):
        def convert_vietnamese_to_ascii(text):
            if not text:
                return ''
            vietnamese = 'ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ'
            vietnamese_ref = 'aaaaaaaaaaaaaaaaaoooooooooooooooooeeeeeeeeeeeuuuuuuuuuuuiiiiiyyyyyd'
            vietnamese = vietnamese + vietnamese.upper()
            vietnamese_ref = vietnamese_ref + vietnamese_ref.upper()
            
            trans_table = str.maketrans(vietnamese, vietnamese_ref)
            return text.translate(trans_table)

        for record in self:
            if record.name:
                # Convert Vietnamese characters to ASCII
                slug = convert_vietnamese_to_ascii(record.name.lower())
                # Replace special characters and spaces with hyphens
                slug = ''.join(c if c.isalnum() else '-' for c in slug)
                # Remove consecutive hyphens
                while '--' in slug:
                    slug = slug.replace('--', '-')
                # Remove leading/trailing hyphens
                slug = slug.strip('-')
                record.x_slug = slug
            else:
                record.x_slug = False

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