# Copyright 2020 Versada UAB
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base_imas.exceptions import iMASException, iMASUserException


class iVAZException(iMASException):
    '''Generic i.VAZ exception.'''


class iVAZUserException(iMASUserException):
    '''User-facing i.VAZ exception.'''
