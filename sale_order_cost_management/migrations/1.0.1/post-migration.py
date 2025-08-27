# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Migration script to add missing columns to sale_order_line table
    """
    # Check if columns exist and add them if they don't
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='sale_order_line' AND column_name='cost_price'
    """)
    
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE sale_order_line 
            ADD COLUMN cost_price NUMERIC
        """)
    
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='sale_order_line' AND column_name='total_cost'
    """)
    
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE sale_order_line 
            ADD COLUMN total_cost NUMERIC
        """)
    
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='sale_order_line' AND column_name='line_margin'
    """)
    
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE sale_order_line 
            ADD COLUMN line_margin NUMERIC
        """)
