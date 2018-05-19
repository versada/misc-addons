# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, exceptions, models


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _opay_form_get_tx_from_data(self, data):
        '''Extracts the order ID from received data.

        Returns the corresponding transaction.'''
        reference = data.get('order_nr')
        if not reference:
            msg = 'Order no. missing in callback data'
            _logger.error(msg)
            raise exceptions.ValidationError(msg)

        txs = self.env['payment.transaction'].search([
            ('reference', '=', reference),
            ('acquirer_id.provider', '=', 'opay'),
        ])
        if not txs or len(txs) > 1:
            raise exceptions.ValidationError(
                'Callback data received for reference ID: "%s", '
                'either zero or multiple order found' % reference)
        return txs[0]

    @api.multi
    def _opay_form_get_invalid_parameters(self, data):
        '''Checks received parameters and returns a list of tuples.

        Tuple format: (parameter_name, received_value, expected_value).

        Transaction will not be validated if there is at least one
        invalid parameter.'''
        self.ensure_one()
