# -*- coding: utf-8 -*-

from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError
from random import randint
from odoo.osv import expression


class PropertyContractStage(models.Model):
    _name = 'property.contract.stage'
    _description = 'Property Contract Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', translate=True)
    sequence = fields.Integer(default=1)
    description = fields.Text(
        "Requirements", help="Enter here the internal requirements for this stage. It will appear "
                             "as a tooltip over the stage's name.", translate=True)
    active = fields.Boolean(string='Active', default=True)
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    category = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('closed', 'Closed')], required=True, default='draft', help="Category of the stage")


class PropertyContractTags(models.Model):
    _name = "property.contract.tags"
    _description = "Property Contract Tags"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Tag Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


class PropertyRentTemplate(models.Model):
    _name = 'property.rent.template'
    _rec_name = 'name'
    _description = 'Property Rent Template'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    code = fields.Char(help="Code is added automatically in the display name of every subscription.")
    description = fields.Html(translate=True, string="Terms and Conditions")
    contract_count = fields.Integer(compute='_compute_contract_count')
    color = fields.Integer()
    company_id = fields.Many2one('res.company', index=True)
    type = fields.Selection(string="Type", selection=[('apartment', 'Apartment'),
                                                      ('shop', 'Shop'),
                                                      ('ship', 'Ship'), ], required=True, )
    template_line = fields.One2many('property.rent.template.line', 'template_id', string='Template Lines', copy=True,
                                    auto_join=True, )
    rent_base = fields.Selection(string="Rent Base", selection=[('fixed', 'Fixed'),
                                                                ('bysize', 'By Size'), ], required=False, )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('close', 'Closed'),
    ], string='State', index=True, default='draft', tracking=True, )

    def _compute_contract_count(self):
        contract_data = self.env['property.contract'].read_group(
            domain=[('template_id', 'in', self.ids), ('stage_id', '!=', False)],
            fields=['template_id'],
            groupby=['template_id'])
        mapped_data = dict([(m['template_id'][0], m['template_id_count']) for m in contract_data])
        for template in self:
            template.contract_count = mapped_data.get(template.id, 0)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            connector = '&' if operator in expression.NEGATIVE_TERM_OPERATORS else '|'
            domain = [connector, ('code', operator, name), ('name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def name_get(self):
        res = []
        for sub in self:
            name = '%s - %s' % (sub.code, sub.name) if sub.code else sub.name
            res.append((sub.id, name))
        return res

    @api.onchange('state')
    def _onchange_state(self):
        pass

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You can not delete Template Which Is Not In Draft State.'))
        return super(PropertyRentTemplate, self).unlink()

    @api.constrains('template_line')
    def _check_rent_product_in_line(self):
        for template in self:
            exist_product_list = []
            for line in template.template_line:
                if line.service_type == 'rent' and len(exist_product_list) != 0:
                    raise ValidationError(_('Rent Product Must be unique.'))
                if line.service_type == 'rent':
                    exist_product_list.append(line.product_id.id)


class PropertyRentTemplateLine(models.Model):
    _name = 'property.rent.template.line'
    _rec_name = 'name'
    _description = 'Property Rent Template Line'

    name = fields.Char()
    template_id = fields.Many2one('property.rent.template', string='Rent Template', required=True, ondelete='cascade',
                                  index=True, copy=False)
    company_id = fields.Many2one('res.company', related='template_id.company_id', string='Company', store=True,
                                 readonly=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('detailed_type', '=', 'service')]",
        change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('is_medicine', '=', True)])
    service_type = fields.Selection(string="Service Type", selection=[('rent', 'Rent'), ('service', 'Service'), ],
                                    required=True, )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('close', 'Closed'),
    ], string='State', related='template_id.state', )
    price_unit = fields.Float('Default Price', required=False, digits='Product Price', default=0.0)


