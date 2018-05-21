# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import lxml.etree as ET

from odoo import _, api, exceptions, models, modules


class IVAZValidator(models.AbstractModel):
    _name = 'imas.ivaz.validator'

    @api.model
    def validate_actor(self, actor, is_company=False):
        if is_company and not actor.company_registry:
            return self.unset_field(actor, 'company_registry')
        elif not is_company and not actor.ref:
            return self.unset_field(actor, 'ref')
        return []

    @api.model
    def unset_field(self, record, field):
        return [] if record[field] else [
            _('Field "%(field_string)s" not set on record: '
              '"%(name)s" (%(record)s)') % {
                'field_string': record._fields[field].string,
                'name': record.name_get()[0][1],
                'record': record,
            },
        ]

    @api.model
    def validate_picking(self, picking):
        errors = []

        errors.extend(self.validate_actor(picking.company_id, is_company=True))
        errors.extend(self.validate_actor(picking.partner_id))

        errors.extend(self.unset_field(picking, 'time_of_dispatch'))

        if picking.use_delivery_carrier:
            carrier = picking.carrier_id
            errors.extend(self.unset_field(picking, 'carrier_id'))
            errors.extend(self.unset_field(carrier, 'partner_id'))
            errors.extend(self.validate_actor(carrier.partner_id))

        if errors:
            msg = '\n'.join(errors)
            raise exceptions.ValidationError(msg)

    def validate_with_xsd(self, tree):
        # TODO: Allow to override by uploading XSD in settings.
        xsd_path = modules.get_module_resource(
            'imas_ivaz', 'data', 'ivaz_xsd_1_3_3.xsd')
        xml_schema = ET.XMLSchema(ET.parse(xsd_path))
        xml_schema.assertValid(tree)
