# -*- encoding: utf-8 -*-
from openerp import models, fields, api, exceptions


class StockPickingPlannedOperation(models.Model):

    _name = 'stock.picking.planned.operation'

    move_line_id = fields.Many2one(string='Product',
                                   comodel_name='stock.move')

    product_id = fields.Many2one(string='product',
                                 comodel_name='product.product',
                                 related='move_line_id.product_id')

    picking_id = fields.Many2one(string='Picking', comodel_name='stock.picking')

    lot_number = fields.Char(string='Lot ID')

    package_numbers = fields.Integer(string='Number of Packages')

    expiry_date = fields.Date(string='Expiry Date')

    retest_date = fields.Date(string='Retest Date')


class StockPackOperation(models.Model):

    _inherit = 'stock.pack.operation'

    lot_ref = fields.Char(string='Supplier Lot ID', related='lot_id.ref')
    pack_index = fields.Integer(string='Package Index')


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    planned_operation_ids = fields.One2many(string='Planned Operations',
                                            comodel_name='stock.picking.planned.operation',
                                            inverse_name='picking_id')

    received_user_id = fields.Many2one(string='Received By',
                                       comodel_name='res.users')

    @api.one
    def do_transfer(self):
        super(StockPicking, self).do_transfer()
        self.received_user_id = self.env.user
        return True

    @api.multi
    def action_generate_packages(self):

        assert self.ensure_one()

        StockProductionLot = self.env['stock.production.lot']
        StockPackOperation = self.env['stock.pack.operation']
        StockQuantPackage = self.env['stock.quant.package']

        processed_lots = []

        if len(self.pack_operation_ids) > 0:
            lots = []
            result_packages = []

            for operation in self.pack_operation_ids:
                # operation.result_package_id.unlink()
                # operation.lot_id.unlink()
                result_packages.append(operation.result_package_id)
                lots.append(operation.lot_id)
                operation.unlink()

            for lot in lots:
                lot.unlink()
            for pack in result_packages:
                pack.unlink()

        for operation in self.planned_operation_ids:

            if operation.lot_number not in processed_lots:
                code = operation.move_line_id.product_id.lot_code_id.get_next()[0]
                lot = StockProductionLot.create({
                    'name': code,
                    'product_id': operation.move_line_id.product_id.id,
                    'ref': operation.lot_number,
                    'retest_date': operation.retest_date,
                    'expiry_date': operation.expiry_date,
                })
                pack_index = 1
                for item in range(operation.package_numbers):
                    result_package = StockQuantPackage.create(
                        {'location_id': operation.move_line_id.location_dest_id.id})

                    StockPackOperation.create({
                        'result_package_id': result_package.id,
                        'lot_id': lot.id,
                        'product_id': lot.product_id.id,
                        'product_uom_id': operation.move_line_id.product_uom.id,
                        'product_qty': 0,
                        'location_dest_id': operation.move_line_id.location_dest_id.id,
                        'location_id': operation.move_line_id.location_id.id,
                        'picking_id': self.id,
                        'pack_index': pack_index,
                    })
                    pack_index += 1
        return True

    @api.multi
    def print_picking_order(self):
        return self.env['report'].get_action(self, 'stock.report_picking')


