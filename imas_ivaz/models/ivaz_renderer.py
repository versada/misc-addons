# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import datetime

import lxml.etree as ET

from odoo import api, fields, models

from ..const import IVAZ_XML_NAMESPACE

PARTNER_ADDRESS_FIELDS = (
    'street',
    'street2',
    'city',
    'zip',
)
PARTNER_CONTACT_INFO_FIELDS = (
    'phone',
    'mobile',
    'email',
)


def str_el(tag, value, attrib=None, max_length=None, nsmap=None, **extra):
    element = ET.Element(tag, attrib=attrib, nsmap=nsmap, **extra)
    text = value if isinstance(value, str) else str(value)
    if max_length is not None:
        text = text[:max_length]
    element.text = text
    return element


def float_el(tag, value, total_digits=None, fraction_digits=None, attrib=None,
             nsmap=None, **extra):
    if total_digits is not None and not value < total_digits ** 10:
        raise ValueError('Value for tag: %s is too large' % tag)
    if fraction_digits is not None:
        value = ('{value:.%df}' % fraction_digits).format(value=value)
    return str_el(tag, value, attrib=attrib, nsmap=nsmap, **extra)


def int_el(tag, value, total_digits=None, attrib=None, nsmap=None, **extra):
    if total_digits is not None and not value < total_digits ** 10:
        raise ValueError('Value for tag: %s is too large' % tag)
    return str_el(tag, value, attrib=attrib, nsmap=nsmap, **extra)


