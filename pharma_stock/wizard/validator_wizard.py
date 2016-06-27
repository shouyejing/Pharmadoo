# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, api, models, exceptions


class PharmaStockValidator(models.TransientModel):

    _name = 'pharma.stock.validator'

    lot_id = fields.Many2one('stock.production.lot', string='Lot ID')
    user = fields.Char(string='User Name')
    user_name = fields.Many2one('res.users', string='User')
    password = fields.Char(string='Password')

    # def default_get(self, cr, uid, fields, context=None):
    #     res = super(PharmaStockValidator, self).default_get(cr, uid, fields, context=context)
    #     res.update(user_name=uid)
    #     return res

    @api.onchange('user')
    def _onchange_name(self):
        res_user_obj = self.env['res.users']
        user = res_user_obj.search([('login', '=', self.user)])
        self.user_name = user[0]

    @api.one
    def do_validate_movement(self):
        print self.user_name.login
        good_group = False
        for group in self.user_name.groups_id:
            if group.name == 'Quality Assurance':
                good_group = True
        if good_group:
            self.user_name.check_credentials(self.password)
            self.lot_id.validated_date = fields.Date.today()
            self.lot_id.validated_by_usr_id = self.user_name.id
            self.lot_id.state = 'accepted'
            self.lot_id.color = 5
            self.lot_id.write({'is_validated': True})
        else:
            raise exceptions.ValidationError("The Entered User Cannot Approve This Document")
        return True

    @api.multi
    def wizard_view(self):
        # #assert the user has credential to validate record
        # if self.lot_id.picking_type_id.validated_by_usr_id.id != self._uid:
        #     raise exceptions.ValidationError("This user doesn't have the credential to validate this document")

        #assert the record hasn't been already validated
        if self.lot_id.is_validated:
            raise exceptions.ValidationError('This record has been already validated by user')


        view = self.env.ref('pharma_stock.pharma_stock_validator_form_view')

        return {
            'name': 'Enter Your Password',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pharma.stock.validator',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }