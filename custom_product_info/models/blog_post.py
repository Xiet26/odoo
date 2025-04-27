from odoo import models, fields

class BlogPost(models.Model):
    _inherit = 'blog.post'

    product_ids = fields.Many2many(
        'product.template',
        'blog_post_product_rel',
        'blog_post_id',
        'product_id',
        string='Products'
    )
    category_ids = fields.Many2many(
        'product.category',
        'blog_post_category_rel',
        'blog_post_id',
        'category_id',
        string='Categories'
    ) 