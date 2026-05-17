from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QMessageBox, QLineEdit, QScrollArea, QWidget
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from ui.base_window import BaseWindow


class ProfileWindow(BaseWindow):
    active_tab = "profile"

    def __init__(self, user_data):
        super().__init__(user_data)
        self._load_profile()

    def _load_profile(self):
        from core.operations import get_profile
        ok, msg, data = get_profile(self.user_data['id'])
        if ok:
            self.profile_data = data
        else:
            self.profile_data = self.user_data
        self._build()

    def _build(self):
        layout = self._content_layout

        title = QLabel("ПРОФИЛЬ")
        title.setStyleSheet("font-size: 26px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(16)

        card = QFrame()
        card.setStyleSheet("""
            QFrame { border: 1px solid #e0e0e0; border-radius: 20px; background: #fafafa; }
        """)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(32)

        # Photo
        photo_col = QVBoxLayout()
        photo_col.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(180, 180)
        self.photo_label.setStyleSheet("""
            QLabel { border: 1.5px solid #cccccc; border-radius: 12px;
                background: #eeeeee; }
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_photo()
        photo_col.addWidget(self.photo_label)

        change_photo_btn = QPushButton("Изменить фото")
        change_photo_btn.setFixedWidth(160)
        change_photo_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #1a1a1a;
                border: 1.5px solid #1a1a1a; border-radius: 14px;
                padding: 6px 14px; font-size: 12px; margin-top: 8px; }
        """)
        change_photo_btn.clicked.connect(self._change_photo)
        photo_col.addWidget(change_photo_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        card_layout.addLayout(photo_col)

        # Fields
        fields_col = QVBoxLayout()
        fields_col.setSpacing(10)

        def field_row(label, value):
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame { border: 1.5px solid #e0e0e0; border-radius: 16px;
                    background: #f5f5f5; }
            """)
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(16, 10, 16, 10)
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
            val = QLabel(str(value) if value else "—")
            val.setStyleSheet("font-size: 14px; color: #888; border: none;")
            fl.addWidget(lbl)
            fl.addSpacing(6)
            fl.addWidget(val)
            fl.addStretch()
            return frame

        d = self.profile_data
        fields_col.addWidget(field_row("Фамилия", d.get('last_name', '')))
        fields_col.addWidget(field_row("Имя", d.get('first_name', '')))
        fields_col.addWidget(field_row("Отчество", d.get('middle_name', '')))
        fields_col.addWidget(field_row("Роль", d.get('role', '')))
        fields_col.addWidget(field_row("Направление", d.get('specialization', '')))

        if d.get('role') == 'спортсмен':
            fields_col.addWidget(field_row("Статус", d.get('current_status', 'Не установлен')))

        fields_col.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignRight)
        edit_btn = QPushButton("Редактировать")
        edit_btn.setFixedWidth(160)
        edit_btn.clicked.connect(self._edit_profile)

        del_btn = QPushButton("Удалить аккаунт")
        del_btn.setFixedWidth(160)
        del_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 18px;
                padding: 10px 24px; font-size: 13px; }
            QPushButton:hover { background: #333; }
        """)
        del_btn.clicked.connect(self._delete_account)

        btn_row.addWidget(edit_btn)
        btn_row.addSpacing(10)
        btn_row.addWidget(del_btn)
        fields_col.addLayout(btn_row)

        card_layout.addLayout(fields_col)
        layout.addWidget(card)
        layout.addStretch()

    def _load_photo(self):
        path = self.profile_data.get('photo_path')
        if path:
            pix = QPixmap(path)
            if not pix.isNull():
                self.photo_label.setPixmap(
                    pix.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)
                )
                return
        self.photo_label.setText("Нет фото")
        self.photo_label.setStyleSheet("""
            QLabel { border: 1.5px dashed #cccccc; border-radius: 12px;
                background: #eeeeee; color: #aaa; font-size: 13px; }
        """)

    def _change_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать фото", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            from core.operations import edit_profile
            d = self.profile_data
            ok, msg, _ = edit_profile(
                self.user_data['id'],
                d['last_name'], d['first_name'], d.get('middle_name'),
                self.user_data.get('email', ''), d['specialization'],
                photo_path=path
            )
            if ok:
                self.profile_data['photo_path'] = path
                self._load_photo()
            else:
                QMessageBox.warning(self, "Ошибка", msg)

    def _edit_profile(self):
        from ui.edit_profile_window import EditProfileWindow
        self.edit_win = EditProfileWindow(self.user_data, self.profile_data, on_saved=self._reload)
        self.edit_win.show()

    def _reload(self):
        # Clear content and reload
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._load_profile()

    def _delete_account(self):
        reply = QMessageBox.warning(
            self, "Удалить аккаунт",
            "Вы уверены, что хотите удалить аккаунт? Это действие необратимо.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Yes:
            from core.operations import delete_account
            ok, msg, _ = delete_account(self.user_data['id'])
            if ok:
                from ui.login_window import LoginWindow
                self._login = LoginWindow()
                self._login.show()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", msg)
