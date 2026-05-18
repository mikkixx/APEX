from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QScrollArea, QWidget, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QFont, QPainter, QPainterPath
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
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px;")
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

        # Photo column
        photo_col = QVBoxLayout()
        photo_col.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        self.photo_label = QLabel()
        self.photo_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.photo_label.setContentsMargins(0, 0, 0, 0)
        # ✅ Серая граница + скругление 20px
        self.photo_label.setStyleSheet("""
            QLabel { border: 1.5px solid #cccccc; border-radius: 20px; background: #eeeeee; }
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_photo()
        photo_col.addWidget(self.photo_label)

        card_layout.addLayout(photo_col)

        # Fields
        fields_col = QVBoxLayout()
        fields_col.setSpacing(10)

        def field_row(label, value):
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame { border: 1.5px solid #e0e0e0; border-radius: 20px;
                    background: #f5f5f5; }
            """)
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(16, 10, 16, 10)
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("font-weight: bold; font-size: 20px; border: none;")
            val = QLabel(str(value) if value else "—")
            val.setStyleSheet("font-size: 20px; color: #888; border: none;")
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
        edit_btn.setFixedWidth(241)
        edit_btn.setStyleSheet("font-size: 20px;")
        edit_btn.clicked.connect(self._edit_profile)

        del_btn = QPushButton("Удалить аккаунт")
        del_btn.setFixedWidth(241)
        del_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                padding: 10px 24px; font-size: 20px; }
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

    def _create_rounded_pixmap(self, pixmap, radius):
        """Создает QPixmap с закругленными углами (QSS не обрезает картинки)"""
        if pixmap.isNull():
            return pixmap
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return rounded

    def _load_photo(self):
        path = self.profile_data.get('photo_path')
        if path:
            pix = QPixmap(path)
            if not pix.isNull():
                # ✅ Масштабируем: высота максимум 400px, ширина подстраивается
                scaled = pix.scaled(
                    2000, 400,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                # ✅ Обрезаем углы на 20px
                rounded = self._create_rounded_pixmap(scaled, 20)
                self.photo_label.setPixmap(rounded)
                # Лейбл автоматически сожмётся до размера картинки
                return
                
        # ✅ Заглушка если фото нет
        self.photo_label.clear()
        self.photo_label.setText("Нет фото")
        self.photo_label.setStyleSheet("""
            QLabel { border: 1.5px dashed #cccccc; border-radius: 20px;
                background: #eeeeee; color: #aaa; font-size: 20px; }
        """)

    def _edit_profile(self):
        from ui.edit_profile_window import EditProfileWindow
        self.edit_win = EditProfileWindow(self.user_data, self.profile_data, on_saved=self._reload)
        self.edit_win.show()

    def _reload(self):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._load_profile()

    def _delete_account(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Удалить аккаунт")
        msg.setText("Вы уверены, что хотите удалить аккаунт?\nЭто действие необратимо.")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        msg.setFont(QFont("Alegreya", 16))
        
        msg.button(QMessageBox.StandardButton.Yes).setText("Удалить")
        msg.button(QMessageBox.StandardButton.No).setText("Отмена")

        if msg.exec() == QMessageBox.StandardButton.Yes:
            from core.operations import delete_account
            ok, msg_text, _ = delete_account(self.user_data['id'])
            if ok:
                from ui.login_window import LoginWindow
                self._login = LoginWindow()
                self._login.show()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", msg_text)