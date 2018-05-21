# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Carrier Partner',
        ondelete='restrict',
    )
