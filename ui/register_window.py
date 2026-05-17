from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QMessageBox, QScrollArea
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


ROLES = ["спортсмен", "тренер", "врач"]


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APEX — Регистрация")
        self.setMinimumSize(520, 700)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        root = QVBoxLayout(container)
        root.setContentsMargins(60, 32, 60, 40)
        root.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.setSpacing(0)

        # Logo
        logo = QLabel()
        pix = QPixmap("img/logo.png")
        if not pix.isNull():
            logo.setPixmap(pix.scaledToHeight(56, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("APEX")
            logo.setStyleSheet("font-size: 48px; font-weight: bold;")
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(logo)
        root.addSpacing(24)

        title = QLabel("РЕГИСТРАЦИЯ")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 2px;")
        root.addWidget(title)
        root.addSpacing(20)

        def make_input(placeholder, echo=False):
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            inp.setFixedWidth(380)
            inp.setFixedHeight(48)
            if echo:
                inp.setEchoMode(QLineEdit.EchoMode.Password)
            return inp

        self.last_name = make_input("Введите фамилию")
        self.first_name = make_input("Введите имя")
        self.middle_name = make_input("Введите отчество")
        self.email = make_input("Введите email")
        self.password = make_input("Введите пароль", echo=True)
        self.confirm_password = make_input("Подтвердите пароль", echo=True)

        self.role_combo = QComboBox()
        self.role_combo.setFixedHeight(48)
        self.role_combo.setFixedWidth(380)
        self.role_combo.addItem("Выберите вашу роль")
        for r in ROLES:
            self.role_combo.addItem(r)

        self.specialization = make_input("Введите ваше направление")

        fields = [
            self.last_name, self.first_name, self.middle_name,
            self.email, self.password, self.confirm_password,
            self.role_combo, self.specialization
        ]
        for f in fields:
            root.addWidget(f)
            root.addSpacing(10)

        root.addSpacing(6)

        reg_btn = QPushButton("Зарегистрироваться")
        reg_btn.setFixedWidth(380)
        reg_btn.setFixedHeight(48)
        reg_btn.clicked.connect(self._on_register)
        root.addWidget(reg_btn)
        root.addSpacing(14)

        login_row = QHBoxLayout()
        login_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        lbl = QLabel("Уже есть аккаунт?")
        lbl.setStyleSheet("font-size: 20px; color: #555;")
        lnk = QLabel("Войти")
        lnk.setStyleSheet("font-size: 20px; color: #1a1a1a; text-decoration: underline;")
        lnk.setCursor(Qt.CursorShape.PointingHandCursor)
        lnk.mousePressEvent = lambda e: self._go_login()
        login_row.addWidget(lbl)
        login_row.addSpacing(4)
        login_row.addWidget(lnk)
        root.addLayout(login_row)

    def _on_register(self):
        from core.operations import register
        role = self.role_combo.currentText()
        if role == "Выберите вашу роль":
            role = ""
        ok, msg, _ = register(
            self.last_name.text().strip(),
            self.first_name.text().strip(),
            self.middle_name.text().strip() or None,
            self.email.text().strip(),
            self.password.text(),
            self.confirm_password.text(),
            role,
            self.specialization.text().strip()
        )
        if ok:
            QMessageBox.information(self, "Успех", msg)
            self._go_login()
        else:
            QMessageBox.warning(self, "Ошибка", msg)

    def _go_login(self):
        from ui.login_window import LoginWindow
        self.login_win = LoginWindow()
        self.login_win.show()
        self.close()
