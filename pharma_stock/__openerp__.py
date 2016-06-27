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

{
    'name': 'Quality Control Order for Raw Materials & Finished Product',
    'version': '1.0',
    'description': """
Quality Control Order for Raw Materials
==================================================
Plan Comptable Algerian

    """,
    'author': 'Altex-Corp',
    'website': 'http://www.altex-corp.com',
    'category': 'Stock',
    'depends': ['stock',
                'product_manufacturer',
                'pharma_security',
                'report',
                'pharma_mrp'],
    'data': [
        #'security/ir.model.access.csv',
        'data/stock_data.xml',
        'views/pharma_stock_view.xml',
        'pharma_stock_data.xml','views/product_view.xml',
        'views/pharma_package_report.xml',
        'views/pharma_package_ticket.xml',
        'views/blocked_accepted_ticket.xml',
        'views/picking_quant.xml',
        'views/stock_picking_view.xml',
        'wizard/approval_view.xml',
        'wizard/validator_view.xml'
    ],
    'demo': [],
    'active': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: