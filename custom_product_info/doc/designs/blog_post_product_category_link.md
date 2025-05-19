# Technical Design Document: Blog Post to Product & Category Linking

## 1. Overview

This feature extends the `blog.post` model to allow linking each blog post to multiple products (`product.template`) and categories (`product.category`). It also enables reverse access: products and categories can show related blog posts. The admin UI for blog posts, products, and categories will be updated to manage these links.

## 2. Requirements

### 2.1 Functional Requirements
- Allow each blog post to be linked to multiple products and categories.
- Allow each product and category to be linked to multiple blog posts (reverse relation).
- Update the detail views for blog post, product, and category to manage and display these links.

### 2.2 Non-Functional Requirements
- Fields can be blank or null (optional links).
- No data migration is required.

## 3. Technical Design

### 3.1 Model Changes (Odoo ORM)
- Inherit `blog.post` in a new model file.
- Add `Many2many` field `product_ids` (to `product.template`).
- Add `Many2many` field `category_ids` (to `product.category`).
- Inherit `product.template` and add reverse `Many2many` field `blog_post_ids`.
- Inherit `product.category` and add reverse `Many2many` field `blog_post_ids`.

#### Model UML
```python
# blog_post.py
class BlogPost(models.Model):
    _inherit = 'blog.post'
    product_ids = fields.Many2many('product.template', 'blog_post_product_rel', 'blog_post_id', 'product_id', string='Products')
    category_ids = fields.Many2many('product.category', 'blog_post_category_rel', 'blog_post_id', 'category_id', string='Categories')

# product_template.py
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    blog_post_ids = fields.Many2many('blog.post', 'blog_post_product_rel', 'product_id', 'blog_post_id', string='Blog Posts')

# product_category.py
class ProductCategory(models.Model):
    _inherit = 'product.category'
    blog_post_ids = fields.Many2many('blog.post', 'blog_post_category_rel', 'category_id', 'blog_post_id', string='Blog Posts')
```

### 3.2 Use Case Layer
- None required (pure model/view change).

### 3.3 Service Layer
- None required.

### 3.4 Repository Layer
- None required.

### 3.5 Controller Layer
- None required.

### 3.6 Workflow / Events
- None required.

### 3.7 Security Considerations
- Ensure ACLs allow access to new fields for relevant user groups.

### 3.8 Performance Considerations
- Many2many fields are indexed by default in Odoo.

## 4. Testing Plan
- Manual test: Link blog posts to products/categories and verify in all three forms.

## 5. Open Questions
- None (all clarified with user).

## 6. Alternatives Considered
- None needed for this straightforward relationship extension. 