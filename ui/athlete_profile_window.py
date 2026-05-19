from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox, QSizePolicy,
    QDialog, QComboBox
)
from PyQt6.QtGui import QPixmap, QFont, QPainter, QPainterPath
from PyQt6.QtCore import Qt


class AthleteNavBar(QWidget):
    def __init__(self, active_tab, on_tab, viewer_role):
        super().__init__()
        self.active_tab = active_tab
        self.on_tab = on_tab
        self.viewer_role = viewer_role
        self._build()

    def _build(self):
        self.setFixedHeight(80)
        # ✅ Убрана линия под навбаром (border-bottom удалён)
        self.setStyleSheet("QWidget { background: #ffffff; }")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)
        layout.setSpacing(0)

        # 🔹 1. Логотип СЛЕВА
        logo_label = QLabel()
        pix = QPixmap("img/logo-profile.png")
        if not pix.isNull():
            logo_label.setPixmap(pix.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("APEX")
            logo_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        logo_label.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(logo_label)

        # 🔹 2. Растяжка слева от вкладок (центрирует навигацию)
        layout.addStretch(1)

        # 🔹 3. Контейнер для вкладок (будет по центру экрана)
        tabs_widget = QWidget()
        tabs_layout = QHBoxLayout(tabs_widget)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(0)

        tabs = [
            ("Профиль", "profile"),
            ("Тренировочный план", "training"),
            ("Дневник нагрузок", "diary"),
            ("Медицинские показатели", "medical"),
        ]

        for label, key in tabs:
            is_active = (key == self.active_tab)
            btn = QPushButton(label)
            btn.setFlat(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {'#1a1a1a' if is_active else '#888888'};
                    font-size: 20px;
                    font-weight: {'bold' if is_active else 'normal'};
                    border: none;
                    padding: 4px 20px;
                }}
                QPushButton:hover {{ color: #1a1a1a; }}
            """)
            btn.clicked.connect(lambda checked, k=key: self.on_tab(k))
            tabs_layout.addWidget(btn)

        layout.addWidget(tabs_widget)

        # 🔹 4. Растяжка справа от вкладок (центрирует навигацию)
        layout.addStretch(1)

        # 🔹 5. Пустой виджет справа, чтобы сбалансировать ширину лого слева
        # (иначе навигация уедет чуть правее центра из-за ширины логотипа)
        spacer = QWidget()
        spacer.setFixedWidth(60)  # Примерная ширина логотипа
        layout.addWidget(spacer)


class AthleteProfileWindow(QMainWindow):
    def __init__(self, viewer_data, athlete_data, on_unbound=None):
        super().__init__()
        self.viewer_data = viewer_data
        self.athlete_data = athlete_data
        self.on_unbound = on_unbound  # ✅ Сохраняем callback
        self.current_tab = "profile"
        self.setMinimumSize(1200, 750)
        self.setWindowTitle("Профиль спортсмена")
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        self._main_layout = QVBoxLayout(central)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self.navbar = AthleteNavBar(
            active_tab=self.current_tab,
            on_tab=self._switch_tab,
            viewer_role=self.viewer_data.get('role', '')
        )
        self._main_layout.addWidget(self.navbar)

        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(40, 32, 40, 32)
        self._main_layout.addWidget(self.content_area)

        self._show_profile()

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _switch_tab(self, tab):
        if tab == self.current_tab:
            return
        self.current_tab = tab
        self._main_layout.removeWidget(self.navbar)
        self.navbar.deleteLater()
        self.navbar = AthleteNavBar(
            active_tab=tab,
            on_tab=self._switch_tab,
            viewer_role=self.viewer_data.get('role', '')
        )
        self._main_layout.insertWidget(0, self.navbar)
        self._clear_content()

        if tab == "profile":
            self._show_profile()

    def _show_popup(self, title, text, icon, ok_text="ОК"):
        """Вспомогательный метод для единых попапов: Alegreya 20px + русские кнопки"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        msg.setFont(QFont("Alegreya", 20))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.button(QMessageBox.StandardButton.Ok).setText(ok_text)
        msg.exec()

    def _create_rounded_pixmap(self, pixmap, radius):
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

    def _load_athlete_photo(self):
        path = self.athlete_data.get('photo_path')
        if path:
            pix = QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaled(
                    2000, 400,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                rounded = self._create_rounded_pixmap(scaled, 20)
                self.photo_label.setPixmap(rounded)
                return
        self.photo_label.clear()
        self.photo_label.setText("Нет фото")
        self.photo_label.setStyleSheet("""
            QLabel { border: 1.5px dashed #cccccc; border-radius: 20px;
                background: #eeeeee; color: #aaa; font-size: 20px; }
        """)

    def _show_profile(self):
        layout = self.content_layout

        # ✅ РОЛЬ БЕРЁТСЯ НАПРЯМУЮ ИЗ БД ПРИ КАЖДОМ ОТКРЫТИИ ВКЛАДКИ
        from core.operations import get_profile
        ok, _, db_data = get_profile(self.athlete_data['id'])
        if ok:
            self.athlete_data.update(db_data)

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

        photo_col = QVBoxLayout()
        photo_col.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        self.photo_label = QLabel()
        self.photo_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.photo_label.setContentsMargins(0, 0, 0, 0)
        self.photo_label.setStyleSheet("""
            QLabel { border: 1.5px solid #cccccc; border-radius: 20px; background: #eeeeee; }
        """)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_athlete_photo()
        photo_col.addWidget(self.photo_label)
        card_layout.addLayout(photo_col)

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
            lbl.setStyleSheet("font-weight: bold; font-size: 20px; border: none; background: transparent;")
            val = QLabel(str(value) if value else "—")
            val.setStyleSheet("font-size: 20px; color: #888; border: none; background: transparent;")
            fl.addWidget(lbl)
            fl.addSpacing(6)
            fl.addWidget(val)
            fl.addStretch()
            return frame

        a = self.athlete_data
        fields_col.addWidget(field_row("Фамилия", a.get('last_name', '')))
        fields_col.addWidget(field_row("Имя", a.get('first_name', '')))
        fields_col.addWidget(field_row("Отчество", a.get('middle_name', '')))
        fields_col.addWidget(field_row("Роль", a.get('role', 'Не указана')))
        fields_col.addWidget(field_row("Направление", a.get('specialization', '')))
        fields_col.addWidget(field_row("Статус", a.get('current_status', '—')))
        fields_col.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        unbind_btn = QPushButton("Отвязать спортсмена")
        unbind_btn.setFixedWidth(314)
        unbind_btn.setStyleSheet("""
            QPushButton { 
                background: #1a1a1a; color: white; 
                border-radius: 20px; font-size: 20px; font-weight: bold; 
            }
            QPushButton:hover { background: #333; }
        """)
        unbind_btn.clicked.connect(self._unbind_athlete)
        
        change_btn = QPushButton("Изменить статус спортсмена")
        change_btn.setFixedWidth(412)
        change_btn.setStyleSheet("""
            QPushButton { 
                background: #1a1a1a; color: white; 
                border-radius: 20px; font-size: 20px; font-weight: bold; 
            }
            QPushButton:hover { background: #333; }
        """)
        change_btn.clicked.connect(self._change_athlete_status)
        
        btn_row.addWidget(unbind_btn)
        btn_row.addSpacing(10)
        btn_row.addWidget(change_btn)
        fields_col.addLayout(btn_row)

        card_layout.addLayout(fields_col)
        layout.addWidget(card)
        layout.addStretch()

    def _unbind_athlete(self):
        full_name = f"{self.athlete_data.get('last_name', '')} {self.athlete_data.get('first_name', '')}".strip()
        msg = QMessageBox(self)
        msg.setWindowTitle("Отвязать спортсмена")
        msg.setText(f"Вы уверены, что хотите отвязать спортсмена «{full_name or 'выбранного атлета'}»?")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setFont(QFont("Alegreya", 20))
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.button(QMessageBox.StandardButton.Yes).setText("Отвязать")
        msg.button(QMessageBox.StandardButton.No).setText("Отмена")

        if msg.exec() == QMessageBox.StandardButton.Yes:
            from core.operations import remove_athlete_from_list
            ok, msg_text, _ = remove_athlete_from_list(
                specialist_id=self.viewer_data['id'],
                athlete_id=self.athlete_data['id']
            )
            if ok:
                self._show_popup("Успех", "Спортсмен исключён из списка.", QMessageBox.Icon.Information)
                
                # ✅ Вызываем обновление списка в родительском окне
                if self.on_unbound:
                    self.on_unbound()
                    
                self.close()  # Закрываем профиль → видим обновлённый список
            else:
                self._show_popup("Ошибка", msg_text, QMessageBox.Icon.Warning)

    def _change_athlete_status(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Изменить статус")
        dlg.setFixedSize(380, 200)
        dlg.setFont(QFont("Alegreya", 20))
        
        v = QVBoxLayout(dlg)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(12)

        title_lbl = QLabel("Новый статус:")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
        v.addWidget(title_lbl)

        combo = QComboBox()
        combo.setFixedHeight(52)
        combo.addItems(["здоров", "устал", "болен"])
        current = self.athlete_data.get('current_status', '')
        idx = combo.findText(current)
        if idx >= 0:
            combo.setCurrentIndex(idx)
        combo.setFont(QFont("Alegreya", 20))
        combo.setStyleSheet("""
            QComboBox { 
                border: 1.5px solid #cccccc; 
                border-radius: 20px; 
                padding: 0 16px; 
                font-size: 20px; 
                background: #ffffff; 
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; border: none; }
        """)
        v.addWidget(combo)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedWidth(120)
        cancel_btn.setFixedHeight(52)
        cancel_btn.setFont(QFont("Alegreya", 20))
        cancel_btn.setStyleSheet("""
            QPushButton { 
                background: #1a1a1a; 
                color: white; 
                border-radius: 20px; 
                font-size: 20px; 
                font-weight: bold; 
            }
            QPushButton:hover { background: #333; }
        """)
        
        save_btn = QPushButton("Сохранить")
        save_btn.setFixedWidth(150)
        save_btn.setFixedHeight(52)
        save_btn.setFont(QFont("Alegreya", 20))
        save_btn.setStyleSheet("""
            QPushButton { 
                background: #1a1a1a; 
                color: white; 
                border-radius: 20px; 
                font-size: 20px; 
                font-weight: bold; 
            }
            QPushButton:hover { background: #333; }
        """)

        cancel_btn.clicked.connect(dlg.reject)
        save_btn.clicked.connect(dlg.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        v.addLayout(btn_row)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            from core.operations import update_athlete_status
            
            selected_status = combo.currentText().strip().lower()
            
            ok, msg_text, _ = update_athlete_status(
                self.viewer_data['id'],
                self.athlete_data['id'],
                selected_status
            )
            
            if ok:
                # ✅ Всплывающее сообщение об успехе (Alegreya 20px + русская кнопка)
                self._show_popup("Успех", "Статус спортсмена успешно обновлён.", QMessageBox.Icon.Information, "Хорошо")
                
                self.athlete_data['current_status'] = selected_status
                self._clear_content()
                self._show_profile()
            else:
                self._show_popup("Ошибка", msg_text, QMessageBox.Icon.Warning, "Понятно")