# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'i.VAZ',
    'version': '11.0.1.0.0',
    'author': 'Naglis Jonaitis',
    'category': 'i.MAS',
    'website': 'https://naglis.me/',
    'license': 'AGPL-3',
    'depends': [
        'base_imas',
        'delivery',
        'fleet',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_carrier.xml',
        'views/ivaz_file.xml',
        'views/stock_picking.xml',
    ],
    'installable': True,
}
