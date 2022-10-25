# odoo_invoicing

Repositorio que extiende las funcionalidades de la Aplicacion de Facturacion:

automatic_account_change
-
Se registra una relación entre el diario y la moneda que van a determinar la cuenta por cobrar o pagar a utilizar en los documentos de venta o compra.

account_discount_global
-
Permite realizar descuentos globales en las facturas (account.move)

account_exchange_currency
-
Permite almacenar valores del cambio de Divisa en el account.currency

account_origin_invoice
-
Crea los campos en el account.invoice de Notas de crédito, que permiten identificar el documento que la Nota de crédito o debito están reftificando. Incluye una relación con una factura existente en Odoo, y en caso no existiera, la posibilidad de Ingresar manualmente los valores de "Fecha", "Serie", "Tipo de documento" y "Correlativo", del documento de Origen.

default_sale_journal
-
Crea campo journal sale en el res.partner el cual cargara al asignarse el cliente en la factura

motive_refund
-
Desde un nuevo objeto permite setear el campo motivo de la nota de credito, desde esta o desde el wizard de la factura

print_aditional_comment
-
Añade campo en la configuración de la compañía/multicompañias, aparecerá impreso en la Factura de Venta, encima del campo "Términos y Condiciones".

print_amount_write
-
Este módulo añade el campo Improte en letra en las Facturas (account.invoice), además lo muestra en el formato de impresión

print_document_type_invoice
-
Añade el nombre del tipo de documento de identificación tributario en la factura.

print_invoice_name_yaros
-
Modifica el nombre que aparece en la Factura Impresa para que muestre el concatenado del nombre del diario y la serie y correlativo separado con un guión.

purchase_document_type_validation
-
Este modelo contiene los parametros de validacion para los campos serie y correlativo en las facturas.

sale_document_prefix_and_sequence
-
aprovecha los campos serie y correlativo, para almacenar, la serie y el correlativo que conforman la secuencia."

sequence_restart
-
Reinicia la sequencia cada mes
