from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt


class EditProfileWindow(QWidget):
    def __init__(self, user_data, profile_data, on_saved=None):
        super().__init__()
        self.user_data = user_data
        self.profile_data = profile_data
        self.on_saved = on_saved
        self.setWindowTitle("Редактировать профиль")
        self.setMinimumSize(480, 540)
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

        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(12)

        title = QLabel("Редактировать профиль")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(8)

        def field(label, value=""):
            layout.addWidget(QLabel(label))
            inp = QLineEdit()
            inp.setFixedHeight(44)
            inp.setText(value or "")
            layout.addWidget(inp)
            return inp

        d = self.profile_data
        self.last_name = field("Фамилия:", d.get('last_name', ''))
        self.first_name = field("Имя:", d.get('first_name', ''))
        self.middle_name = field("Отчество:", d.get('middle_name', ''))
        self.email = field("Email:", self.user_data.get('email', ''))
        self.specialization = field("Направление:", d.get('specialization', ''))

        layout.addSpacing(8)

        # Change password section
        pw_lbl = QLabel("Изменить пароль")
        pw_lbl.setStyleSheet("font-size: 15px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(pw_lbl)
        self.current_password = field("Текущий пароль:")
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password = field("Новый пароль:")
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = field("Подтвердите новый пароль:")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addSpacing(10)

        save_btn = QPushButton("Сохранить изменения")
        save_btn.setFixedHeight(48)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
        layout.addStretch()

    def _save(self):
        from core.operations import edit_profile, change_password

        ok, msg, _ = edit_profile(
            self.user_data['id'],
            self.last_name.text().strip(),
            self.first_name.text().strip(),
            self.middle_name.text().strip() or None,
            self.email.text().strip(),
            self.specialization.text().strip()
        )
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return

        # Password change if filled
        cur = self.current_password.text()
        new = self.new_password.text()
        conf = self.confirm_password.text()
        if cur or new or conf:
            pw_ok, pw_msg, _ = change_password(self.user_data['id'], cur, new, conf)
            if not pw_ok:
                QMessageBox.warning(self, "Ошибка пароля", pw_msg)
                return

        QMessageBox.information(self, "Успех", "Профиль обновлён.")
        if self.on_saved:
            self.on_saved()
        self.close()
