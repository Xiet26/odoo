# -*- coding: utf-8 -*-

def migrate(cr, version):
    """
    Migration script for version 1.1.1
    - Added commercial_terms field to sale_order
    """
    # Add commercial_terms column to sale_order table
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='sale_order' AND column_name='commercial_terms'
    """)
    
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE sale_order 
            ADD COLUMN commercial_terms TEXT
        """)
