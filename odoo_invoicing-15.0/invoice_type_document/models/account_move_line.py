from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    serie_correlative = fields.Char(
        string='Serie-Correlativo',
        compute='_compute_serie_correlative_payment',
        store=True,
    )

    @api.depends('ref', 'name')
    def _compute_serie_correlative_payment(self):
        for move in self:
            if move.move_type in ['in_invoice', 'in_refund', 'in_receipt']:
                move.serie_correlative = move.ref
                for line in move.invoice_line_ids:
                    line.serie_correlative = move.ref
                for line in move.line_ids:
                    line.serie_correlative = move.ref
            elif move.move_type in ['out_invoice', 'out_refund',
                                    'out_receipt'] and not move.journal_id.l10n_latam_use_documents and move.journal_id.type != 'sale':
                return
            elif move.move_type in ['out_invoice', 'out_refund', 'out_receipt']:
                move.serie_correlative = move.name
                for line in move.invoice_line_ids:
                    line.serie_correlative = move.name
                for line in move.line_ids:
                    line.serie_correlative = move.name
            elif move.move_type == 'entry':
                ids = move.line_ids._reconciled_lines()
                if ids:
                    self.env.cr.execute("""SELECT l10n_latam_document_type_id, serie_correlative
                                                FROM account_move_line
                                                WHERE id in %s and serie_correlative is not NULL""", [tuple(ids)])
                    is_document_type = self.env.cr.dictfetchall()
                    if is_document_type:
                        document_type = is_document_type[0]['l10n_latam_document_type_id']
                        serie_correlative = is_document_type[0]['serie_correlative']
                        for id_line in ids:
                            self.env.cr.execute("""SELECT l10n_latam_document_type_id, serie_correlative
                                    FROM account_move_line
                                    WHERE id=%s """, [(id_line)])
                            is_document_type = self.env.cr.dictfetchall()
                            if not is_document_type[0]['l10n_latam_document_type_id']:
                                self._cr.execute("""UPDATE account_move_line
                                                    SET l10n_latam_document_type_id=%s
                                                    WHERE id=%s """,
                                                 (document_type, id_line))
                                self._cr.execute("""UPDATE account_move_line
                                                    SET serie_correlative=%s
                                                    WHERE id=%s """,
                                                 (serie_correlative, id_line))


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    serie_correlative = fields.Char(string='Serie-Correlativo', store=True)
    move_type = fields.Selection(related='move_id.move_type')
    serie_correlative_is_readonly = fields.Boolean(string='Es editable', compute='_compute_serie_correlative_is_readonly', store=True)

    def create(self, vals_list):
        lines = super(AccountMoveLine, self).create(vals_list)
        for line in lines:
            if vals_list and isinstance(vals_list, list) and 'l10n_latam_document_type_id' in vals_list[0].keys():
                doc = self.env['l10n_latam.document.type'].search([('id', '=', vals_list[0]['l10n_latam_document_type_id'])])
                line.l10n_latam_document_type_id = doc
        return lines

    @api.depends('move_id')
    def _compute_serie_correlative_is_readonly(self):
        for rec in self:
            if rec.move_id:
                if rec.move_id.move_type in ['out_invoice', 'out_refund',
                                             'out_receipt'] and not rec.move_id.journal_id.l10n_latam_use_documents and rec.move_id.journal_id.type == 'sale':
                    rec.serie_correlative_is_readonly = False
                elif rec.move_id.move_type == 'entry':
                    rec.serie_correlative_is_readonly = False
                else:
                    rec.serie_correlative_is_readonly = True

    # Extract type of document from the invoices to the other accounting entries
    def reconcile(self):
        res = super(AccountMoveLine, self).reconcile()
        if 'full_reconcile' in res.keys():
            account_reconcile = res['full_reconcile']

            document_type = False
            ids = False
            serie_correlative = False

            for move_line in account_reconcile.reconciled_line_ids:
                if move_line.move_id.move_type != 'entry':
                    if move_line.move_id.l10n_latam_document_type_id and move_line.move_id.serie_correlative:
                        document_type = move_line.move_id.l10n_latam_document_type_id
                        serie_correlative = move_line.move_id.serie_correlative

                else:
                    ids = move_line.move_id.line_ids._reconciled_lines()
            if self.full_reconcile_id:
                for line in self.full_reconcile_id.reconciled_line_ids:
                    if line.serie_correlative and line.l10n_latam_document_type_id:
                        serie_correlative = line.serie_correlative
                        document_type = line.l10n_latam_document_type_id
            if document_type and ids:
                for id_line in ids:
                    self.env.cr.execute("""SELECT l10n_latam_document_type_id 
                        FROM account_move_line
                        WHERE id=%s """, [(id_line)])
                    is_document_type = self.env.cr.dictfetchall()

                    if not is_document_type[0]['l10n_latam_document_type_id']:
                        self._cr.execute("""UPDATE account_move_line
                                            SET l10n_latam_document_type_id=%s
                                            WHERE id=%s """,
                                         (document_type.id, id_line))
                        self._cr.execute("""UPDATE account_move_line
                                            SET serie_correlative=%s
                                            WHERE id=%s """,
                                         (serie_correlative, id_line))
            if self.statement_id:
                if document_type:
                    for line in self.statement_id.line_ids:
                        for move_line in line.move_id.line_ids:
                            if document_type and serie_correlative:
                                move_line.l10n_latam_document_type_id = document_type
                                move_line.serie_correlative = serie_correlative
        return res
