### Models
- [ ] Create `models/blog_post.py` to inherit `blog.post` and add `product_ids` and `category_ids` Many2many fields
- [ ] Update `models/product_template.py` to add reverse `blog_post_ids` Many2many field
- [ ] Update `models/product_category.py` to add reverse `blog_post_ids` Many2many field
- [ ] Update `models/__init__.py` to import `blog_post.py`

### Views
- [ ] Create or update view for `blog.post` form to show and edit `product_ids` and `category_ids`
- [ ] Update product template form view to show and edit `blog_post_ids`
- [ ] Update product category form view to show and edit `blog_post_ids`

### Security
- [ ] Ensure ACLs allow access to new fields for relevant user groups

### Documentation
- [ ] Document new fields and relationships in module README or developer docs 