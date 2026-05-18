from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QComboBox, QFrame,
    QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt
from ui.base_window import SpecialistBaseWindow

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
        def col(text, width=None):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 20px;")
            if width:
                lbl.setFixedWidth(width)
            return lbl

        info_row.addWidget(col(self.athlete.get('last_name', ''), 200))
        info_row.addWidget(col(self.athlete.get('first_name', ''), 180))
        info_row.addWidget(col(self.athlete.get('middle_name', '') or '', 200))
        info_row.addWidget(col(self.athlete.get('specialization', ''), 220))
        status = self.athlete.get('current_status', '—')
        status_lbl = QLabel(status)
        status_lbl.setStyleSheet("font-size: 20px; color: #555;")
        info_row.addWidget(status_lbl)
        info_row.addStretch()
        layout.addLayout(info_row)

        btn_row = QHBoxLayout()
        detail_btn = QPushButton("Подробнее")
        detail_btn.setStyleSheet("""
            QPushButton { background: #1a1a1a; color: white; border-radius: 20px;
                padding: 10px; font-size: 20px; font-weight: bold; }
            QPushButton:hover { background: #333; }
        """)
        detail_btn.clicked.connect(lambda: on_detail(self.athlete))
        btn_row.addWidget(detail_btn)
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
        self.search_input.setPlaceholderText("🔍  Поиск")
        self.search_input.setFixedHeight(52)
        self.search_input.setStyleSheet("""
            QLineEdit { border: 1.5px solid #cccccc; border-radius: 18px;
                padding: 10px 18px; font-size: 20px; background: #ffffff; }
        """)
        filter_row.addWidget(self.search_input, 3)

        self.direction_combo = QComboBox()
        self.direction_combo.setFixedHeight(52)
        self.direction_combo.addItems(["Направление", "бег", "плавание", "велосипед", "борьба", "гимнастика"])
        filter_row.addWidget(self.direction_combo, 1)

        self.status_combo = QComboBox()
        self.status_combo.setFixedHeight(52)
        self.status_combo.addItems(["Статус", "готов", "не готов", "под наблюдением"])
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

        # Header row labels
        header = QHBoxLayout()
        for text, width in [("Фамилия", 200), ("Имя", 180), ("Отчество", 200), ("Направление", 220), ("Статус", 0)]:
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 20px; color: #888; font-weight: bold;")
            if width:
                lbl.setFixedWidth(width)
            header.addWidget(lbl)
        header.addStretch()
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

        # Pagination
        page_row = QHBoxLayout()
        page_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.prev_btn = QPushButton("←")
        self.prev_btn.setStyleSheet("QPushButton { background: transparent; color: #1a1a1a; border: none; font-size: 24px; }")
        self.prev_btn.setFixedWidth(40)
        self.prev_btn.clicked.connect(self._prev_page)
        self.page_label = QLabel("1 страница из 1")
        self.page_label.setStyleSheet("font-size: 20px;")
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

    def _apply_filter(self):
        self.page = 1
        self.search_text = self.search_input.text().strip()
        d = self.direction_combo.currentText()
        self.direction_filter = d if d != "Направление" else None
        s = self.status_combo.currentText()
        self.status_filter = s if s != "Статус" else None
        self._refresh()

    def _refresh(self):
        from core.operations import get_my_athletes
        
        # Получаем текущие значения фильтров
        search_val = self.search_input.text().strip() or None
        direction_val = self.direction_combo.currentText()
        status_val = self.status_combo.currentText()
        
        # ✅ ИСПРАВЛЕНО: direction -> sport_type (как ожидает бэкенд)
        ok, msg, data = get_my_athletes(
            self.user_data['id'],
            page=self.page,
            per_page=PER_PAGE,
            search=search_val,
            sport_type=direction_val if direction_val != "Все направления" else None,
            status=status_val if status_val != "Все статусы" else None
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
            empty.setStyleSheet("color: #888; font-size: 20px; margin: 20px;")
            self.scroll_layout.addWidget(empty)
        else:
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
        self.athlete_win = AthleteProfileWindow(self.user_data, athlete)
        self.athlete_win.show()

    def _add_athlete(self):
        from PyQt6.QtWidgets import QInputDialog
        email, ok = QInputDialog.getText(self, "Добавить спортсмена", "Email спортсмена:")
        if not ok or not email.strip():
            return
        from core.operations import bind_athlete
        success, msg, _ = bind_athlete(self.user_data['id'], email.strip())
        if success:
            self._refresh()
        else:
            QMessageBox.warning(self, "Ошибка", msg)
