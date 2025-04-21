from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = 'product.category'

    x_content = fields.Html(string='Content', translate=True)
    x_slug = fields.Char(string='URL Slug', compute='_compute_x_slug', store=True)
    x_is_show_in_homepage = fields.Boolean(string='Show in Homepage', default=False)
    x_logo = fields.Image(string='Logo')  # Thêm trường logo

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
                # Append the record ID
                record.x_slug = f"{slug}-{record.id}" if record.id else slug
            else:
                record.x_slug = False 