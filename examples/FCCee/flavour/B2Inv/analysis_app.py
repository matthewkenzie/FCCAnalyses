import sys

from PyQt6.QtWidgets import (
        QWidget, QMainWindow, QApplication)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Test window")

        self.setCentralWidget(QWidget())

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        app.exec()
