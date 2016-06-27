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

from openerp.report import report_sxw
from openerp.osv import osv
import time


class PharmaPackageDoc(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(PharmaPackageDoc, self).__init__(cr, uid, name, context = context)
        self.localcontext.update({
            'time': time,
            'get_product_packs': self.get_product_packs,
        })


    def get_product_packs(self, picking):
        res = {}
        for pack in picking.pack_operation_ids:
            if pack.lot_id.name in res:
                res[pack.lot_id.name] += 1
            else:
                res.update({pack.lot_id.name: 1})
        print res
        return res


class report_pharma_package_doc(osv.AbstractModel):
    _name = 'report.pharma_stock.report_package'
    _inherit = 'report.abstract_report'
    _template = 'pharma_stock.report_package'
    _wrapped_report_class = PharmaPackageDoc