class StockPickingQuant(models.Model):

    """
        Stock picking to move entire packages from a location to another.
    """
    _name = 'stock.picking.quant'
    _description = 'Stock Picking for Quants'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    quant_ids = fields.Many2many(string='Quant',
                                 comodel_name='stock.quant',
                                 column1='picking_id',
                                 column2='quant_id')

    date = fields.Datetime(string='Date',
                           copy=False,
                           default=fields.Datetime.now())

    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('confirmed', 'Confirmed'),
                                        ('done', 'Done'),
                                        ('canceled', 'Canceled')],
                             select=True,
                             copy=False,
                             default='draft')

    name = fields.Char(string='Name',
                       required=True,
                       default='/',
                       select=True,
                       readonly=True,
                       copy=False)

    date_done = fields.Datetime(string='Done Date',
                                readonly=True,
                                copy=False,
                                help='The move created from the quant_lines will be set to this date')
    picking_type_id = fields.Many2one(string='Picking Type',
                                      comodel_name='stock.picking.type',
                                      required=True,
                                      select=True)

    move_ids = fields.One2many(string='Moves',
                               comodel_name='stock.move',
                               inverse_name='picking_quant_id')

    location_src_id = fields.Many2one(string='Source Location',
                                      related='picking_type_id.default_location_src_id')
    location_dest_id = fields.Many2one(string='Destination Location',
                                       related='picking_type_id.default_location_dest_id')

    @api.multi
    def action_confirm_picking(self):
        """
            when the picking is confirmed the stock moves are created and set
            to assigned
        """
        self.ensure_one()
        products = dict()
        # Group all the products line together in a dictionary
        for line in self.quant_ids:
            if line.product_id in products:
                products[line.product_id]['qty'] += line.qty
                products[line.product_id]['quant_ids'].append(line.id)
            else:
                products.update({line.product_id: {'qty': line.qty,
                                                   'quant_ids': [line.id]}})

        self._create_move(products)
        self.state = 'confirmed'
        return True

    def _create_move(self, products):

        """
            Create stock move for each product in
            :param products dictionary containing:
            'qty': total quantity of the packs desired to move
            'quant_ids' list of quants selected

        """

        # create the moves for each element in dictionary
        for product in products:
            vals = {
                'name': self.name,
                'product_id': product.id,
                'product_uom_qty': products[product]['qty'],
                'product_uom': product.uom_id.id,
                'location_id': self.picking_type_id.default_location_src_id.id,
                'location_dest_id': self.picking_type_id.default_location_dest_id.id,
                'description': self.name,
                # 'picking_type_id': self.picking_type_id.id,
                'invoice_state': 'none',
                'picking_quant_id': self.id,
                'quant_ids': [(6, False, products[product]['quant_ids'])],

            }
            move = self.env['stock.move'].create(vals)
            move.action_confirm()
            move.action_assign()
            # for quant_id in products[product]['quant_ids']:
            #     move.write({'quant_ids': [(4, quant_id)]})

        return True

    @api.multi
    def action_done_picking(self):
        """
            Process the stock moves created when the picking was confirmed
        """
        StockTransferDetails = self.env['stock.transfer_details']
        assert self.ensure_one()
        for move in self.move_ids:
            transfer_details = StockTransferDetails.with_context({'active_model': 'stock.picking',
                                                                  'active_ids': [move.picking_id.id],
                                                                  'active_id': move.picking_id.id}).\
                                                    create({'picking_id': move.picking_id.id})
            transfer_details.do_detailed_transfer()

        # set the date done
        self.date_done = fields.Datetime.now()
        self.state = 'done'
        return True

    @api.multi
    def action_cancel_picking(self):
        """
        Cancel Picking Quants only in draft and confirmed state
        """
        assert self.ensure_one()

        if self.state == 'draft':
            self.state = 'canceled'
        elif self.state == 'confirmed':
            for move in self.move_ids:
                move.action_cancel()
            self.state = 'canceled'
        return True

    @api.multi
    def print_transfer_documents(self):
        assert self.ensure_one()
        picking_ids = [move.picking_id.id for move in self.move_ids]
        return self.env['stock.picking'].browse(picking_ids).print_picking_order()

    @api.model
    def create(self, vals):
        PickingType = self.env['stock.picking.type']
        if ('name' not in vals) or (vals.get('name') in ('/', False)):
            ptype_id = vals.get('picking_type_id', self.env.context.get('default_picking_type_id', False))
            sequence = PickingType.browse(ptype_id).picking_quant_sequence
            vals['name'] = sequence.get_id(sequence.id, 'id')
        return super(StockPickingQuant, self).create(vals)

    @api.multi
    def unlink(self):
        for picking_quant in self.browse(self.ids):
            if picking_quant.state in ['confirmed', 'done']:
                raise exceptions.ValidationError("This document is in % state and "
                                                 "it can't be cancelled" % picking_quant.state)
        return super(StockPickingQuant, self).unlink()


class StockPickingType(models.Model):

    """
    Inherit stock.picking.type to add picking quant handling
    * use_picking_quant a boolean field  to mark
    if the picking type can be used to move quants
    * functional fields to keep the same behavior as original picking
    """

    _inherit = 'stock.picking.type'

    use_picking_quant = fields.Boolean(string='Use in Picking Quant',
                                       help='True if this quant type can be used in picking quants')

    picking_quant_sequence = fields.Many2one(string='Quant Reference',
                                             comodel_name='ir.sequence')

    count_picking_quant_draft = fields.Integer(string='Dtaft Quants', compute='_compute_total_quants')
    count_picking_quant_confirmed = fields.Integer(string='Dtaft Quants', compute='_compute_total_quants')
    count_picking_quant_done = fields.Integer(string='Dtaft Quants', compute='_compute_total_quants')

    @api.multi
    def _compute_total_quants(self):
        PickingQuant = self.env['stock.picking.quant']
        for picking_type in self.browse(self.ids):
            picking_type.count_picking_quant_draft = 0
            picking_type.count_picking_quant_confirmed = 0
            picking_type.count_picking_quant_done = 0

            picking_quants = PickingQuant.search([('picking_type_id', '=', picking_type.id)])

            for picking_quant in picking_quants:
                if picking_quant.state == 'draft':
                    picking_type.count_picking_quant_draft += 1
                elif picking_quant.state == 'confirmed':
                    picking_type.count_picking_quant_confirmed += 1
                elif picking_quant.state == 'done':
                    picking_type.count_picking_quant_done += 1

        return True


class StockQuant(models.Model):

    _inherit = "stock.quant"

    is_open = fields.Boolean(string='Is Open?', compute='_compute_is_open')

    @api.multi
    def _compute_is_open(self):
        for quant in self.browse(self.ids):
            for move in quant.history_ids:
                if move.location_id == self.env.ref('pharma_stock.pharma_rmw_weighting_location') or \
                   move.location_dest_id == self.env.ref('pharma_stock.pharma_rmw_weighting_location'):
                    quant.is_open = True
                    break
        return True


class StockMove(models.Model):

    _inherit = 'stock.move'

    picking_quant_id = fields.Many2one(string='Picking Quant',
                                       comodel_name='stock.picking.quant')


