# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    hm_contact_type = fields.Selection([
        ('Boat', 'Boat'),
        ('Shop', 'Shop'),
        ('Apartment', 'Apartment'),
        ('General', 'General'),
    ], string=_("Contact Type"))
    hm_boat_partner_id = fields.Many2one('res.partner', string=_("Boat Partner"))
    hm_shop_partner_id = fields.Many2one('res.partner', string=_("Shop Partner"))
    hm_apartment_partner_id = fields.Many2one('res.partner', string=_("Apartment Partner"))
    hm_boat_length = fields.Char(string=_("Boat Length"), related='partner_id.hm_boat_length')
    hm_boat_nationality = fields.Selection(string=_("Boat Nationality"), related='partner_id.hm_boat_nationality')
    hm_boat_type = fields.Selection(string=_("Boat Type"), related='partner_id.hm_boat_type')

    is_boat_owner = fields.Boolean(string=_("Boat Owner"), related='hm_boat_partner_id.is_boat_owner')
    is_apartment_owner = fields.Boolean(string=_("Apartment Owner"), related='hm_apartment_partner_id.is_apartment_owner')
    is_apartment_renter = fields.Boolean(string=_("Apartment Renter"), related='hm_apartment_partner_id.is_apartment_renter')
    is_shop_renter = fields.Boolean(string=_("Shop Renter"), related='hm_shop_partner_id.is_shop_renter')

    @api.onchange('hm_contact_type')
    def _onchange_hm_contact_type(self):
        domain = {}
        value = {}

        if self.hm_contact_type == 'General':
            domain['partner_id'] = [
                ('customer_rank','>',0),
                ('hm_contact_type','not in',['Boat', 'Shop', 'Apartment']),
                ('is_boat_owner','=',False),
                ('is_apartment_owner','=',False),
                ('is_apartment_renter','=',False),
                ('is_shop_renter','=',False),
            ]
        else:
            domain['partner_id'] = [('id','=',0)]
        value['hm_boat_partner_id'] = False
        value['hm_shop_partner_id'] = False
        value['hm_apartment_partner_id'] = False
        value['partner_id'] = False
        return {
            'domain': domain,
            'value': value,
        }

    @api.onchange('hm_boat_partner_id')
    def _onchange_hm_boat_partner_id(self):
        domain = {}
        value = {}
        boat_recs = self.env['res.partner'].search([('parent_id','=',self.hm_boat_partner_id.id)])
        boats_list = []
        for b in boat_recs:
            boats_list.append(b.id)

        domain['partner_id'] = [('id','in',boats_list)]
        value['partner_id'] = False
        return {
            'domain': domain,
            'value': value,
        }

    @api.onchange('hm_shop_partner_id')
    def _onchange_hm_shop_partner_id(self):
        domain = {}
        value = {}
        shop_recs = self.env['res.partner'].search([('parent_id','=',self.hm_shop_partner_id.id)])
        shops_list = []
        for b in shop_recs:
            shops_list.append(b.id)

        domain['partner_id'] = [('id','in',shops_list)]
        value['partner_id'] = False
        return {
            'domain': domain,
            'value': value,
        }

    @api.onchange('hm_apartment_partner_id')
    def _onchange_hm_apartment_partner_id(self):
        domain = {}
        value = {}
        apartment_recs = self.env['res.partner'].search([('parent_id','=',self.hm_apartment_partner_id.id)])
        apartments_list = []
        for b in apartment_recs:
            apartments_list.append(b.id)

        domain['partner_id'] = [('id','in',apartments_list)]
        value['partner_id'] = False
        return {
            'domain': domain,
            'value': value,
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    boat_fees = fields.Float(string=_("Boat Fees"), compute='_compute_boat_fees')

    @api.depends('order_id.hm_boat_length', 'product_uom', 'product_uom_qty')
    def _compute_boat_fees(self):
        for l in self:
            if l.order_id.partner_id.hm_contact_type != 'Boat':
                l.boat_fees = 0.0
            elif l.product_id != self.env.ref('inst_hurghada_marina.boat_duration_product'):
                l.boat_fees = 0.0
            elif l.product_id == self.env.ref('inst_hurghada_marina.boat_duration_product'):
                boat_length = l.order_id.hm_boat_length
                pricing_found = self.env['hm.boat.pricing'].search([
                    ('length_from', '<=', float(boat_length)),
                    ('length_to', '>=', float(boat_length))
                ])
                if pricing_found:
                    price_unit = 0.0
                    for pl in pricing_found.line_ids:
                        # Get day fees
                        if l.product_uom.name == 'Days' and pl.duration == 'd' \
                            and l.order_id.hm_boat_nationality == 'Egyptian' and pl.boat_nationality == 'Egyptian' \
                            and l.order_id.hm_boat_type == 'Commercial' and pl.boat_type == 'Commercial':

                            price_unit = pl.fees_egp
                            break
                        elif l.product_uom.name == 'Days' and pl.duration == 'd' \
                            and l.order_id.hm_boat_nationality == 'Egyptian' and pl.boat_nationality == 'Egyptian' \
                            and l.order_id.hm_boat_type == 'Private' and pl.boat_type == 'Private':

                            price_unit = pl.fees_egp
                            break

                        # Get month fees
                        elif l.product_uom.name == 'Months' and pl.duration == 'm' \
                            and l.order_id.hm_boat_nationality == 'Egyptian' and pl.boat_nationality == 'Egyptian' \
                            and l.order_id.hm_boat_type == 'Commercial' and pl.boat_type == 'Commercial':

                            price_unit = pl.fees_egp
                            break
                        elif l.product_uom.name == 'Months' and pl.duration == 'm' \
                            and l.order_id.hm_boat_nationality == 'Egyptian' and pl.boat_nationality == 'Egyptian' \
                            and l.order_id.hm_boat_type == 'Private' and pl.boat_type == 'Private':

                            price_unit = pl.fees_egp
                            break

                        # Get year fees
                        elif l.product_uom.name == 'Years' and pl.duration == 'y' \
                            and l.order_id.hm_boat_nationality == 'Egyptian' and pl.boat_nationality == 'Egyptian' \
                            and l.order_id.hm_boat_type == 'Commercial' and pl.boat_type == 'Commercial':

                            price_unit = pl.fees_egp
                            break
                        elif l.product_uom.name == 'Years' and pl.duration == 'y' \
                            and l.order_id.hm_boat_nationality == 'Egyptian' and pl.boat_nationality == 'Egyptian' \
                            and l.order_id.hm_boat_type == 'Private' and pl.boat_type == 'Private':

                            price_unit = pl.fees_egp
                            break

                    l.price_unit = price_unit * float(boat_length)
                    l.boat_fees = price_unit * float(boat_length) * l.product_uom_qty

    @api.onchange('product_id')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()

        domain = {}
        value = {}
        if self.order_id.hm_contact_type == 'Boat':
            boats_products = [
                self.env.ref('inst_hurghada_marina.boat_duration_product').id,
                self.env.ref('inst_hurghada_marina.electricity_product').id,
                self.env.ref('inst_hurghada_marina.water_product').id,
                self.env.ref('inst_hurghada_marina.penalty_product').id,
            ]
            domain['product_id'] = [('id','in', boats_products)]
        return {
            'domain': domain,
            'value': value,
        }
