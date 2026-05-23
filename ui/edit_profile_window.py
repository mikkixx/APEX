from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from db.models import User  

class EditProfileWindow(QWidget):
    def __init__(self, user_data, profile_data, on_saved=None):
        super().__init__()
        self.user_data = user_data
        self.profile_data = profile_data
        self.on_saved = on_saved
        self.setWindowTitle("Редактировать профиль")
        self.setMinimumSize(480, 640)
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
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        layout.addSpacing(8)

        def field(label, value=""):
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
            layout.addWidget(lbl)
            inp = QLineEdit()
            inp.setFixedHeight(48)
            inp.setText(str(value) if value is not None else "")
            inp.setStyleSheet("font-size: 20px; padding: 0 10px; color: #1a1a1a;")
            layout.addWidget(inp)
            return inp

        d = self.profile_data
        self.last_name = field("Фамилия:", d.get('last_name', ''))
        self.first_name = field("Имя:", d.get('first_name', ''))
        self.middle_name = field("Отчество:", d.get('middle_name', ''))
        
        try:
            email_db = User.get_by_id(self.user_data['id']).email
        except Exception:
            email_db = self.user_data.get('email', '')  
            
        self.email = field("Email:", email_db)
        self.specialization = field("Направление:", d.get('specialization', ''))

        photo_lbl_title = QLabel("Путь к фото:")
        photo_lbl_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(photo_lbl_title)

        self.photo_path = d.get('photo_path')
        self.photo_display = QLabel()
        self.photo_display.setFixedHeight(48)
        self.photo_display.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.photo_display.setStyleSheet("""
            QLabel { font-size: 20px; padding: 0 10px;
                     border: 2px solid #CFCFCF; border-radius: 20px; background: #f9f9f9; }
        """)
        
        self.photo_display.setText(self.photo_path if self.photo_path else "отсутствует")
        self.photo_display.setCursor(Qt.CursorShape.PointingHandCursor)
        self.photo_display.mousePressEvent = lambda e: self._browse_photo()
        layout.addWidget(self.photo_display)

        self.delete_photo_btn = QPushButton("Удалить фото")
        self.delete_photo_btn.setFixedHeight(52)
        self.delete_photo_btn.setStyleSheet("""
            QPushButton {
                background: #1a1a1a;
                color: #ffffff;
                border: 1.5px solid #1a1a1a;
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover { background: transparent; color: #1a1a1a; }
        """)
        self.delete_photo_btn.clicked.connect(self._delete_photo)
        layout.addWidget(self.delete_photo_btn)

        self._update_delete_btn_visibility()

        pw_header = QLabel("Изменить пароль")
        pw_header.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 0px; margin-left: 0px;")
        layout.addWidget(pw_header)

        self.current_password = field("Текущий пароль:")
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password = field("Новый пароль:")
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = field("Подтвердите новый пароль:")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addSpacing(10)

        save_btn = QPushButton("Сохранить изменения")
        save_btn.setFixedHeight(52)
        save_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                font-size: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)
        layout.addStretch()

    def _update_delete_btn_visibility(self):
        if self.photo_path:
            self.delete_photo_btn.show()
        else:
            self.delete_photo_btn.hide()

    def _browse_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать фото", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.photo_path = path
            self.photo_display.setText(path)
            self.photo_display.setStyleSheet("""
                QLabel { font-size: 20px; padding: 0 10px; color: #1a1a1a;
                         border: 2px solid black; border-radius: 20px; background: #f9f9f9; }
            """)
            self._update_delete_btn_visibility()

    def _delete_photo(self):
        self.photo_path = None
        self.photo_display.setText("отсутствует")
        self.photo_display.setStyleSheet("""
            QLabel { font-size: 20px; padding: 0 10px;
                     border: 2px solid #CFCFCF; border-radius: 20px; background: #f9f9f9; }
        """)
        self._update_delete_btn_visibility()

    def _save(self):
        from core.operations import edit_profile, change_password

        current_text = self.photo_display.text()
        photo_path = self.photo_path if current_text not in ("отсутствует", "") else None

        ok, msg, _ = edit_profile(
            self.user_data['id'],
            self.last_name.text().strip(),
            self.first_name.text().strip(),
            self.middle_name.text().strip() or None,
            self.email.text().strip(),
            self.specialization.text().strip(),
            photo_path=photo_path
        )
        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return

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