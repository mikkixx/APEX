import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PySide6.QtGui import QFont, QPixmap, QFontDatabase
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.operations import register

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
        self._base_width = 280
        self._base_height = 60
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


class RegisterWindow(QMainWindow):
    def __init__(self, show_login_callback=None):
        super().__init__()
        _ensure_font_loaded()
        self.show_login_callback = show_login_callback
        self.init_ui()

    def init_ui(self):
        self.showMaximized()
        self.setWindowTitle("APEX — Регистрация")
        
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QLabel { color: #73A15D; }
            QLabel#title { font-size: 48px; font-weight: bold; letter-spacing: 2px; }
            QLineEdit {
                background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 20px;
                padding: 15px 20px; font-size: 20px; color: #222222;
            }
            QLineEdit:focus { border: 1px solid #73A15D; }
            QComboBox {
                background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 20px;
                padding: 15px 20px; font-size: 20px; color: #222222;
            }
            QComboBox:focus { border: 1px solid #73A15D; }
            QComboBox::drop-down { border: none; width: 0px; }
            QComboBox::down-arrow { width: 0px; height: 0px; }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 10px;
                font-size: 20px; selection-background-color: #73A15D;
                selection-color: white; color: #222222; outline: none;
            }
            QPushButton#register-btn {
                background-color: #73A15D; color: white; border: none; border-radius: 20px;
                font-size: 24px; font-weight: bold;
            }
            QPushButton#register-btn:hover { background-color: #638F4D; }
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
        main_layout.addSpacing(30)

        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(15)

        title = QLabel("РЕГИСТРАЦИЯ")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)
        form_layout.addSpacing(30)

        self.input_lastname = QLineEdit(); self.input_lastname.setPlaceholderText("Введите фамилию"); self.input_lastname.setFixedWidth(468); form_layout.addWidget(self.input_lastname, alignment=Qt.AlignCenter)
        self.input_firstname = QLineEdit(); self.input_firstname.setPlaceholderText("Введите имя"); self.input_firstname.setFixedWidth(468); form_layout.addWidget(self.input_firstname, alignment=Qt.AlignCenter)
        self.input_middlename = QLineEdit(); self.input_middlename.setPlaceholderText("Введите отчество"); self.input_middlename.setFixedWidth(468); form_layout.addWidget(self.input_middlename, alignment=Qt.AlignCenter)
        self.input_email = QLineEdit(); self.input_email.setPlaceholderText("Введите email"); self.input_email.setFixedWidth(468); form_layout.addWidget(self.input_email, alignment=Qt.AlignCenter)
        
        self.input_password = QLineEdit(); self.input_password.setPlaceholderText("Введите пароль"); self.input_password.setEchoMode(QLineEdit.Password); self.input_password.setFixedWidth(468); form_layout.addWidget(self.input_password, alignment=Qt.AlignCenter)
        self.input_confirm = QLineEdit(); self.input_confirm.setPlaceholderText("Подтвердите пароль"); self.input_confirm.setEchoMode(QLineEdit.Password); self.input_confirm.setFixedWidth(468); form_layout.addWidget(self.input_confirm, alignment=Qt.AlignCenter)

        self.combo_role = QComboBox()
        self.combo_role.addItem("Выберите вашу роль"); self.combo_role.addItem("спортсмен"); self.combo_role.addItem("тренер"); self.combo_role.addItem("врач")
        self.combo_role.setFixedWidth(468); form_layout.addWidget(self.combo_role, alignment=Qt.AlignCenter)

        self.input_spec = QLineEdit(); self.input_spec.setPlaceholderText("Введите ваше направление"); self.input_spec.setFixedWidth(468); form_layout.addWidget(self.input_spec, alignment=Qt.AlignCenter)

        form_layout.addSpacing(20)
        self.btn_register = SmoothButton("Зарегистрироваться")
        self.btn_register.setObjectName("register-btn")
        self.btn_register.clicked.connect(self.handle_register)
        form_layout.addWidget(self.btn_register, alignment=Qt.AlignCenter)
        form_layout.addSpacing(15)

        self.link_label = QLabel('Уже есть аккаунт? <a href="#" style="color:#73A15D;">Войти</a>')
        self.link_label.setObjectName("link"); self.link_label.setAlignment(Qt.AlignCenter); self.link_label.setTextFormat(Qt.RichText); self.link_label.linkActivated.connect(self.go_to_login)
        form_layout.addWidget(self.link_label, alignment=Qt.AlignCenter)

        main_layout.addStretch()
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    def handle_register(self):
        last_name = self.input_lastname.text().strip()
        first_name = self.input_firstname.text().strip()
        middle_name = self.input_middlename.text().strip() or None
        email = self.input_email.text().strip()
        password = self.input_password.text()
        confirm = self.input_confirm.text()
        role = self.combo_role.currentText()
        spec = self.input_spec.text().strip()

        if not all([last_name, first_name, email, password, confirm, spec]):
            self._show_msg("Внимание", "Заполните все обязательные поля", QMessageBox.Warning); return
        if role == "Выберите вашу роль":
            self._show_msg("Внимание", "Выберите роль", QMessageBox.Warning); return

        success, message, _ = register(last_name, first_name, middle_name, email, password, confirm, role, spec)

        if success:
            if self.show_login_callback:
                self.show_login_callback()
            else:
                from ui.login_window import LoginWindow
                self.login_win = LoginWindow()
                self.login_win.show()
            self.close()
            QTimer.singleShot(50, self._show_success_msg)
        else:
            self._show_msg("Ошибка", message, QMessageBox.Critical)

    def _show_success_msg(self):
        msg = QMessageBox()
        msg.setWindowTitle("Успех")
        msg.setText("Регистрация прошла успешно!\nВойдите в систему.")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox { background-color: #FFFFFF; font-size: 16px; }
            QLabel { color: #333333; }
            QPushButton { background-color: #73A15D; color: white; border: none; border-radius: 10px; padding: 8px 24px; font-weight: bold; }
            QPushButton:hover { background-color: #638F4D; }
        """)
        msg.exec()

    def _show_msg(self, title, text, icon):
        msg = QMessageBox(self)
        msg.setWindowTitle(title); msg.setText(text); msg.setIcon(icon)
        msg.setStyleSheet("""
            QMessageBox { background-color: #FFFFFF; font-size: 16px; }
            QLabel { color: #333333; }
            QPushButton { background-color: #73A15D; color: white; border: none; border-radius: 10px; padding: 8px 24px; font-weight: bold; }
            QPushButton:hover { background-color: #638F4D; }
        """)
        msg.exec()

    def go_to_login(self):
        if self.show_login_callback:
            self.show_login_callback()
        else:
            from ui.login_window import LoginWindow
            self.login_win = LoginWindow()
            self.login_win.show()
            self.hide()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec())