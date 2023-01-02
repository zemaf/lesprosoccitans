from fbs_runtime.application_context.PySide6 import ApplicationContext

# on import os pour pouvoir insérer des lignes de commande
# => utliser la commande "spctl —master-disable/enable" pour autoriser installation toute appli sur mac
import os
import sys

from package.mainwindow import MainWindow

if __name__ == '__main__':
    # os.system('ls -lah')
    # os.system('spctl —master-enable')
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = MainWindow()
    window.resize(400, 400)
    window.show()
    exit_code = appctxt.app.exec()      # 2. Invoke appctxt.app.exec()
    sys.exit(exit_code)
