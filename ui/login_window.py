import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QGraphicsDropShadowEffect, QMessageBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont, QPixmap, QFontDatabase
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.operations import login

def _ensure_font_loaded():
    app = QApplication.instance()
    if not app: return
    if "Alegreya" in QFontDatabase.families():
        app.setFont(QFont("Alegreya", 18))
        return
    font_path = Path(__file__).resolve().parent.parent / "fonts" / "Alegreya-Regular.ttf"
    if font_path.exists():
        fid = QFontDatabase.addApplicationFont(str(font_path))
        if fid != -1:
            families = QFontDatabase.applicationFontFamilies(fid)
            if families:
                app.setFont(QFont(families[0], 18))

class SmoothButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._base_width = 250
        self._base_height = 55
        self.setMinimumSize(self._base_width, self._base_height)
        self.setMaximumSize(self._base_width + 15, self._base_height + 5)
        self.size_anim = QPropertyAnimation(self, b"minimumSize")
        self.size_anim.setDuration(300)
        self.size_anim.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        self.size_anim.setStartValue(self.size())
        self.size_anim.setEndValue(QSize(self._base_width + 15, self._base_height + 5))
        self.size_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.size_anim.setStartValue(self.size())
        self.size_anim.setEndValue(QSize(self._base_width, self._base_height))
        self.size_anim.start()
        super().leaveEvent(event)


class LoginWindow(QMainWindow):
    def __init__(self, show_register_callback=None):
        super().__init__()
        _ensure_font_loaded()
        self.show_register_callback = show_register_callback
        self.init_ui()

    def init_ui(self):
        self.showMaximized()
        self.setWindowTitle("APEX — Вход")

        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QLabel { color: #73A15D; }
            QLabel#title { font-size: 48px; font-weight: bold; letter-spacing: 2px; }
            QLineEdit {
                background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 20px;
                padding: 15px 20px; font-size: 20px; color: #222222;
            }
            QLineEdit:focus { border: 1px solid #73A15D; }
            QPushButton#login-btn {
                background-color: #73A15D; color: white; border: none; border-radius: 20px;
                font-size: 24px; font-weight: bold;
            }
            QPushButton#login-btn:hover { background-color: #638F4D; }
            QLabel#link { color: #73A15D; font-size: 18px; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        logo_path = Path(__file__).parent.parent / "img" / "logo.png"
        logo_label = QLabel()
        if logo_path.exists():
            logo_label.setPixmap(QPixmap(str(logo_path)).scaledToWidth(305, Qt.SmoothTransformation))
        else:
            logo_label.setText("APEX")
            logo_label.setStyleSheet("color: #73A15D; font-size: 32px; font-weight: bold;")
        
        main_layout.addWidget(logo_label, alignment=Qt.AlignHCenter)
        main_layout.addSpacing(60)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(25)

        title = QLabel("ВХОД")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)
        form_layout.addSpacing(40)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Введите email")
        self.input_email.setFixedWidth(468)
        self._add_shadow(self.input_email)
        form_layout.addWidget(self.input_email, alignment=Qt.AlignCenter)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setFixedWidth(468)
        self._add_shadow(self.input_password)
        form_layout.addWidget(self.input_password, alignment=Qt.AlignCenter)

        form_layout.addSpacing(30)

        self.btn_login = SmoothButton("Войти")
        self.btn_login.setObjectName("login-btn") 
        self.btn_login.clicked.connect(self.handle_login)
        self._add_shadow(self.btn_login)
        form_layout.addWidget(self.btn_login, alignment=Qt.AlignCenter)

        form_layout.addSpacing(15)

        self.link_label = QLabel('Нет аккаунта? <a href="#" style="color:#73A15D;">Зарегистрироваться</a>')
        self.link_label.setObjectName("link")
        self.link_label.setAlignment(Qt.AlignCenter)
        self.link_label.setTextFormat(Qt.RichText)
        self.link_label.linkActivated.connect(self.go_to_register)
        form_layout.addWidget(self.link_label, alignment=Qt.AlignCenter)

        main_layout.addStretch()
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(7)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(Qt.black)
        widget.setGraphicsEffect(shadow)

    def handle_login(self):
        email = self.input_email.text().strip()
        password = self.input_password.text()

        if not email or not password:
            self.show_message("Внимание", "Заполните поля email и пароль", QMessageBox.Warning)
            return

        success, message, user_data = login(email, password)

        if success:
            self.close()
            print("Вход выполнен успешно:", user_data)
        else:
            self.show_message("Ошибка входа", message, QMessageBox.Critical)

    def go_to_register(self):
        if self.show_register_callback:
            self.show_register_callback()
        else:
            try:
                from ui.register_window import RegisterWindow
                self.register_win = RegisterWindow(show_login_callback=self.show)
                self.register_win.show()
                self.hide()
            except ImportError:
                print("Окно регистрации не найдено.")

    def show_message(self, title, text, icon):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        msg.setStyleSheet("""
            QMessageBox { background-color: #FFFFFF; font-size: 16px; }
            QLabel { color: #333333; }
            QPushButton { 
                background-color: #73A15D; color: white; border: none; 
                border-radius: 10px; padding: 8px 24px; font-weight: bold;
            }
            QPushButton:hover { background-color: #638F4D; }
        """)
        msg.exec()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())