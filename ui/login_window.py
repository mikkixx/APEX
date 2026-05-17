from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APEX — Вход")
        self.setMinimumSize(480, 580)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Logo at top center
        top = QHBoxLayout()
        top.setContentsMargins(0, 32, 0, 0)
        top.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        logo = QLabel()
        pix = QPixmap("img/logo.png")
        if not pix.isNull():
            logo.setPixmap(pix.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("APEX")
            logo.setStyleSheet("font-size: 48px; font-weight: bold;")
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        top.addWidget(logo)
        root.addLayout(top)

        root.addStretch(1)

        # Form
        form_wrapper = QHBoxLayout()
        form_wrapper.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        form = QVBoxLayout()
        form.setSpacing(12)
        form.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        title = QLabel("ВХОД")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 2px; margin-bottom: 16px;")
        form.addWidget(title)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введите email")
        self.email_input.setFixedWidth(380)
        self.email_input.setFixedHeight(48)
        form.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(380)
        self.password_input.setFixedHeight(48)
        form.addWidget(self.password_input)

        login_btn = QPushButton("Войти")
        login_btn.setFixedWidth(220)
        login_btn.setFixedHeight(48)
        login_btn.clicked.connect(self._on_login)
        self.password_input.returnPressed.connect(self._on_login)
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        btn_row.addWidget(login_btn)
        form.addLayout(btn_row)

        reg_row = QHBoxLayout()
        reg_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        no_acc = QLabel("Нет аккаунта?")
        no_acc.setStyleSheet("font-size: 20px; color: #555;")
        reg_link = QLabel("Зарегистрироваться")
        reg_link.setObjectName("link")
        reg_link.setStyleSheet("font-size: 20px; color: #1a1a1a; text-decoration: underline;")
        reg_link.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_link.mousePressEvent = lambda e: self._go_register()
        reg_row.addWidget(no_acc)
        reg_row.addSpacing(4)
        reg_row.addWidget(reg_link)
        form.addLayout(reg_row)

        form_wrapper.addLayout(form)
        root.addLayout(form_wrapper)

        root.addStretch(2)

    def _on_login(self):
        from core.operations import login
        email = self.email_input.text().strip()
        password = self.password_input.text()
        ok, msg, user_data = login(email, password)
        if ok:
            self._open_main(user_data)
        else:
            QMessageBox.warning(self, "Ошибка входа", msg)

    def _open_main(self, user_data):
        from ui.training_plan_window import TrainingPlanWindow
        self.main_win = TrainingPlanWindow(user_data)
        self.main_win.show()
        self.close()

    def _go_register(self):
        from ui.register_window import RegisterWindow
        self.reg_win = RegisterWindow()
        self.reg_win.show()
        self.close()
