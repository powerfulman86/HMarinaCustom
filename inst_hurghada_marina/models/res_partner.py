# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_boat_owner = fields.Boolean(string=_("Boat Owner"))
    is_apartment_owner = fields.Boolean(string=_("Apartment Owner"))
    is_apartment_renter = fields.Boolean(string=_("Apartment Renter"))
    is_shop_renter = fields.Boolean(string=_("Shop Renter"))

    hm_english_name = fields.Char(string=_("English Name"))
    hm_governrate = fields.Char(string=_("Governrate"))
    hm_contact_type = fields.Selection([
        ('Boat', 'Boat'),
        ('Shop', 'Shop'),
        ('Apartment', 'Apartment'),
    ], string=_("Contact Type"))

    # Vendor Extra Info
    hm_activity = fields.Char(string=_("Activity"))
    hm_activity_type = fields.Char(string=_("Activity Type"))
    hm_activity_type_code = fields.Char(string=_("Activity Type Code"))

    hm_fav_item = fields.Char(string=_("Favorite Item"))
    hm_fav_item_2 = fields.Char(string=_("Favorite Item 2"))
    hm_fav_item_3 = fields.Char(string=_("Favorite Item 3"))
    hm_fav_item_4 = fields.Char(string=_("Favorite Item 4"))

    # Boat Info
    hm_boat_nationality = fields.Selection([
        ('Egyptian', 'Egyptian'),
        ('Foreign', 'Foreign'),
    ], string=_("Boat Nationality"))
    hm_boat_category = fields.Selection([
        ('Boat', 'Boat'),
        ('Catamaran', 'Catamaran'),
        ('Daily', 'Daily'),
        ('Safari', 'Safari'),
        ('Service', 'Service'),
        ('Speed', 'Speed'),
        ('Glass Boat', 'Glass Boat'),
        ('Yacht', 'Yacht'),
        ('Zodiac', 'Zodiac'),
    ], string=_("Boat Category"))
    hm_boat_type = fields.Selection([
        ('Commercial', 'Commercial'),
        ('Government', 'Government'),
        ('Private', 'Private'),
    ], string=_("Boat Type"))
    hm_boat_length = fields.Char(string=_("Boat Length"))
    hm_boat_width = fields.Char(string=_("Boat Width"))

    hm_boat_code = fields.Char(string=_("Boat Code"))
    hm_special_discount = fields.Char(string=_("Special Discount"))

    # Shop Info
    hm_shop_area_in = fields.Char(string=_("Shop Area 'Inside' (m2)"))
    hm_shop_area_in_price = fields.Char(string=_("Shop Price 'Inside' (EGP)"))

    hm_shop_area_out = fields.Char(string=_("Shop Area 'Outside' (m2)"))
    hm_shop_area_out_price = fields.Char(string=_("Shop Price 'Outside' Price (EGP)"))

    # Apartment Info
    hm_apartment_area = fields.Char(string=_("Apartment Area (m2)"))
    hm_apartment_price = fields.Char(string=_("Apartment Price"))

    @api.depends('company_type', 'parent_id')
    @api.onchange('name')
    def _onchange_name(self):
        if self.company_type == 'person' and not self.parent_id:
            return {
                'value': {
                    'warning': _("Please select the company first!"),
                    'name': False,
                }
            }