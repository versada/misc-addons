# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import functools
import logging
import urllib

from odoo import api, fields, models

from ..controllers.main import OPAYController
from ..opay import (
    OPAY_DEFAULT_COUNTRY,
    OPAY_DEFAULT_LANG,
    OPAY_GATEWAY_URL,
    OPAY_LANG_MAP,
    OPAY_SPEC_VERSION,
    opay_bool_to_str,
    opay_encode_values,
    opay_sign_with_password,
)

_logger = logging.getLogger(__name__)


def get_lang_from_values(values):
    lang = values.get('billing_partner_lang') or ''
    if '_' in lang:
        lang = OPAY_LANG_MAP.get(lang.split('_')[0].lower(), '')
    return lang or OPAY_DEFAULT_LANG


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[
            ('opay', 'OPAY'),
        ],
    )
    opay_website_id = fields.Char(
        string='OPAY Website ID',
        required_if_provider='opay',
        groups='base.group_user',
    )
    opay_sign_key = fields.Char(
        string='OPAY Signing Key',
        required_if_provider='opay',
        groups='base.group_user',
    )
    opay_test_user_id = fields.Char(
        string='OPAY Test User ID',
    )
    opay_redirect_on_success = fields.Boolean(
        string='Redirect on success',
        default=True,
    )

    @api.multi
    def ensure_opay(self):
        for rec in self:
            if not rec.provider == 'opay':
                raise ValueError('Unexpected payment provider used!')

    @api.multi
    def _get_opay_form_values(self, values):
        self.ensure_one().ensure_opay()

        currency = self.env.ref('base.EUR')
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        full_url = functools.partial(urllib.parse.urljoin, base_url)

        opay_params = dict(
            website_id=self.opay_website_id,
            order_nr=values['reference'],
            redirect_url=full_url('/shop/payment/validate'),
            redirect_on_success=opay_bool_to_str(
                self.opay_redirect_on_success),
            web_service_url=full_url(OPAYController._callback_url),
            standard=OPAY_SPEC_VERSION,
            language=get_lang_from_values(values),
            amount='%d' % int(currency.round(values['amount']) * 100),
            currency=currency.name,
            # show_channels='',
            # hide_channels='',
            country=OPAY_DEFAULT_COUNTRY,
            # accepturl=full_url(PayseraController._accept_url),
            # cancelurl=full_url(PayseraController._cancel_url),
            # callbackurl=full_url(PayseraController._callback_url),
            # country=country_code,
            # p_firstname=values['billing_partner_first_name'],
            # p_lastname=values['billing_partner_last_name'],
            # p_streec=values['billing_partner_address'],
            # p_city=values['billing_partner_city'],
            # p_zip=values['billing_partner_zip'],
            # p_countrycode=country_code,
            # test='1' if self.environment == 'test' else '0',
            # version=paysera.PAYSERA_API_VERSION,
        )
        if values.get('billing_partner_email'):
            opay_params.update(c_email=values['billing_partner_email'])
        if self.environment == 'test' and self.opay_test_user_id:
            opay_params.update(test=self.opay_test_user_id)

        _logger.info(opay_params)
        return opay_params

    @api.multi
    def opay_form_generate_values(self, values):
        self.ensure_one().ensure_opay()

        opay_params = self._get_opay_form_values(values)

        signature = opay_sign_with_password(opay_params, self.opay_sign_key)
        opay_params.update(password_signature=signature)

        values.update(encoded=opay_encode_values(opay_params))

        return values

    @api.multi
    def opay_get_form_action_url(self) -> str:
        '''Returns the form action URL.'''
        self.ensure_one().ensure_opay()
        return OPAY_GATEWAY_URL
