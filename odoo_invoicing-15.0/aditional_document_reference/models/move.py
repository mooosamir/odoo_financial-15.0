from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    aditional_document_reference = fields.Char(string='Otro tipo de documento')

    related_tax_documents_code = fields.Selection([
        ('01', "Factura - emitida para corregir error en el RUC"),
        ('02', "Factura - emitida por anticipos"),
        ('03', "Boleta de venta - Emitida por anticipos"),
        ('04', "Ticket de salida - ENAPU"),
        ('05', "Código SCOP"),
        ('06', "Factura electrónica remitente"),
        ('07', "Guía de remisión remitente"),
        ('08', "Declaración de salida del depósito franco"),
        ('09', "Declaración simplificada de importación"),
        ('10', "Liquidación de compra - emitida por anticipos"),
        ('99', "Otros"),
    ], string='Código de documentos relacionados tributarios')


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    @api.model
    def carrier_reference_update_template_base(self):
        l10n_pe_template_base = self.env.ref('l10n_pe_edi.pe_ubl_2_1_common')
        for content in l10n_pe_template_base.inherit_children_ids:
            if content.name == 'pe_ubl_2_1_invoice_body_inherit_l10n_pe_edocument_carrier_ref':
                content.arch_base = '''
                <data inherit_id="l10n_pe_edi.pe_ubl_2_1_common">
                        <xpath expr="//*[name()='cac:Signature']" position="before">
                            <t xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
                                <t t-if="record.carrier_ref_number and not record.exist_advance">
                                    <cac:DespatchDocumentReference>
                                        <cbc:ID t-esc="(str(record.carrier_ref_number).replace(' ', ''))[:30]"/>
                                        <cbc:DocumentTypeCode listAgencyName="PE:SUNAT"
                                                              listName="Tipo de Documento"
                                                              listURI="urn:pe:gob:sunat:cpe:see:gem:catalogos:catalogo01">09</cbc:DocumentTypeCode>
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
                l10n_pe_template_remove = self.env.ref('aditional_document_reference.pe_ubl_2_1_invoice_aditional_document')
                l10n_pe_template_remove.arch_base = '''
                <data inherit_id="l10n_pe_edi.pe_ubl_2_1_common">
                        <xpath expr="//*[name()='cac:Signature']" position="before"/>
                    </data>
                '''
