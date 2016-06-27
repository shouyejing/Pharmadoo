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
    'name': 'Production Order Type',
    'version': '1.0',
    'description': """
Production order type and sequence
==================================================

    """,
    'author': 'Altex-Corp',
    'website': 'http://www.altex-corp.com',
    'category': 'MRP',
    'depends': ['mrp', 'pharma_codification'],
    'data': [
        'views/product_vignette.xml',
        'views/pharma_mrp_view.xml',
        'data/pharma_mrp_data.xml',
        'views/production_working_centers.xml'
    ],
    'demo': [],
    'active': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: