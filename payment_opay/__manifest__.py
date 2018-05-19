# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'OPAY Payment Acquirer',
    'version': '11.0.1.0.0',
    'author': 'Naglis Jonaitis',
    'category': 'eCommerce',
    'website': 'https://naglis.me/addon/payment_opay/',
    'license': 'AGPL-3',
    'summary': 'Collect payment using OPAY',
    'depends': [
        'payment',
    ],
    'data': [
        'views/payment_acquirer.xml',
        'views/website_templates.xml',
        'data/payment_acquirer.xml',
    ],
    'images': [
    ],
    'installable': True,
    'application': False,
}
