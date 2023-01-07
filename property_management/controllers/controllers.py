# -*- coding: utf-8 -*-
# from odoo import http


# class PropertyManagement(http.Controller):
#     @http.route('/property_management/property_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/property_management/property_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('property_management.listing', {
#             'root': '/property_management/property_management',
#             'objects': http.request.env['property_management.property_management'].search([]),
#         })

#     @http.route('/property_management/property_management/objects/<model("property_management.property_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('property_management.object', {
#             'object': obj
#         })
