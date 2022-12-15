# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    standard_price = fields.Float(string=_("Cost"), related='product_id.standard_price')
    cost_currency_id = fields.Many2one('res.currency', string=_("Currency"), related='product_id.cost_currency_id')
