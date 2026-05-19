from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QComboBox, QFrame,
    QMessageBox, QLineEdit, QSizePolicy, QDialog
)
from PyQt6.QtCore import Qt
from ui.base_window import SpecialistBaseWindow
from PyQt6.QtGui import QFont
from core.operations import add_athlete_by_email
from db.connection import db

PER_PAGE = 5

class AthleteRow(QFrame):
    def __init__(self, athlete, on_detail):
        super().__init__()
        self.athlete = athlete
        self._build(on_detail)

    def _build(self, on_detail):
        self.setStyleSheet("""
            QFrame { background: #fff; border: 1px solid #e0e0e0; border-radius: 20px; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(8)

        info_row = QHBoxLayout()
        
        def col(text, stretch=1):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 20px; background: transparent; border: none;")
            lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            lbl.setWordWrap(True)
            return lbl, stretch

        info_row.addWidget(*col(self.athlete.get('last_name', ''), 2))
        info_row.addWidget(*col(self.athlete.get('first_name', ''), 2))
        info_row.addWidget(*col(self.athlete.get('middle_name', '') or '', 2))
        info_row.addWidget(*col(self.athlete.get('specialization', ''), 2))
        info_row.addWidget(*col(self.athlete.get('current_status', '—'), 1))
        
        btn_row = QHBoxLayout()
        detail_btn = QPushButton("Подробнее")
        detail_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                padding: 10px; font-size: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        detail_btn.clicked.connect(lambda: on_detail(self.athlete))
        btn_row.addWidget(detail_btn)
        layout.addLayout(info_row)
        layout.addLayout(btn_row)


class MyAthletesWindow(SpecialistBaseWindow):
    active_tab = "athletes"

    def __init__(self, user_data):
        super().__init__(user_data)
        self.page = 1
        self.search_text = ""
        self.direction_filter = None
        self.status_filter = None
        self._load()

    def _load(self):
        layout = self._content_layout

        title = QLabel("МОИ СПОРТСМЕНЫ")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(16)

        outer = QFrame()
        outer.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 20px; background: #fafafa; }")
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(24, 20, 24, 20)
        outer_layout.setSpacing(12)

        # Filter row
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск")
        self.search_input.setFixedHeight(52)
        self.search_input.setStyleSheet("""
            QLineEdit { border: 1.5px solid #cccccc; border-radius: 20px;
                padding: 10px 18px; font-size: 20px; background: #ffffff; }
        """)
        filter_row.addWidget(self.search_input, 3)

        self.direction_combo = QComboBox()
        self.direction_combo.setFixedHeight(52)
        self.direction_combo.addItem("Все направления")  # ✅ Исправлено: совпадает с логикой фильтра
        filter_row.addWidget(self.direction_combo, 1)

        self.status_combo = QComboBox()
        self.status_combo.setFixedHeight(52)
        self.status_combo.addItem("Все статусы")  # ✅ Исправлено: совпадает с логикой фильтра
        filter_row.addWidget(self.status_combo, 1)

        apply_btn = QPushButton("Применить")
        apply_btn.setFixedHeight(52)
        apply_btn.clicked.connect(self._apply_filter)
        filter_row.addWidget(apply_btn)
        outer_layout.addLayout(filter_row)

        # Add athlete button
        add_btn = QPushButton("Добавить спортсмена")
        add_btn.setFixedWidth(280)
        add_btn.setFixedHeight(52)
        add_btn.clicked.connect(self._add_athlete)
        outer_layout.addWidget(add_btn)

        # Header — без обводки, колонки растягиваются
        header = QHBoxLayout()
        for text, stretch in [("Фамилия", 2), ("Имя", 2), ("Отчество", 2), ("Направление", 2), ("Статус", 1)]:
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 20px; color: #888; font-weight: bold; background: transparent; border: none;")
            lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            header.addWidget(lbl, stretch)
        outer_layout.addLayout(header)

        # Scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        outer_layout.addWidget(self.scroll_area)

        # Pagination — без обводки
        page_row = QHBoxLayout()
        page_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.prev_btn = QPushButton("←")
        self.prev_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 24px; }")
        self.prev_btn.setFixedWidth(40)
        self.prev_btn.clicked.connect(self._prev_page)
        self.page_label = QLabel("1 страница из 1")
        self.page_label.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        self.next_btn = QPushButton("→")
        self.next_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 24px; }")
        self.next_btn.setFixedWidth(40)
        self.next_btn.clicked.connect(self._next_page)
        page_row.addWidget(self.prev_btn)
        page_row.addWidget(self.page_label)
        page_row.addWidget(self.next_btn)
        outer_layout.addLayout(page_row)

        layout.addWidget(outer)
        self._refresh()

    def _load_filter_options(self, athletes):
        """Заполняет комбобоксы уникальными значениями из текущего списка спортсменов"""
        directions = sorted(set(
            a.get('specialization', '').strip() for a in athletes 
            if a.get('specialization') and a['specialization'].strip()
        ))
        self.direction_combo.clear()
        self.direction_combo.addItem("Все направления")
        for d in directions:
            self.direction_combo.addItem(d)

        statuses = sorted(set(
            a.get('current_status', '').strip() for a in athletes 
            if a.get('current_status') and a['current_status'].strip()
        ))
        self.status_combo.clear()
        self.status_combo.addItem("Все статусы")
        for s in statuses:
            self.status_combo.addItem(s)

    def _apply_filter(self):
        self.page = 1
        self.search_text = self.search_input.text().strip()
        d = self.direction_combo.currentText()
        # ✅ Проверяем все возможные "пустые" значения
        self.direction_filter = d if d not in ("Все направления", "Направление") else None
        s = self.status_combo.currentText()
        self.status_filter = s if s not in ("Все статусы", "Статус") else None
        self._refresh()

    def _refresh(self):
        from core.operations import get_my_athletes
        
        search_val = self.search_input.text().strip() or None
        direction_val = self.direction_combo.currentText()
        status_val = self.status_combo.currentText()
        
        ok, msg, data = get_my_athletes(
            self.user_data['id'],
            page=self.page,
            per_page=PER_PAGE,
            search=search_val,
            sport_type=direction_val if direction_val not in ("Все направления", "Направление") else None,
            status=status_val if status_val not in ("Все статусы", "Статус") else None
        )

        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return

        athletes = data.get('athletes', [])
        total = data.get('total', 0)
        total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

        if not athletes:
            empty = QLabel("Спортсменов не найдено.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #888; font-size: 20px; margin: 20px; background: transparent;")
            self.scroll_layout.addWidget(empty)
            self.direction_combo.clear()
            self.direction_combo.addItem("Все направления")
            self.status_combo.clear()
            self.status_combo.addItem("Все статусы")
        else:
            self._load_filter_options(athletes)
            for a in athletes:
                row = AthleteRow(a, self._open_athlete)
                self.scroll_layout.addWidget(row)

        self.page_label.setText(f"{self.page} страница из {total_pages}")
        self.prev_btn.setEnabled(self.page > 1)
        self.next_btn.setEnabled(self.page < total_pages)

    def _prev_page(self):
        if self.page > 1:
            self.page -= 1
            self._refresh()

    def _next_page(self):
        self.page += 1
        self._refresh()

    def _open_athlete(self, athlete):
        from ui.athlete_profile_window import AthleteProfileWindow
        # ✅ Передаём функцию обновления списка как callback
        self.athlete_win = AthleteProfileWindow(
            self.user_data, 
            athlete, 
            on_unbound=lambda: self._refresh()
        )
        self.athlete_win.show()

    def _add_athlete(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить спортсмена")
        dialog.setModal(True)
        dialog.setMinimumWidth(420)
        dialog.setFont(QFont("Alegreya", 20))
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(12)
        
        title = QLabel("Email спортсмена:")
        title.setStyleSheet("font-weight: bold; font-size: 20px;")
        layout.addWidget(title)
        
        email_input = QLineEdit()
        email_input.setPlaceholderText("Введите email")
        email_input.setFixedHeight(52)
        email_input.setStyleSheet("""
            QLineEdit { 
                border: 1.5px solid #cccccc; 
                border-radius: 20px; 
                padding: 0 16px; 
                font-size: 20px; 
                background: #ffffff; 
            }
        """)
        layout.addWidget(email_input)
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedWidth(140)
        cancel_btn.setFixedHeight(52)
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
        
        add_btn = QPushButton("Добавить")
        add_btn.setFixedWidth(140)
        add_btn.setFixedHeight(52)
        add_btn.setStyleSheet("""
            QPushButton { 
                background: #1a1a1a; 
                color: white; 
                border-radius: 20px; 
                font-size: 20px; 
                font-weight: bold; 
            }
            QPushButton:hover { background: #333; }
        """)
        
        btn_row.addWidget(cancel_btn)
        btn_row.addSpacing(10)
        btn_row.addWidget(add_btn)
        layout.addLayout(btn_row)
        
        result = {"email": None}
        
        def on_add():
            result["email"] = email_input.text().strip()
            dialog.accept()
        def on_cancel():
            dialog.reject()
            
        add_btn.clicked.connect(on_add)
        cancel_btn.clicked.connect(on_cancel)
        email_input.returnPressed.connect(on_add)
        
        if dialog.exec() == QDialog.DialogCode.Accepted and result["email"]:
            success, msg, _ = add_athlete_by_email(self.user_data['id'], result["email"])
            if success:
                # ✅ ПОКАЗЫВАЕМ СООБЩЕНИЕ ОБ УСПЕХЕ
                success_msg = QMessageBox(self)
                success_msg.setWindowTitle("Успех")
                success_msg.setText("Спортсмен успешно добавлен.")
                success_msg.setIcon(QMessageBox.Icon.Information)
                success_msg.setFont(QFont("Alegreya", 20))
                success_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                success_msg.button(QMessageBox.StandardButton.Ok).setText("Хорошо")
                success_msg.exec()
                
                # ✅ СБРОС ФИЛЬТРОВ + ПЕРЕЗАГРУЗКА
                self.search_input.clear()
                self.direction_combo.setCurrentIndex(0)  # "Все направления"
                self.status_combo.setCurrentIndex(0)      # "Все статусы"
                self.page = 1
                self._refresh()
            else:
                error_msg = QMessageBox(self)
                error_msg.setWindowTitle("Ошибка")
                error_msg.setText(msg)
                error_msg.setIcon(QMessageBox.Icon.Warning)
                error_msg.setFont(QFont("Alegreya", 20))
                error_msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_msg.button(QMessageBox.StandardButton.Ok).setText("Хорошо")
                error_msg.exec()