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

from openerp import fields, api, exceptions, models


class mrp_product_produce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    def _get_lot_id(self, cr, uid, context=None):
        prod=False
        if context and context.get("active_id"):
            prod = self.pool.get('mrp.production').browse(cr, uid,
                                    context['active_id'], context=context)
            return prod and prod.mrp_lot_id.id or False

    _defaults = {
        'lot_id': _get_lot_id
    }

    @api.multi
    def do_produce(self):
        self._context
        if self._context and self._context.get("active_id"):

            prod = self.env['mrp.production'].browse(self._context['active_id'])
            data = self.browse(self.ids[0])
            print data
            if prod.mrp_lot_id and data.lot_id.id != prod.mrp_lot_id.id:
                raise exceptions.ValidationError("You can't change the lot ID already created in the production order")
        return super(mrp_product_produce, self).do_produce()