class IVAZRenderer(models.AbstractModel):
    _name = 'imas.ivaz.renderer'
    _description = 'i.VAZ XML Renderer (abstract)'
    _ivaz_version = 'iVAZ1.3.3'

    @api.model
    def get_ns_map(self):
        '''Returns the namespace mapping used for rendering the i.VAZ XML.'''
        return {
            None: IVAZ_XML_NAMESPACE,
        }

    @api.model
    def render_file_description(self, company, date_created=None):
        date_created = (date_created or datetime.datetime.now()).replace(
            microsecond=0)
        fd = ET.Element('FileDescription')
        fd.append(str_el('FileVersion', self._ivaz_version, max_length=24))
        fd.append(str_el('FileDateCreated', date_created.isoformat()))
        fd.append(str_el(
            'SoftwareCompanyName',
            'Naglis Jonaitis',
            max_length=256))
        fd.append(str_el('SoftwareName', 'Odoo i.VAZ', max_length=256))
        # FIXME(naglis): take version from module?
        fd.append(str_el('SoftwareVersion', '1.0', max_length=24))
        fd.append(str_el(
            'CreatorRegistrationNumber', company.company_registry))
        return fd

    @api.model
    def render_transport_documents(self, pickings):
        el = ET.Element('TransportDocuments')
        for picking in pickings:
            el.append(self.render_transport_document(picking))
        return el

    @api.model
    def render_transport_document(self, picking):
        el = ET.Element('TransportDocument')
        uid_el = ET.SubElement(el, 'TransportDocumentUID')
        uid_el.append(str_el(
            'LocalTransportDocumentUID', picking.id, max_length=40))
        el.append(str_el(
            'LocalTransportDocumentNumber', picking.id, max_length=35))
        if picking.scheduled_date:
            doc_date = fields.Date.from_string(picking.scheduled_date)
            el.append(str_el(
                'LocalTransportDocumentDate', doc_date.isoformat()))
        poi_el = ET.SubElement(el, 'PlaceOfIssueTransportDocument')
        poi_el.append(self.render_address(picking.company_id.partner_id))

        dispatch_dt = fields.Datetime.from_string(picking.time_of_dispatch)
        el.append(str_el('TimeOfDispatch', dispatch_dt.isoformat()))

        if picking.eta:
            eta_dt = fields.Datetime.from_string(picking.eta)
            el.append(str_el('EstimatedTimeOfArrival', eta_dt.isoformat()))

        el.append(
            self.render_actor(
                'Consignor', picking.company_id, is_company=True))
        el.append(self.render_actor('Consignee', picking.partner_id))

        el.append(self.render_transporter(picking))

        wh = picking.picking_type_id.warehouse_id
        ship_from_el = ET.SubElement(el, 'ShipFrom')
        ship_from_el.append(str_el('WarehouseID', wh.code, max_length=24))
        load_addr_el = ET.SubElement(ship_from_el, 'LoadAddress')
        load_addr_el.append(self.render_address(wh.partner_id))
        # XXX: ImportCustomOffice?

        ship_to_el = ET.SubElement(el, 'ShipTo')
        # XXX: Warehouse?
        # ship_to_el.append(str_el('WarehouseID', wh.code))
        unload_addr_el = ET.SubElement(ship_to_el, 'UnloadAddress')
        unload_addr_el.append(self.render_address(picking.partner_id))
        # XXX: ExportCustomOffice?

        el.append(self.render_delivery_data(picking))

        # TODO: ComplementaryTransportInformation

        return el

    @api.model
    def render_product(self, line_no, move_line):
        el = ET.Element('Product')
        el.append(int_el('ProductLineNumber', line_no, total_digits=3))
        # TODO: Is quantity_done ok to use here?
        el.append(float_el(
            'Quantity',
            move_line.quantity_done, total_digits=10, fraction_digits=3,
        ))
        el.append(str_el(
            'UnitOfMeasure', move_line.product_uom.name, max_length=24))

        product = move_line.product_id
        if product.default_code:
            el.append(str_el(
                'ProductCode', product.default_code, max_length=70))
        # FIXME: Is this code ok to use here?
        if product.hs_code:
            el.append(str_el(
                'AdditionalProductCode', product.hs_code, max_length=70))
        # FIXME: Is it correct to use this description here?
        el.append(str_el(
            'ProductDescription', product.name, max_length=350))
        return el

    @api.model
    def render_delivery_data(self, picking):
        el = ET.Element('DeliveryData')
        products_el = ET.SubElement(el, 'Products')
        for idx, move in enumerate(picking.move_lines, start=1):
            products_el.append(self.render_product(idx, move))
        if picking.package_ids:
            packages_el = ET.SubElement(el, 'Packages')
            for package in picking.package_ids:
                packages_el.append(self.render_package(picking, package))
        el.append(self.render_weight(picking))

        # TODO: ClassesAndNumbers
        # XXX: Should classes and numbers be defined on products or on the
        # picking?

        # TODO: Value
        # XXX: Where to take the value from?

        # TODO: Currency

        # TODO: ComplementaryDeliveryInformation
        # XXX: Ok to use `note` here?
        if picking.note:
            el.append(str_el(
                'ComplementaryDeliveryInformation',
                picking.note, max_length=256,
            ))

        return el

    @api.model
    def render_weight(self, picking):
        el = ET.Element('Weight')
        el.append(float_el(
            'GrossWeight',
            picking.shipping_weight,
            total_digits=13,
            fraction_digits=3,
        ))
        el.append(float_el(
            'NetWeight',
            picking.weight_bulk,
            total_digits=13,
            fraction_digits=3,
        ))
        el.append(str_el(
            'UnitOfMeasure', picking.weight_uom_id.name, max_length=10))
        return el

    @api.model
    def render_package(self, picking, package):
        el = ET.Element('Package')
        el.append(str_el(
            'KindOfPackagesCode', package.packaging_id.name, max_length=24))
        el.append(str_el('PackagesID', package.name, max_length=256))
        # FIXME: Is this correct?
        el.append(str_el('NumberOfPackages', 1))
        # FIXME: Seals?
        return el

    @api.model
    def render_actor(self, tag, actor, is_company=False, is_transporter=False):
        el = ET.Element(tag)
        el.append(str_el(
            'RegistrationNumber',
            actor.company_registry if is_company else actor.ref,
            max_length=35,
        ))
        actor_partner = (
            actor.partner_id if is_company else actor.commercial_partner_id)
        el.append(str_el(
            'Name',
            actor_partner.name,
            max_length=256,
        ))
        addr_el = ET.SubElement(
            el, 'TransporterAddress' if is_transporter else 'Address')
        addr_el.append(self.render_address(actor_partner))

        contact_info = [
            actor_partner[f]
            for f in PARTNER_CONTACT_INFO_FIELDS
            if actor_partner[f]
        ]
        if contact_info:
            el.append(str_el(
                'ContactInformation', '; '.join(contact_info), max_length=256))

        return el

    @api.model
    def render_transporter(self, picking):
        if picking.use_delivery_carrier:
            el = self.render_actor(
                'Transporter', picking.carrier_id.partner_id,
                is_transporter=True)
        else:
            el = self.render_actor(
                'Transporter', picking.company_id, is_company=True,
                is_transporter=True)

        means_el = ET.SubElement(el, 'TransportMeans')
        for mean in picking.transport_mean_ids:
            means_el.append(self.render_mean(mean))
        return el

    @api.model
    def render_mean(self, mean):
        el = ET.Element('TransportMean')
        el.append(str_el(
            'IdentityOfTransportUnits', mean.license_plate, max_length=10))
        el.append(str_el(
            'MarqueModelTransportUnits',
            ' '.join([
                mean.vehicle_model_id.brand_id.name,
                mean.vehicle_model_id.name,
            ]),
            max_length=70,
        ))
        # FIXME: Extract to separate func?
        if mean.seal_ids:
            seals_el = ET.SubElement(el, 'Seals')
            for seal in mean.seal_ids:
                seal_el = ET.SubElement(seals_el, 'Seal')
                seal_el.append(str_el(
                    'IdentityOfCommercialSeal', seal.name, max_length=35))
                if seal.description:
                    seal_el.append(str_el(
                        'SealInformation', seal.description, max_length=256))
        return el

    @api.model
    def render_address(self, partner):
        '''
        Returns address tag from `res.partner`.

        We render the unstructured address as Odoo does not provide
        building number in a reliable way. Parsing building number from `steet`
        is heuristic, eg. 'Kovo 11-osios g. 1-2', etc.

        Override this function in your module if you use a third-party
        module to add building number support on `res.partner` and want to
        return the structured address.
        '''
        return str_el(
            'FullAddress',
            ', '.join(
                partner[f] for f in PARTNER_ADDRESS_FIELDS if partner[f]),
            max_length=256,
        )

    def from_pickings(self, pickings):
        root = ET.Element('iVAZFile', nsmap=self.get_ns_map())
        root.append(self.render_file_description(pickings[:1].company_id))
        root.append(self.render_transport_documents(pickings))
        return ET.tostring(root, pretty_print=True)
