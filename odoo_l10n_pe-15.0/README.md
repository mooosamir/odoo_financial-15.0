# odoo_l10n_pe

----------------------------------------------

* Libraries to install with - apt :
  > apt-get install tesseract-ocr

* To install the file requirements.txt use:
  > pip install -r requirements.txt

base_spot
-
Create additional fields on purchase invoices that allow you to identify if an invoice is affected by legal deductions, the type of deduction, the payment date
of the deduction, and the payment operation code of the deduction.

checkout_balance
-
Creates the trial balance report that includes the income statement by nature and by function. The presentation of this report is at the accounting account
level (two digits) because it uses the groups of accounts to group the information. It also takes advantage of dynamic Odoo queries. (Only for enterprise) See
video:
<a href="https://www.youtube.com/watch?v=FFbXmFLBugs.">https://www.youtube.com/watch?v=FFbXmFLBugs.

code_product_extension
-
It creates fields in the product that allow to identify additional coding in the products for electronic invoicing and electronic books for Peru.

conditional_rate_exchange
-
Add a Boolean to the coins to decide whether to automatically register the rate using the Odoo service. This is very useful, because you can have the automatic
rate update active, however, some currencies may not want to update them through a different service.

dua_in_invoice
-
Add required fields on purchase invoices to register the DUA as required by the electronic purchase record (PLE).

l10n_pe_catalog
-
Create the catalogs established by Peruvian legislation.

l10n_pe_name_sunat
-
Add required fields on purchase invoices to register the DUA as required by the electronic purchase record (PLE).

localization_menu
-
Create the main menus for the Peruvian localization.

ruc_validation_invoice
-
It allows you to control whether a RUC is Active or Ingrained at the time of making a purchase invoice, and if it does not meet both conditions, it does not
allow you to validate the invoice and warns you that the supplier does not meet said condition

ruc_validation_purchase
-
It allows you to control whether a RUC is Active or Ingrained at the time of placing a purchase order, and if it does not meet both conditions, it does not
allow you to confirm the order and warns you that the supplier does not meet said condition"

ruc_validation_sunat
-
Consult RUC, DNI and complete contacts automatically from SUNAT, using a private consultation service <a href="https://apiperu.dev">https://apiperu.dev</a>.

sbs_currency_update
-
Check the SUNAT exchange rate and automatically register them in USD. To obtain the SUNAT exchange rate, a cron automatically consults the exchange rate
registered in the SBS every day and records it in Odoo with the date of the next day.

tributary_information
-
Create two fields in the employee contracts where it is indicated if the worker applies for the double taxation agreement or if he receives income from the 5th
exempt.