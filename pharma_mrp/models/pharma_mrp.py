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

from openerp import models, api, exceptions, fields


class PharmaMRP(models.Model):

    _inherit = 'mrp.production'

    mrp_lot_id = fields.Many2one('stock.production.lot', string="Lot ID", copy=False)
    qc_lot_id = fields.Many2one('stock.production.lot', string="Test Lot ID", copy=False)

    _defaults = {
        'name': '/',
    }

    @api.one
    def action_generate_lot(self):
        if not self.product_id.lot_code_id:
            raise exceptions.MissingError("You Must Set Lot Code ID for This Product First!")
        code = self.product_id.lot_code_id.get_next()[0]
        lot = self.env['stock.production.lot'].create({'name': code, 'product_id': self.product_id.id, 'ref': code})
        self.mrp_lot_id = lot
        # self.write({'mrp_lot_id': self.product_id.lot_code_id.get_next()[0]})

    def action_confirm(self, cr, uid, ids, context=None):
        for production in self.browse(cr, uid, ids, context):
            if production.product_id.production_type == 'MO' and not production.mrp_lot_id:
                raise exceptions.ValidationError('This Production Order Must have a lot number, '
                                                 'click on create button to generate a new one')

        return super(PharmaMRP, self).action_confirm(cr, uid, ids, context)

    def create(self, cr, uid, vals, context={}):
        product= self.pool.get('product.product').browse(cr, uid, vals['product_id'], context)
        production_type = product.production_type
        if production_type == 'MO' or not production_type:
            sequences = self.pool.get('ir.sequence').get(cr, uid, 'mrp.production')
            vals['name'] = sequences
            # if not vals['mpr_lot_id']:
            #     raise exceptions.ValidationError("This Production Order must have a Lot ID")
        else:
            code = 'mrp.production.' + str(production_type).lower()
            sequences = self.pool.get('ir.sequence').get(cr, uid, code)
            vals['name'] = sequences
        print vals
        res_id = super(PharmaMRP, self).create(cr, uid, vals, context)
        return res_id


class PharmaProduct(models.Model):

    _inherit = 'product.template'

    production_type = fields.Selection(selection=[('QCO', 'Quality Control'),
                                                  ('MO', 'Production'),
                                                  ('MBO', 'Micro-Biology'),
                                                  ('MPO', 'Media Preparation')])

    lot_code_id = fields.Many2one('pharma.codification.lot', string="Production/Reception Lot Codification")

    reference_rate = fields.Float(string='TR', digits=(16, 2))
    public_algerian_price = fields.Float(string='PPA', digits=(16, 2))
    shp_rate = fields.Float(string='SHP Rate', digits=(16, 2))
    active_principal = fields.Char(string='Active Principal')
    product_dose = fields.Char(string='Product Dose')
    de_reference = fields.Char(string='DE Reference')


class StockLot(models.Model):
    _inherit = 'stock.production.lot'

    def create(self, cr, uid, vals, context):
        print vals
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'], context)[0]
            print product
            if product.lot_code_id:
                code = product.lot_code_id.get_next()[0]
                if 'name' in vals and vals['name'] != None:
                    if not 'ref' in vals:
                        vals['ref'] = code
                else:
                    vals['name'] = code
                    vals['ref'] = code

        return super(StockLot, self).create(cr, uid, vals, context)