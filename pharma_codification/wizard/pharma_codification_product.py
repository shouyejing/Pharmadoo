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

from openerp import fields, exceptions, models, api

class PharmaProductCodification(models.TransientModel):

    _name = 'pharma.codification.product'

    product_id = fields.Many2one('product.template', string='Product')
    product_dosage = fields.Many2one('pharma.codification.dosage', string="Dosage Form")
    product_family = fields.Many2one('pharma.codification.family', string="Therapeutic Class")
    product_condit = fields.Char(string='Conditioning', size=1)
    product_material = fields.Many2one('pharma.codification.materiel.code', string="Therapeutic Class")

    @api.one
    def generate_product_code(self):

        if not self.product_dosage and not self.product_family and not self.product_condit and not self.product_material:
            raise exceptions.ValidationError("You have to select one of the options "
                                             "above to generate a code for your product")
        elif self.product_dosage and not self.product_family:
            raise exceptions.ValidationError("You must choose a Therapeutic Class for  finished product")

        elif not self.product_dosage and self.product_family:
            raise exceptions.ValidationError("You must choose a Dosage Form for  finished product")

        elif self.product_dosage and self.product_family and self.product_condit:
            if self.product_material:
                raise exceptions.ValidationError("You have to choose between option for finished product or Raw Material"
                                                 " You can't have both selected")
            else:
                code_id = self.env['pharma.codification.product.code'].search([
                    ('dosage_id', '=', self.product_dosage.id),
                    ('family_id', '=', self.product_family.id),
                ])

                print "CODE ID", code_id
                # code = self.env['pharma.codification.product.code'].browse(code_id[0])[0]
                # print code_id[0].padding
                self.product_id.write({'default_code': str(code_id.get_next()[0]) + str(self.product_condit)})
        elif not (self.product_dosage and self.product_family and self.product_condit) and self.product_material:
            self.product_id.write({'default_code': self.product_material.get_next()[0]})
        return True

    @api.multi
    def wizard_view(self):
        view = self.env.ref('pharma_codification.pharma_codification_product_code_form')
        return {
            'name': 'Product Internal Reference Generator',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pharma.codification.product',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }
