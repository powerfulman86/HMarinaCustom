# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    hm_english_name = fields.Char(string=_("English Name"))
