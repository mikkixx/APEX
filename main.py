import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont
from ui.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)
    # Без setQuitOnLastWindowClosed(False) — приложение корректно завершается
    # когда закрывается последнее окно. Навигация между окнами теперь
    # сначала показывает новое окно, потом закрывает старое — Qt не видит
    # момента «0 открытых окон» и процесс не зависает.

    font_id = QFontDatabase.addApplicationFont("fonts/Alegreya-Regular.ttf")
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 11))

    app.setStyleSheet("""
        QWidget {
            background-color: #ffffff;
            color: #1a1a1a;
        }
        QLineEdit {
            border: 1.5px solid #cccccc;
            border-radius: 20px;
            padding: 10px 16px;
            font-size: 20px;
            background: #f9f9f9;
        }
        QLineEdit:focus {
            border: 1.5px solid #1a1a1a;
            background: #ffffff;
        }
        QPushButton {
            background-color: #1a1a1a;
            color: #ffffff;
            border-radius: 20px;
            padding: 10px 24px;
            font-size: 20px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #333333;
        }
        QPushButton:pressed {
            background-color: #000000;
        }
        QPushButton#secondary {
            background-color: #ffffff;
            color: #1a1a1a;
            border: 1.5px solid #1a1a1a;
        }
        QPushButton#secondary:hover {
            background-color: #f0f0f0;
        }
        QLabel#link {
            color: #1a1a1a;
            text-decoration: underline;
        }
        QLabel#link:hover {
            color: #555555;
        }
        QComboBox {
            border: 1.5px solid #cccccc;
            border-radius: 20px;
            padding: 10px 16px;
            font-size: 20px;
            background: #f9f9f9;
        }
        QComboBox:focus {
            border: 1.5px solid #1a1a1a;
        }
        QComboBox::drop-down {
            border: none;
            padding-right: 12px;
        }
        QScrollBar:vertical {
            width: 6px;
            background: transparent;
        }
        QScrollBar::handle:vertical {
            background: #cccccc;
            border-radius: 3px;
        }
        QTextEdit {
            border: 1.5px solid #cccccc;
            border-radius: 20px;
            padding: 10px 14px;
            font-size: 20px;
            background: #f9f9f9;
        }
        QSpinBox, QDoubleSpinBox {
            border: 1.5px solid #cccccc;
            border-radius: 20px;
            padding: 10px 16px;
            font-size: 16px;
            background: #f9f9f9;
        }
        QDateEdit {
            border: 1.5px solid #cccccc;
            border-radius: 20px;
            padding: 10px 16px;
            font-size: 20px;
            background: #f9f9f9;
        }
        QMessageBox {
            font-family: "Alegreya";
            font-size: 18px;
        }
        QMessageBox QLabel {
            font-family: "Alegreya";
            font-size: 18px;
        }
        QMessageBox QPushButton {
            font-family: "Alegreya";
            font-size: 18px;
            padding: 8px 16px;
        }
    """)

    window = LoginWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
