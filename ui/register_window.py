import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QGraphicsDropShadowEffect, QAction, QIcon

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.operations import register

class RegisterWindow(QMainWindow):
    def __init__(self, show_login_callback):
        super().__init__()
        self.show_login_callback = show_login_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("APEX — Регистрация")
        self.setFixedSize(420, 720)
        
        # Пути к иконкам
        img_dir = Path(__file__).parent.parent / "img"
        self.open_eye_icon = QIcon(str(img_dir / "open-eye.png"))
        self.close_eye_icon = QIcon(str(img_dir / "close-eye.png"))
        
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QLabel { color: #73A15D; font-family: 'Alegreya', 'Times New Roman', serif; }
            QLabel#title { font-size: 32px; font-weight: bold; letter-spacing: 1px; }
            QLineEdit, QComboBox {
                background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 12px;
                padding: 14px 45px 14px 18px; font-size: 15px; color: #333333;
                font-family: 'Alegreya', 'Times New Roman', serif;
            }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #73A15D; }
            QPushButton#btn-register {
                background-color: #73A15D; color: white; border: none; border-radius: 12px;
                padding: 14px 40px; font-size: 16px; font-weight: bold;
                font-family: 'Alegreya', 'Times New Roman', serif;
            }
            QPushButton#btn-register:hover { background-color: #638F4D; }
            QPushButton#btn-register:pressed { background-color: #557A42; }
            QLabel#link { color: #73A15D; font-size: 14px; font-family: 'Alegreya', serif; }
            QLabel#link a { color: #73A15D; text-decoration: underline; }
            QLabel#link a:hover { color: #557A42; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 30, 40, 40)
        layout.setSpacing(10)

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
        
        layout.addSpacing(15)
        
        title = QLabel("РЕГИСТРАЦИЯ")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(25)

        # Поля ввода
        self.input_lastname = QLineEdit()
        self.input_lastname.setPlaceholderText("Введите фамилию")
        layout.addWidget(self.input_lastname)

        self.input_firstname = QLineEdit()
        self.input_firstname.setPlaceholderText("Введите имя")
        layout.addWidget(self.input_firstname)

        self.input_middlename = QLineEdit()
        self.input_middlename.setPlaceholderText("Введите отчество")
        layout.addWidget(self.input_middlename)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Введите email")
        layout.addWidget(self.input_email)

        # Пароль 1
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.eye_action_pass = self.input_password.addAction(self.close_eye_icon, QLineEdit.TrailingPosition)
        self.eye_action_pass.triggered.connect(lambda: self._toggle_password(self.input_password, self.eye_action_pass))
        layout.addWidget(self.input_password)

        # Пароль 2 (Подтверждение)
        self.input_confirm = QLineEdit()
        self.input_confirm.setPlaceholderText("Подтвердите пароль")
        self.input_confirm.setEchoMode(QLineEdit.Password)
        self.eye_action_confirm = self.input_confirm.addAction(self.close_eye_icon, QLineEdit.TrailingPosition)
        self.eye_action_confirm.triggered.connect(lambda: self._toggle_password(self.input_confirm, self.eye_action_confirm))
        layout.addWidget(self.input_confirm)

        # Роль
        self.input_role = QComboBox()
        self.input_role.addItem("Выберите вашу роль")
        self.input_role.addItem("спортсмен")
        self.input_role.addItem("тренер")
        self.input_role.addItem("врач")
        self.input_role.setCurrentIndex(0)
        layout.addWidget(self.input_role)

        # Направление
        self.input_specialization = QLineEdit()
        self.input_specialization.setPlaceholderText("Введите ваше направление")
        layout.addWidget(self.input_specialization)

        layout.addSpacing(15)

        # Кнопка
        self.btn_register = QPushButton("Зарегистрироваться")
        self.btn_register.setObjectName("btn-register")
        self.btn_register.clicked.connect(self.handle_register)
        layout.addWidget(self.btn_register)

        layout.addSpacing(10)

        link_label = QLabel("Уже есть аккаунт? <a href='#'>Войти</a>")
        link_label.setObjectName("link")
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setTextFormat(Qt.RichText)
        link_label.linkActivated.connect(self.go_to_login)
        layout.addWidget(link_label)

        layout.addStretch()

    def _toggle_password(self, line_edit, action):
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal)
            action.setIcon(self.open_eye_icon)
        else:
            line_edit.setEchoMode(QLineEdit.Password)
            action.setIcon(self.close_eye_icon)

    def handle_register(self):
        last_name = self.input_lastname.text().strip()
        first_name = self.input_firstname.text().strip()
        middle_name = self.input_middlename.text().strip() or None
        email = self.input_email.text().strip()
        password = self.input_password.text()
        confirm = self.input_confirm.text()
        role = self.input_role.currentText()
        spec = self.input_specialization.text().strip()

        self.reset_errors()

        if not all([last_name, first_name, email, password, confirm, spec]):
            self.show_error("Заполните все обязательные поля")
            return
        if role == "Выберите вашу роль":
            self.input_role.setStyleSheet("border: 2px solid #E74C3C; background-color: #FFFFFF; border-radius: 12px; padding: 14px 18px;")
            return

        success, message, data = register(last_name, first_name, middle_name, email, password, confirm, role, spec)

        if success:
            self.show_success("Регистрация успешна! Переход к входу...")
            self.show_login_callback()
        else:
            self.show_error(message)

    def reset_errors(self):
        for widget in self.findChildren(QLineEdit):
            widget.setStyleSheet("")
        self.input_role.setStyleSheet("")

    def show_error(self, message):
        print(f"❌ Ошибка: {message}")
        # Подсветка можно добавить позже, пока логирование

    def show_success(self, message):
        print(f"✅ {message}")

    def go_to_login(self):
        self.show_login_callback()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFontDatabase
    
    app = QApplication(sys.argv)
    font_path = Path(__file__).parent.parent / "fonts" / "Alegreya-Regular.ttf"
    if font_path.exists():
        QFontDatabase.addApplicationFont(str(font_path))
    
    window = RegisterWindow(lambda: print("Переход к логину"))
    window.show()
    sys.exit(app.exec())