# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'i.MAS Base',
    'version': '11.0.1.0.0',
    'author': 'Naglis Jonaitis',
    'category': 'i.MAS',
    'license': 'AGPL-3',
    'depends': [
    ],
    'external_dependencies': {
        'python': [
            'cryptography',
        ],
    },
    'data': [
        'security/imas_security.xml',
        'security/ir.model.access.csv',
        'views/imas.xml',
    ],
    'images': [
    ],
    'installable': True,
}
