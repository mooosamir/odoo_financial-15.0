from . import models


def _uninstall_module_complete(cr, registry):
    cr.execute("""UPDATE ir_act_window SET domain = '[]' WHERE name = 'Accounting Dashboard';""")