class PropertyContract(models.Model):
    _name = 'property.contract'
    _rec_name = 'name'
    _description = 'Property Contract'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = []
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        default_stage = self.env['property.contract.stage'].search([], limit=1)
        return default_stage

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    def _get_default_pricelist(self):
        return self.env['product.pricelist'].search([('currency_id', '=', self.env.company.currency_id.id)], limit=1).id

    def _compute_currency_rate(self):
        self.currency_rate = 1.0

    name = fields.Char(string='Contact Reference', copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))

    stage_id = fields.Many2one('property.contract.stage', string='Stage', ondelete='restrict', tracking=True,
                               index=True,
                               default=_get_default_stage_id, group_expand='_read_group_stage_ids', copy=False)
    stage_category = fields.Selection(related='stage_id.category', store=True)
    date_contract = fields.Datetime(string='Contract Date', required=True, index=True, copy=False,
                                    default=fields.Datetime.now, )
    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date_end = fields.Date(string='End Date', default=fields.Date.today)
    tag_ids = fields.Many2many('property.contract.tags', string='Tags')
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=2,
                              default=lambda self: self.env.user,
                              domain=lambda self: [
                                  ('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman').id)],
                              readonly=True)
    team_id = fields.Many2one(
        'crm.team', 'Sales Team', change_default=True, default=_get_default_team,
        check_company=True, ondelete="set null", tracking=True, readonly=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True, index=True,
                                 tracking=1,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    property_id = fields.Many2one(comodel_name="property.unit", string="Property", required=True, index=True,
                                  tracking=2, )
    pricelist_id = fields.Many2one('product.pricelist',
                                   domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                   string='Pricelist', default=_get_default_pricelist, required=True,
                                   check_company=True)
    currency_id = fields.Many2one('res.currency', related='pricelist_id.currency_id', string='Currency', readonly=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, tracking=4)
    currency_rate = fields.Float("Currency Rate", compute='_compute_currency_rate', compute_sudo=True, store=True,
                                 digits=(12, 6), readonly=True,
                                 help='The rate of the currency to the currency of rate 1 applicable at the date of the order')
    to_renew = fields.Boolean(string='To Renew', default=False, copy=False)
    note = fields.Text('Terms and conditions', )
    description = fields.Html()
    company_id = fields.Many2one('res.company', string="Company", default=lambda s: s.env.company, required=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Default Payment Terms',
                                      tracking=True,
                                      help="These payment terms will be used when generating new invoices and renewal/upsell orders. Note that invoices paid using online payment will use 'Already paid' regardless of this setting.")
    type = fields.Selection(string="Type", selection=[('apartment', 'Apartment'),
                                                      ('shop', 'Shop'),
                                                      ('ship', 'Ship'), ], required=True, )
    template_id = fields.Many2one(
        'property.rent.template', string='Rent Template',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True,
        help="The Rent template defines the invoice policy and the payment terms.", tracking=True,
        check_company=True)
    contract_line = fields.One2many('property.contract.line', 'contract_id', string='Contract Lines', copy=True,
                                    auto_join=True, )
    monthly_fees = fields.Float('Monthly Fees', required=False, digits='Product Price', default=0.0)
    invoice_count = fields.Integer(compute='_compute_invoice_count')

    def _compute_invoice_count(self):
        self.invoice_count = 0
        # can_read = self.env['account.move'].check_access_rights('read', raise_exception=False)
        # if not can_read:
        #     self.update({'invoice_count': 0})
        #     return
        # res = self.env['account.move.line'].read_group(
        #     [('subscription_id', 'in', self.ids)], ['move_id:count_distinct'], ['subscription_id'])
        # invoice_count_dict = {r['subscription_id'][0]: r['move_id'] for r in res}
        # for subscription in self:
        #     subscription.invoice_count = invoice_count_dict.get(subscription.id, 0)

    def action_contract_invoice(self):
        self.ensure_one()
        invoices = self.env['account.move'].search([('invoice_line_ids.subscription_id', 'in', self.ids)])
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action["context"] = {
            "create": False,
            "default_move_type": "out_invoice"
        }
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('property.contract') or _('New')

        return super(PropertyContract, self).create(vals)

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     if self.partner_id:
    #         self.pricelist_id = self.partner_id.with_company(self.company_id).property_product_pricelist.id
    #         self.payment_term_id = self.partner_id.with_company(self.company_id).property_payment_term_id.id
    #     if self.partner_id.user_id:
    #         self.user_id = self.partner_id.user_id

    def set_to_renew(self):
        return self.write({'to_renew': True})

    def unset_to_renew(self):
        return self.write({'to_renew': False})

    def write(self, values):
        last = self.stage_id.sequence
        res = super(PropertyContract, self).write(values)
        now = self.stage_id.sequence
        if now < last:
            raise ValidationError(_("Must Proceed In Forward Steps !"))

        return res

    @api.onchange('template_id')
    def _onchange_template(self):
        # we need to avoid keeping incorrect lines, so clearing is necessary too.
        if self.template_id != self._origin.template_id:
            self.contract_line = [(5,)]


        pass


class PropertyContractLine(models.Model):
    _name = 'property.contract.line'
    _rec_name = 'name'
    _description = 'Property Contract Line'

    name = fields.Char()
    contract_id = fields.Many2one('property.contract', string='Property Contract', required=True, ondelete='cascade',
                                  index=True, copy=False)
    company_id = fields.Many2one('res.company', related='contract_id.company_id', string='Company', store=True,
                                 readonly=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_id = fields.Many2one('product.product', string='Product', domain="[('detailed_type', '=', 'service')]",
                                 change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    product_template_id = fields.Many2one(
        'product.template', string='Product Template',
        related="product_id.product_tmpl_id", domain=[('is_medicine', '=', True)])
    service_type = fields.Selection(string="Service Type", selection=[('rent', 'Rent'), ('service', 'Service'), ],
                                    required=True, )
    price_unit = fields.Float('Unit Price', required=False, digits='Product Price', default=0.0)
