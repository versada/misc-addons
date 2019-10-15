# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis,
#           2019 Versada UAB
# License LGPL-3 or later (https://www.gnu.org/licenses/agpl).

from openerp import _, api, exceptions, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def _notify_action(self, params):
        notifications = []
        is_admin = self.env.user.has_group('base.group_system')
        for user in self:
            if user != self.env.user and not is_admin:
                raise exceptions.AccessError(_(
                    u'Only users belonging to "Administration -> Settings" '
                    u'group can notify other users!'
                ))
            notifications.append((
                (
                    self.env.cr.dbname,
                    'web_notify_action.notify_action',
                    user.id,
                ),
                params,
            ))
        self.env['bus.bus'].sendmany(notifications)
