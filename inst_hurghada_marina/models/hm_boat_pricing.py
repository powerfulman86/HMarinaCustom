# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HmBoatPricingLine(models.Model):
    _name = 'hm.boat.pricing.line'
    _description = "Boat Pricing Line"

    pricing_id = fields.Many2one('hm.boat.pricing', string=_("Boot Pricing ID"))
    duration = fields.Selection([
        ('d', 'Day'),
        ('m', 'Month'),
        ('y', 'Year'),
    ], string=_("Duration"), Required=True)
    boat_nationality = fields.Selection([
        ('Egyptian', 'Egyptian'),
        ('Foreign', 'Foreign'),
    ], string=_("Boat Nationality"), Required=True)
    boat_type = fields.Selection([
        ('Commercial', 'Commercial'),
        ('Government', 'Government'),
        ('Private', 'Private'),
    ], string=_("Boat Type"), Required=True)
    fees_egp = fields.Float(string=_("Fees (EGP)"))
    fees_usd = fields.Float(string=_("Fees (USD)"))


class HmBoatPricing(models.Model):
    _name = 'hm.boat.pricing'
    _description = "Boat Pricing"

    name = fields.Char(string=_("Pricing Name"))
    length_from = fields.Float(string=_("Length From"), required=True)
    length_to = fields.Float(string=_("Length To"), required=True)
    line_ids = fields.One2many('hm.boat.pricing.line', 'pricing_id', string=_('Pricing Items'))

    @api.model
    def create(self, vals):
        if vals.get('length_from') and vals.get('length_to'):
            vals['name'] = "From %s to %s" % (vals['length_from'], vals['length_to'])
        return super(HmBoatPricing, self).create(vals)

    def write(self, vals):
        if vals.get('length_from') and vals.get('length_to'):
            vals['name'] = "From %s to %s" % (vals['length_from'], vals['length_to'])
        return super(HmBoatPricing, self).write(vals)
