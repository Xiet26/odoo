from odoo import models, fields, api

class SocialFloat(models.Model):
    _name = 'social.float'
    _description = 'Social Float Buttons'

    name = fields.Char(string='Name', required=True)
    zalo_link = fields.Char(string='Zalo Link')
    facebook_link = fields.Char(string='Facebook Link')
    phone_number = fields.Char(string='Phone Number')
    
    zalo_icon = fields.Text(string='Zalo SVG Icon', required=True, default='''
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path fill="currentColor" d="M12.49 10.272v-.45h1.347v6.322h-.77a.576.576 0 0 1-.577-.573v.001a3.273 3.273 0 0 1-1.938.632a3.284 3.284 0 0 1-3.284-3.282a3.284 3.284 0 0 1 3.284-3.282a3.273 3.273 0 0 1 1.937.632zm-1.939 5.032a2.174 2.174 0 0 0 2.175-2.172a2.174 2.174 0 0 0-2.175-2.172a2.174 2.174 0 0 0-2.174 2.172a2.174 2.174 0 0 0 2.174 2.172zm6.47-4.843a.578.578 0 0 1 .577-.573h.77v5.256c0 1.156-.97 2.093-2.166 2.093c-1.196 0-2.166-.937-2.166-2.093v-5.256h.77a.578.578 0 0 1 .577.573v4.683a.82.82 0 0 0 .82.817a.82.82 0 0 0 .818-.817V10.46zM8.683 9.344a4.187 4.187 0 0 1 4.186 4.184a4.187 4.187 0 0 1-4.186 4.184a4.187 4.187 0 0 1-4.185-4.184a4.187 4.187 0 0 1 4.185-4.184zm0 1.088a3.098 3.098 0 0 0-3.097 3.096a3.098 3.098 0 0 0 3.097 3.096a3.098 3.098 0 0 0 3.097-3.096a3.098 3.098 0 0 0-3.097-3.096zm10.87 5.838l-.258.002c-.902.01-1.643-.99-1.643-1.905v-5.893h1.642v5.888c0 .195.05.324.129.374c.07.044.13.045.13.045v1.489zM12 2C6.477 2 2 6.477 2 12s4.477 10 10 10s10-4.477 10-10S17.523 2 12 2z"/>
        </svg>
    ''')
    
    facebook_icon = fields.Text(string='Facebook SVG Icon', required=True, default='''
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path fill="currentColor" d="M14 13.5h2.5l1-4H14v-2c0-1.03 0-2 2-2h1.5V2.14c-.326-.043-1.557-.14-2.857-.14C11.928 2 10 3.657 10 6.7v2.8H7v4h3V22h4v-8.5z"/>
        </svg>
    ''')
    
    phone_icon = fields.Text(string='Phone SVG Icon', required=True, default='''
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <path fill="currentColor" d="M6.62 10.79c1.44 2.83 3.76 5.15 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24c1.12.37 2.33.57 3.57.57c.55 0 1 .45 1 1V20c0 .55-.45 1-1 1c-9.39 0-17-7.61-17-17c0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1c0 1.25.2 2.45.57 3.57c.11.35.03.74-.25 1.02l-2.2 2.2z"/>
        </svg>
    ''')
    
    is_active = fields.Boolean(string='Active', default=True)
    button_color = fields.Char(string='Button Color', default='#25D366')
    icon_color = fields.Char(string='Icon Color', default='#FFFFFF') 