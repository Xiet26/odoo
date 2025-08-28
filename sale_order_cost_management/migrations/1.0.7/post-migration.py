# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Migration script to add missing columns for version 1.0.7
    """
    # Add new columns to sale_order table
    columns_to_add_order = [
        ('order_lines_cost', 'NUMERIC'),
        ('total_all_costs', 'NUMERIC'),
        ('final_profit', 'NUMERIC')
    ]
    
    for column_name, column_type in columns_to_add_order:
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sale_order' AND column_name=%s
        """, (column_name,))
        
        if not cr.fetchone():
            cr.execute(f"""
                ALTER TABLE sale_order 
                ADD COLUMN {column_name} {column_type}
            """)
    
    # Add columns to sale_order_line table if they don't exist
    columns_to_add_line = [
        ('cost_price', 'NUMERIC'),
        ('total_cost', 'NUMERIC'),
        ('line_margin', 'NUMERIC'),
        ('product_warranty', 'VARCHAR')
    ]
    
    for column_name, column_type in columns_to_add_line:
        cr.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='sale_order_line' AND column_name=%s
        """, (column_name,))
        
        if not cr.fetchone():
            cr.execute(f"""
                ALTER TABLE sale_order_line 
                ADD COLUMN {column_name} {column_type}
            """)
