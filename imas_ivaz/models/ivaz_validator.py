# Copyright 2018 Naglis Jonaitis
#           2020 Versada UAB
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import lxml.etree as ET

from odoo import _, models, modules, tools
from ..exceptions import iVAZUserException


class IVAZValidator(models.AbstractModel):
    _name = 'imas.ivaz.validator'

    def _unset_field(self, record, field):
        return [] if record[field] else [
            _('Field "%(field_string)s" not set on record: '
              '"%(name)s" (%(record)s)') % {
                'field_string': record._fields[field].string,
                'name': record.name_get()[0][1],
                'record': record,
            },
        ]

    def _validate_actor(self, actor):
        is_company = actor._name == 'res.company'
        if is_company and not actor.company_registry:
            return self._unset_field(actor, 'company_registry')
        elif not is_company and not actor.ref:
            return self._unset_field(actor, 'ref')
        return []

    def _validate_transporter_actor(self, picking):
        errors = []
        actor = picking._get_ivaz_transporter_actor()
        if actor:
            errors.extend(self._validate_actor(actor))
        else:
            errors.append('Transporter is unknown!')
        return errors

    def _validate_picking(self, picking):
        errors = []

        errors.extend(self._validate_actor(picking.company_id))
        errors.extend(self._validate_actor(picking.partner_id))

        errors.extend(self._unset_field(picking, 'time_of_dispatch'))

        errors.extend(self._validate_transporter_actor(picking))

        # Skip duplicated errors.
        errors = tools.OrderedSet(errors)

        if errors:
            msg = '\n'.join(errors)
            raise iVAZUserException(msg)

    def _validate_with_xsd(self, tree):
        # TODO: Allow to override by uploading XSD in settings.
        xsd_path = modules.get_module_resource(
            'imas_ivaz', 'data', 'ivaz_xsd_1_3_3.xsd')
        xml_schema = ET.XMLSchema(ET.parse(xsd_path))
        try:
            xml_schema.assertValid(tree)
        except ET.DocumentInvalid as e:
            raise iVAZUserException(_(
                'The generated i.VAZ XML does not validate against XSD '
                'schema: "%s". Please contact the Odoo administrator.'
            ) % e) from e
