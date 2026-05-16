import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QGraphicsDropShadowEffect, QAction, QIcon
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.operations import login

class LoginWindow(QMainWindow):
    def __init__(self, show_register_callback):
        super().__init__()
        self.show_register_callback = show_register_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("APEX — Вход")
        self.setFixedSize(420, 580)
        
        # Пути к иконкам
        img_dir = Path(__file__).parent.parent / "img"
        self.open_eye_icon = QIcon(str(img_dir / "open-eye.png"))
        self.close_eye_icon = QIcon(str(img_dir / "close-eye.png"))
        
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QLabel { color: #73A15D; font-family: 'Alegreya', 'Times New Roman', serif; }
            QLabel#title { font-size: 32px; font-weight: bold; letter-spacing: 1px; }
            QLineEdit {
                background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
                padding: 14px 45px 14px 18px; font-size: 15px; color: #333333;
                font-family: 'Alegreya', 'Times New Roman', serif;
            }
            QLineEdit:focus { border: 2px solid #73A15D; }
            QPushButton#btn-login {
                background-color: #111111; color: white; border: none; border-radius: 12px;
                padding: 14px 40px; font-size: 16px; font-weight: bold;
                font-family: 'Alegreya', 'Times New Roman', serif;
            }
            QPushButton#btn-login:hover { background-color: #333333; }
            QPushButton#btn-login:pressed { background-color: #000000; }
            QLabel#link { color: #73A15D; font-size: 14px; font-family: 'Alegreya', serif; }
            QLabel#link a { color: #73A15D; text-decoration: underline; }
            QLabel#link a:hover { color: #557A42; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        # Логотип
        logo_path = Path(__file__).parent.parent / "img" / "logo.png"
        logo_label = QLabel()
        if logo_path.exists():
            logo_label.setPixmap(QPixmap(str(logo_path)).scaledToWidth(120, Qt.SmoothTransformation))
        else:
            logo_label.setText("APEX")
            logo_label.setStyleSheet("color: #73A15D; font-size: 32px; font-weight: bold;")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        layout.addSpacing(30)
        
        title = QLabel("ВХОД")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(30)

        # Поле Email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Введите email")
        self._add_shadow(self.input_email)
        layout.addWidget(self.input_email)

        # Поле Пароль с иконкой ВНУТРИ
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setEchoMode(QLineEdit.Password)
        
        # Действие-глаз (изначально перечёркнутый, т.к. пароль скрыт)
        self.eye_action = self.input_password.addAction(self.close_eye_icon, QLineEdit.TrailingPosition)
        self.eye_action.triggered.connect(self.toggle_password)
        
        self._add_shadow(self.input_password)
        layout.addWidget(self.input_password)

        layout.addSpacing(20)

        # Кнопка Войти
        self.btn_login = QPushButton("Войти")
        self.btn_login.setObjectName("btn-login")
        self.btn_login.clicked.connect(self.handle_login)
        self._add_shadow(self.btn_login)
        layout.addWidget(self.btn_login)

        layout.addSpacing(15)

        # Ссылка на регистрацию
        link_label = QLabel("Нет аккаунта? <a href='#'>Зарегистрироваться</a>")
        link_label.setObjectName("link")
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setTextFormat(Qt.RichText)
        link_label.linkActivated.connect(self.go_to_register)
        layout.addWidget(link_label)

        layout.addStretch()

    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(Qt.black)
        widget.setGraphicsEffect(shadow)

    def toggle_password(self):
        if self.input_password.echoMode() == QLineEdit.Password:
            self.input_password.setEchoMode(QLineEdit.Normal)
            self.eye_action.setIcon(self.open_eye_icon)
        else:
            self.input_password.setEchoMode(QLineEdit.Password)
            self.eye_action.setIcon(self.close_eye_icon)

    def handle_login(self):
        email = self.input_email.text().strip()
        password = self.input_password.text()

        if not email or not password:
            self.show_error("Заполните поля email и пароль")
            return

        success, message, user_data = login(email, password)

        if success:
            self.close()
            print(f"✅ Вход выполнен: {user_data}")
            # Здесь будет вызов главного окна: self.main_window = MainWindow(user_data); self.main_window.show()
        else:
            self.show_error(message)

    def show_error(self, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Ошибка входа")
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: white; font-family: 'Alegreya', serif; }
            QLabel { color: #333333; font-family: 'Alegreya', serif; }
            QPushButton { background-color: #73A15D; color: white; border: none; border-radius: 8px; padding: 8px 20px; font-weight: bold; }
            QPushButton:hover { background-color: #638F4D; }
        """)
        msg_box.exec()

    def go_to_register(self):
        self.show_register_callback()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font_path = Path(__file__).parent.parent / "fonts" / "Alegreya-Regular.ttf"
    if font_path.exists():
        from PySide6.QtGui import QFontDatabase
        QFontDatabase.addApplicationFont(str(font_path))
    
    window = LoginWindow(lambda: print("Переход к регистрации"))
    window.show()
    sys.exit(app.exec())