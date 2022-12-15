# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hm_english_name = fields.Char(string=_("English Name"))
    hm_insurance_id = fields.Char(string=_("Insurance No"))
    hm_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string=_("Gender"))

    hm_end_of_contract_date = fields.Date(string=_("End of Contract Date"))
    hm_end_of_service_date = fields.Date(string=_("End of Service Date"))
    hm_hire_date = fields.Date(string=_("Hire Date"))
