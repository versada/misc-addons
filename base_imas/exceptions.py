# Copyright 2020 Versada UAB
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions


class iMASException(Exception):
    '''Generic i.MAS exception.'''


class iMASUserException(exceptions.UserError, iMASException):
    '''User-facing i.MAS exception.'''
