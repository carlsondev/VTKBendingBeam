import sys
from threading import Thread
from PyQt5.QtWidgets import QApplication

from pyqtconsole.console import PythonConsole

app = QApplication([])
console = PythonConsole()
console.show()
console.eval_in_thread()
console.insert_input_text('\n', show_ps=False)
console.process_input("from ConsoleInterface import *\n")

sys.exit(app.exec_())