# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import http

from ..opay import opay_decode_values

_logger = logging.getLogger(__name__)


class OPAYController(http.Controller):
    _callback_url = '/payment/opay/callback'

    @http.route([
        _callback_url,
    ], type='http', methods=['post'], auth='none', csrf=False)
    def opay_payment_callback(self, **post_data):
        sudo_tx_obj = http.request.env['payment.transaction'].sudo()

        try:
            encoded_data = post_data['encoded']
        except KeyError:
            return b'NOT OK'
        parsed_data = opay_decode_values(encoded_data)
        _logger.info('Callback data: %s', parsed_data)

        try:
            ok = sudo_tx_obj.form_feedback(parsed_data, 'opay')
        except Exception:
            _logger.exception(
                'An error occurred while handling OPAY callback')
            ok = False
        return b'OK' if ok else b'NOT OK'
