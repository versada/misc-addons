# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import base64

import lxml.etree as ET

from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    use_delivery_carrier = fields.Boolean(
        string='Use Carrier Delivery',
        help='If checked, indicates that the products are delivered by '
             'external delivery company.',
    )
    time_of_dispatch = fields.Datetime(
        string='Time of Dispatch',
    )
    eta = fields.Datetime(
        string='Estimated Time of Arrival',
    )
    transport_mean_ids = fields.One2many(
        comodel_name='ivaz.transport.mean',
        inverse_name='picking_id',
        string='Vehicles',
    )
    ivaz_file_ids = fields.One2many(
        comodel_name='ivaz.file',
        inverse_name='picking_id',
        string='i.VAZ Files',
    )
    ivaz_file_count = fields.Integer(
        string='i.VAZ File Count',
        compute='_compute_ivaz_file_count',
        store=False,
    )

    @api.depends('ivaz_file_ids')
    def _compute_ivaz_file_count(self):
        for record in self:
            record.ivaz_file_count = len(record.ivaz_file_ids)

    @api.multi
    def action_see_ivaz_files(self):
        self.ensure_one()
        action = self.env['ivaz.file'].get_formview_action()
        if len(self.ivaz_file_ids) == 1:
            action.update(res_id=self.ivaz_file_ids.id)
        else:
            action.update(
                name=_('i.VAZ Files'),
                domain=[
                    ('id', 'in', self.ivaz_file_ids.ids),
                ],
                views=[],
                view_mode='tree,form',
            )
        return action

    @api.multi
    def action_generate_ivaz(self):
        self.ensure_one()
        validator = self.env['imas.ivaz.validator']
        validator.validate_picking(self)
        ivaz_xml = self.env['imas.ivaz.renderer'].from_pickings(self)
        print(ivaz_xml.decode('utf-8'))
        ivaz_tree = ET.fromstring(ivaz_xml)
        validator.validate_with_xsd(ivaz_tree)
        ivaz_file = self.env['ivaz.file'].create({
            'ivaz_file': base64.b64encode(ivaz_xml),
            'picking_id': self.id,
        })
        return ivaz_file.get_formview_action()
