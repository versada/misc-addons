# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis,
#           2019 Versada UAB
# License LGPL-3 or later (https://www.gnu.org/licenses/agpl).

from openerp.addons.bus.bus import Controller as BusController
from openerp.http import request


class NotifyActionBusController(BusController):

    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            channels.append((
                request.db,
                'web_notify_action.notify_action',
                request.env.user.id,
            ))
        return super(NotifyActionBusController, self)._poll(
            dbname, channels, last, options)
