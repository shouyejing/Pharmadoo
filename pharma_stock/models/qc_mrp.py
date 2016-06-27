# -*- encoding: utf-8 -*-

from openerp import models, api, exceptions, fields


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer(self):
        for item in self.item_ids:
            if not item.lot_id.is_validated and item.sourceloc_id.id in (21, 31):
                raise exceptions.ValidationError('The lot Number %s has not yet been Validated' % item.lot_id.name)
        for pack in self.packop_ids:
            for quant in pack.package_id.quant_ids:
                if not quant.lot_id.is_validated and pack.sourceloc_id.id in (21, 31):
                    raise exceptions.ValidationError('The lot number %s (pack number %s) has not yet been Validated' % (quant.lot_id.name, pack.package_id.name))
        super(StockTransferDetails, self).do_detailed_transfer()


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.model
    def cron_create_qc_mrp(self):

        """
        Generate manufacturing order for each item in the stock picking list
        where the source location is the QC location and the result will be in a Virtual location
        for quality control tests.
        """

        release_materials_type = self.env.ref('pharma_stock.pharma_release_materials_picking_type')

        qc_product_attribute = self.env.ref('pharma_stock.pharma_qc_product_attribute')

        picking_ids = self.search([('picking_type_id', '=', release_materials_type.id),
                                   ('state', '=', 'assigned')])

        mrp_obj = self.env['mrp.production']
        bom_obj = self.env['mrp.bom']
        partner_ids = [user.partner_id.id for user in self.env.ref('pharma_security.pharmadoo_qc_manager').users]
        partner_ids.append([user.partner_id.id for user in self.env.ref('pharma_security.pharmadoo_qc_anlyst').users])
        print partner_ids
        subject = "QC Test Creation"

        for picking in picking_ids:
            mo_exist = self.env['mrp.production'].search([('origin', '=', picking.name)])
            if len(mo_exist) == 0:
                for line in picking.move_lines:
                    product_value_ids = self.env['product.attribute.value'].\
                        search([('attribute_id', '=', qc_product_attribute.id), ('name', '=', line.product_id.name)])
                    for product_value in product_value_ids:
                        product_ids = self.env['product.product'].search([('attribute_value_ids', '=', product_value.id)])
                        for product in product_ids:
                            if len(line.reserved_quant_ids):
                                current_lot = line.reserved_quant_ids[0].lot_id
                                bom_ids = bom_obj.search([('product_id', '=', product.id)])
                                if len(bom_ids) > 0:
                                    mo_order_values = {
                                        'product_id': product.id,
                                        'scheduled_date': fields.datetime.today(),
                                        'product_qty': 1,
                                        'product_uom': 1,
                                        'location_src_id': picking.location_id.id,
                                        'location_dist_id': picking.location_id.id,
                                        'bom_id': bom_ids[0].id,
                                        'origin': picking.name,
                                        'qc_lot_id': current_lot.id
                                    }
                                    mo_order = mrp_obj.create(mo_order_values)
                                    message = "The System has created a manufacturing order: <b>" + \
                                              mo_order.name.encode('utf-8') + \
                                              "</b> for the product <b>" + product.name.encode('utf-8') + \
                                              "</b>, with the lot number: <b>" + \
                                              current_lot.name.encode('utf-8') + "</b>."

                                    picking.message_post(subject=subject,
                                                         body=message,
                                                         message_type='notification',
                                                         partner_ids=partner_ids)
                                else:
                                    message = "The Product <b>" + product.name.encode('utf-8') + \
                                              "</b> has no bill of material. Please create a BOM for the product." \
                                              "and create QC order manually"

                                    picking.message_post(subject=subject,
                                                         body=message,
                                                         message_type='notification',
                                                         partner_ids=partner_ids)
                                    break
                                for quant in line.reserved_quant_ids:
                                    if current_lot != quant.lot_id:
                                        current_lot = quant.lot_id
                                        mo_order = mrp_obj.create({
                                            'product_id': product.id,
                                            'scheduled_date': fields.datetime.today(),
                                            'product_qty': 1,
                                            'product_uom': 1,
                                            'location_src_id': picking.location_id.id,
                                            'location_dist_id': picking.location_id.id,
                                            'bom_id': bom_ids[0].id,
                                            'origin': picking.name,
                                            'qc_lot_id': quant.lot_id.id
                                        })

                                        message = "The System has created a manufacturing order: <b>" + \
                                                  mo_order.name.encode('utf-8') + \
                                                  "</b> for the product <b>" + product.name.encode('utf-8') + \
                                                  "</b>, with the lot number: <b>" + \
                                                  current_lot.name.encode('utf-8') + "</b>."
                                        picking.message_post(subject=subject,
                                                             body=message,
                                                             message_type='notification',
                                                             partner_ids=partner_ids)
                            else:
                                message = "The Product <b>" + product.name.encode('utf-8') + \
                                          "</b> has not lot selected yet. Please check the product configuration."
                                picking.message_post(subject=subject,
                                                     body=message,
                                                     message_type='notification',
                                                     partner_ids=partner_ids)
                                break
        return True


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    is_approved = fields.Boolean(string='Is Approved?', default=False)
    is_validated = fields.Boolean(string='Is Validated?', default=False)
    approved_by_usr_id = fields.Many2one('res.users', string='Approved by User')
    validated_by_usr_id = fields.Many2one('res.users', string='Validated by User')
    validated_date = fields.Date(string="Validate Date")
    approved_date = fields.Date(string="Approved Date")
    rejected_date = fields.Date(string="Rejected Date")
    rejected_by_user_id = fields.Many2one('res.users', string='Rejected By')
    exp_retest_date = fields.Date(string="Expiry/Retest Date")
    expiry_date = fields.Date(string="Expiry Date")
    retest_date = fields.Date(string="Retest Date")
    state = fields.Selection(string='State',
                             selection=[('quarantine', 'Quarantine'),
                                        ('approved', 'Approved'),
                                        ('accepted', 'Accepted'),
                                        ('rejected', 'Rejected')],
                             default='quarantine')
    color = fields.Integer(string='Color Index', default='2')

    @api.multi
    def action_approve_picking(self):
        created_id = self.env['pharma.stock.approval'].with_context(active_model=self._name, active_ids=self.ids, active_id=self.ids[0]).create({'lot_id': self.ids[0]})
        return created_id.wizard_view()

    @api.multi
    def action_validate_picking(self):
        created_id = self.env['pharma.stock.validator'].with_context(active_model=self._name, active_ids=self.ids, active_id=self.ids[0]).create({'lot_id': self.ids[0]})
        return created_id.wizard_view()

    @api.multi
    def action_reject(self):
        assert self.ensure_one()
        self.rejected_by_user_id = self.env.user
        self.rejected_date = fields.Date.today()
        self.state = 'rejected'
        self.color = 3
        return True


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    lock_number = fields.Char(string='Lock Number')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    need_qc_tests = fields.Boolean(string='Need QC Tests')

    def add_qc_variant(self):
        # Add the current created product as a variant to the qc product
        if self.need_qc_tests:
            product_obj = self.env['product.product']
            attribute_obj_line = self.env['product.attribute.line']
            attribute_value_obj = self.env['product.attribute.value']

            attribute_line = attribute_obj_line.search([('product_tmpl_id', '=', 185), ('attribute_id', '=', 2)])
            product_value = attribute_value_obj.create({'attribute_id': 2, 'name': self.name})
            attribute_line.update({'value_ids': [(4, product_value.id, attribute_line.id)]})
            product_obj.create({
                'product_tmpl_id': 185,
                'attribute_value_ids': [(6, 0, [product_value.id])]
            })

    @api.model
    def create(self, vals):
        product = super(ProductTemplate, self).create(vals)
        product.add_qc_variant()
        return product
