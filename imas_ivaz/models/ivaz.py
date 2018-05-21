# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IVAZSeal(models.AbstractModel):
    _name = 'ivaz.seal'
    _description = 'i.VAZ Seal (abstract)'

    name = fields.Char(
        string='Number',
        required=True,
        size=35,
    )
    description = fields.Char(
        size=256,
    )


class IVAZTransportMeanSeal(models.Model):
    _name = 'ivaz.transport.mean.seal'
    _inherit = 'ivaz.seal'
    _description = 'i.VAZ Transport Mean Seal'

    mean_id = fields.Many2one(
        comodel_name='ivaz.transport.mean',
        string='Transport Mean',
        ondelete='cascade',
    )


class IVAZTransportMean(models.Model):
    _name = 'ivaz.transport.mean'
    _description = 'i.VAZ Transport'

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        ondelete='cascade',
    )
    use_delivery_carrier = fields.Boolean(
        related='picking_id.use_delivery_carrier',
        readonly=True,
    )
    license_plate = fields.Char(
        string='License Plate',
        size=10,
        required=True,
    )
    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
        ondelete='restrict',
    )
    vehicle_model_id = fields.Many2one(
        comodel_name='fleet.vehicle.model',
        string='Vehicle Model',
        ondelete='restrict',
        required=True,
    )
    seal_ids = fields.One2many(
        comodel_name='ivaz.transport.mean.seal',
        inverse_name='mean_id',
        string='Seals',
    )

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if not self.use_delivery_carrier:
            self.update({
                'vehicle_model_id': self.vehicle_id.model_id.id,
                'license_plate': self.vehicle_id.license_plate,
            })


class IVAZFile(models.Model):
    _name = 'ivaz.file'
    _description = 'i.VAZ File'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=False,
    )
    ivaz_file = fields.Binary(
        string='i.VAZ File',
        readonly=True,
    )
    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Delivery Order',
        readonly=True,
        required=True,
    )

    def _compute_name(self):
        for record in self:
            record.name = 'i.VAZ_%d.xml' % record.id
