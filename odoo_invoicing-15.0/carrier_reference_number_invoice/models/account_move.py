from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    exist_advance = fields.Boolean(compute='_compute_if_exist_advance', store=True)

    def _compute_if_exist_advance(self):
        for p_t in self:
            if 'l10n_pe_advance' in p_t._fields.keys():
                if p_t.l10n_pe_advance:
                    p_t.exist_advance = True
                else:
                    p_t.exist_advance = False


class AccountMove(models.Model):
    _inherit = 'account.move'

    carrier_ref_number = fields.Char('Guía(s) de Remisión')
    exist_advance = fields.Boolean(compute='_compute_exist_advance')

    @api.depends('invoice_line_ids')
    def _compute_exist_advance(self):
        for move in self:
            move.exist_advance = True
            for line in move.invoice_line_ids:
                if line.product_id.exist_advance:
                    move.exist_advance = False


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    @api.model
    def carrier_reference_update_template_base(self):
        l10n_pe_template_base = self.env.ref('l10n_pe_edi.pe_ubl_2_1_common')
        for content in l10n_pe_template_base.inherit_children_ids:
            if content.name == 'pe_ubl_2_1_invoice_aditional_document':
                content.arch_base = '''
                <data inherit_id="l10n_pe_edi.pe_ubl_2_1_common">
                        <xpath expr="//*[name()='cac:Signature']" position="before">
                            <t xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
                                <t t-if="record.carrier_ref_number and not record.exist_advance">
                                    <cac:DespatchDocumentReference>
                                        <cbc:ID t-esc="(str(record.carrier_ref_number).replace(' ', ''))[:30]"/>
                                        <cbc:DocumentTypeCode listAgencyName="PE:SUNAT"
                                                              listName="SUNAT:Identificador de guía relacionada"
                                                              listURI="um:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01">09</cbc:DocumentTypeCode>
                                    </cac:DespatchDocumentReference>
                                </t>
                                <t t-if="record.aditional_document_reference">               
                                    <cac:AdditionalDocumentReference>
                                        <cbc:ID t-esc="record.aditional_document_reference"/>
                                        <cbc:DocumentTypeCode listAgencyName="PE:SUNAT" 
                                                              listName="Documento Relacionado" 
                                                              listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo12" 
                                        t-esc="str(record.related_tax_documents_code).replace('\n', '').replace(' ', '')"/>
                                    </cac:AdditionalDocumentReference>
                                </t>
                            </t>
                        </xpath>
                    </data>
                '''
                l10n_pe_template_remove = self.env.ref('carrier_reference_number_invoice.pe_ubl_2_1_invoice_body_inherit_l10n_pe_edocument_carrier_ref')
                l10n_pe_template_remove.arch_base = '''
                <data inherit_id="l10n_pe_edi.pe_ubl_2_1_common">
                        <xpath expr="//*[name()='cac:Signature']" position="before"/>
                    </data>
                '''
