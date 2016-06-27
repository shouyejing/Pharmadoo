# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import fields, exceptions, api, models

LETTERS = {1: 'A', 2: 'B', 3:'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J', 11: 'K', 12: 'L', 13: 'M',
           14: 'N', 15: 'O', 16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T', 21: 'U', 22: 'V', 23: 'W', 24: 'Y', 25: 'X',
           26: 'Z'}


class Dosageform(models.Model):
    _name = "pharma.codification.dosage"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", size=1, required=True)


class FinishedProductFamily(models.Model):
    _name = "pharma.codification.family"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", size=1, required=True)


    def create(self, cr, uid, vals, context):
        if vals['code'] in ('A', 'C', 'E'):
            raise exceptions.ValidationError("You can't have a code with value 'A', 'C' and 'E'")
        return super(FinishedProductFamily, self).create(cr, uid, vals, context)


class FinishedProductConditioning(models.Model):
    _name = "pharma.codification.conditioning"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", size=1, required=True)


class FinishedProductCode(models.Model):
    _name = 'pharma.codification.product.code'

    dosage_id = fields.Many2one('pharma.codification.dosage', string='Dosage Form', required=True)
    family_id = fields.Many2one('pharma.codification.family', string='Therapeutic Class', required=True)
    seq = fields.Integer(string="Sequence", default=1, readonly=1)
    padding = fields.Integer(string="Padding", default=3, readonly=1)

    @api.one
    def get_next(self):
        code = self.family_id.code + self.dosage_id.code + '%%0%sd' % self.padding % self.seq + '/'
        self.seq += 1

        return code


class RawMaterielCode(models.Model):

    _name = "pharma.codification.materiel.code"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", size=2, required=True)
    increment = fields.Char(string="Increment", size=2, default='A', readonly=1)
    seq = fields.Integer(string="Sequence", default=1, readonly=1)
    padding = fields.Integer(string="Padding", default=3, readonly=1)

    @api.one
    def get_next(self):
        code = self.code + self.increment + '%%0%sd' % self.padding % self.seq
        self.seq += 1
        if int(self.seq) > 999:
            next_letter = LETTERS.keys()[LETTERS.values().index(self.increment[0])] + 1
            self.increment = LETTERS[next_letter]
            self.seq = 1

        return code


class LotCode(models.Model):

    _name="pharma.codification.lot"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    increment = fields.Char(string="Increment", default='AA', readonly=1)
    seq = fields.Integer(string="Sequence", default=1, readonly=1)
    padding = fields.Integer(string="Padding", default=3, readonly=1)

    @api.one
    def get_next(self):
        # seq = self.env['ir.sequence'].get(self.sequence.code)
        if self.code:
            code = self.code + self.increment + '%%0%sd' % self.padding % self.seq
        else:
            code = self.increment + '%%0%sd' % self.padding % self.seq
        self.seq += 1
        if int(self.seq) > 999:
            if self.increment[1] == 'Z':
                next_letter = LETTERS.keys()[LETTERS.values().index(self.increment[0])] + 1
                self.increment = LETTERS[next_letter] + LETTERS[1]
            else:
                next_letter = LETTERS.keys()[LETTERS.values().index(self.increment[1])] + 1
                self.increment = str(self.increment[0]) + LETTERS[next_letter]
            self.seq = 1

        return code


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def generate_default_code(self):
        created_id = self.env['pharma.codification.product'].with_context(active_model=self._name, active_ids=self.ids, active_id=self.ids[0]).create({'product_id': self.ids[0]})
        return created_id.wizard_view()


