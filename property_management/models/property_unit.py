# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
from random import randint


class PropertyActivity(models.Model):
    _name = "property.activity"
    _description = "Property Activity"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Activity Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


class PropertyUnit(models.Model):
    _name = 'property.unit'
    _rec_name = 'internal_reference'
    _description = 'Property Unit'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    internal_reference = fields.Char(string="Internal Reference", )

    description = fields.Char(string="Description", required=False, )
    type = fields.Selection(string="Type", selection=[('apartment', 'Apartment'),
                                                      ('shop', 'Shop'),
                                                      ('ship', 'Ship'), ], required=False, )
    commercial_reference = fields.Char(string="Commercial Reference", )

    size = fields.Float(string="Size", required=False, )
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the product without removing it.")
    note = fields.Text('Notes ...', )
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Favorite'),
    ], default='0', string="Favorite")
    image_1920 = fields.Binary('Image', attachment=True)
    unit_activity = fields.Many2many('property.activity', string='Unit Activity')
    contract_count = fields.Integer(compute='_compute_contract_count')

    _sql_constraints = [
        ("property_reference_uniq", "unique (internal_reference)", "Reference Number already exists !"),
    ]

    def _compute_contract_count(self):
        contract_data = self.env['property.contract'].read_group(
            domain=[('property_id', 'in', self.ids), ('stage_id', '!=', False)],
            fields=['property_id'],
            groupby=['property_id'])
        mapped_data = dict([(m['property_id'][0], m['property_id_count']) for m in contract_data])
        for property in self:
            property.contract_count = mapped_data.get(property.id, 0)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            connector = '&' if operator in expression.NEGATIVE_TERM_OPERATORS else '|'
            domain = [connector, ('internal_reference', operator, name), ('commercial_reference', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        res = []
        for each in self:
            name = '%s - %s' % (each.internal_reference,
                                each.commercial_reference) if each.internal_reference else each.commercial_reference
            res.append((each.id, name))
        return res
