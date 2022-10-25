from io import BytesIO
from datetime import date, datetime

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportFinancial(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    @staticmethod
    def get_filename():
        return 'Reporte_Notas_Anexos.xlsx'

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = workbook.add_worksheet('Report de Venta')

        style0 = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'border': 7
        })
        style1 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'border': 7
        })
        style2 = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'font_name': 'Arial',
            'bold': True
        })
        style3 = workbook.add_format({
            'valign': 'vcenter',
            'size': 10,
            'font_name': 'Arial'
        })
        content_number_format_bold = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
            'bold': True
        })
        content_number_format = workbook.add_format({
            'size': 10,
            'num_format': '#,##0.00',
        })
        content_date_format = workbook.add_format({
            'align': 'right',
            'size': 10,
            'num_format': 'dd/mm/yy',
        })

        c = 0
        i = c + 3

        ws.write(0, 0, 'Notas y Anexos de los Estados Financieros', style0)
        ws.write(c + 1, 0, 'De {} a {}'.format(
            date.strftime(self.obj.date_start, '%d/%m/%Y'),
            date.strftime(self.obj.date_end, '%d/%m/%Y')
        ), style0)
        ws.write(c + 2, 0, 'Total General:', style0)

        ws.set_column('A:A', 12)
        ws.set_column('B:B', 10)
        ws.set_column('C:C', 14)
        ws.set_column('D:D', 20)
        ws.set_column('E:E', 17)
        ws.set_column('F:F', 17)
        ws.set_column('G:G', 12)
        ws.set_column('H:H', 12)
        ws.set_column('I:I', 20)
        ws.set_column('J:J', 16)
        ws.set_column('K:K', 5)
        ws.set_column('L:L', 16)
        ws.set_column('M:M', 5.86)
        ws.set_column('N:N', 17)
        ws.set_column('O:O', 12)
        ws.set_column('P:P', 12)
        ws.set_column('Q:Q', 16)
        ws.set_column('R:R', 16)
        ws.set_column('S:S', 16)
        ws.set_column('T:T', 16)
        ws.set_column('U:U', 16)

        ws.write(i, 0, 'Fecha', style1)
        ws.write(i, 1, 'Cuenta', style1)
        ws.write(i, 2, 'Nro. de Doc.', style1)
        ws.write(i, 3, 'Socio', style1)
        ws.write(i, 4, 'N° de Asiento', style1)
        ws.write(i, 5, 'Referencia', style1)
        ws.write(i, 6, 'F. Vencimiento', style1)
        ws.write(i, 7, 'F. Esperada', style1)
        ws.write(i, 8, 'Etiqueta', style1)
        ws.write(i, 9, 'Saldo pendiente', style1)
        ws.write(i, 10, 'Divisa', style1)
        ws.write(i, 11, 'Importe divisa', style1)
        ws.write(i, 12, 'Tasa', style1)
        ws.write(i, 13, 'Saldo Actualizado', style1)
        ws.write(i, 14, 'Ajuste', style1)
        ws.write(i, 15, 'Cuenta Ajuste', style1)

        i += 1

        sum_general_balance = 0
        sum_general_currency = 0

        income_currency_exchange_account_id = self.obj.company_id.income_currency_exchange_account_id.id
        expense_currency_exchange_account_id = self.obj.company_id.expense_currency_exchange_account_id.id
        account_gain = self.obj.env['account.account'].search([('id', '=', income_currency_exchange_account_id)]).code
        account_lose = self.obj.env['account.account'].search([('id', '=', expense_currency_exchange_account_id)]).code

        for k in self.data.keys():
            if self.data[k]:
                head_i = i
                sum_balance = 0
                sum_currency = 0
                ws.write(head_i, 0, k, style2)
                ws.write(head_i, 7, 'Total:', style2)
                i += 1
                adjustment_rate = 0.00
                sum_updated_balance = 0.00
                sum_adjust = 0.00

                for line_data in self.data[k]:
                    date_format = datetime.strptime(line_data.get('date'), '%d/%m/%Y').date()
                    date_maturity = date_format if not line_data.get('date_maturity') else line_data.get('date_maturity')
                    amount_currency = line_data.get('balance', 0.00) if not line_data.get('account_currency') else line_data.get('amount_currency', 0.00)
                    updated_balance = amount_currency * line_data.get('adjustment_rate', 0.00)
                    adjust = updated_balance - line_data.get('balance', 0.00)
                    adjust_account = account_gain if adjust >= 0.00 else account_lose

                    ws.write(i, 0, line_data.get('date', ''), content_date_format)
                    ws.write(i, 1, line_data.get('account', ''), style3)
                    ws.write(i, 2, line_data.get('vat', ''), style3)
                    ws.write(i, 3, line_data.get('partner', ''), style3)
                    ws.write(i, 4, line_data.get('move', ''), style3)
                    ws.write(i, 5, line_data.get('ref', ''), style3)
                    ws.write(i, 6, date_maturity, content_date_format)
                    ws.write(i, 7, line_data.get('expected_pay_date', ''), content_date_format)
                    ws.write(i, 8, line_data.get('name', ''), style3)
                    ws.write(i, 9, line_data.get('balance', 0.00), content_number_format)
                    ws.write(i, 10, line_data.get('name_currency', ''), style3)
                    ws.write(i, 11, amount_currency, content_number_format)
                    #
                    ws.write(i, 12, line_data.get('adjustment_rate', 0.00), content_number_format)
                    ws.write(i, 13, updated_balance, content_number_format)
                    ws.write(i, 14, adjust, content_number_format)
                    ws.write(i, 15, adjust_account, style3)
                    i += 1
                    sum_balance += line_data.get('balance', 0.00)
                    sum_currency += line_data.get('amount_currency', 0.00)
                    adjustment_rate = line_data.get('adjustment_rate', 0.00)
                    sum_updated_balance += updated_balance
                    sum_adjust += adjust

                ws.write(i, 8, 'Total de la subpartida {}:'.format(line_data.get('account', '')), style2)
                ws.write(head_i, 9, sum_balance, content_number_format_bold)
                ws.write(head_i, 11, sum_currency, content_number_format_bold)
                ws.write(head_i, 12, adjustment_rate, content_number_format_bold)
                ws.write(head_i, 13, sum_updated_balance, content_number_format_bold)
                ws.write(head_i, 14, sum_adjust, content_number_format_bold)

                ws.write(i, 9, sum_balance, content_number_format_bold)
                ws.write(i, 11, sum_currency, content_number_format_bold)
                ws.write(i, 12, adjustment_rate, content_number_format_bold)
                ws.write(i, 13, sum_updated_balance, content_number_format_bold)
                ws.write(i, 14, sum_adjust, content_number_format_bold)

                sum_general_balance += sum_balance
                sum_general_currency += sum_currency
                i += 3

        ws.write(c + 2, 9, sum_general_balance, content_number_format)
        ws.write(c + 2, 11, sum_general_currency, content_number_format)

        workbook.close()
        output.seek(0)
        return output.read()
