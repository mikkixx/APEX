from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QComboBox, QFrame,
    QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from ui.base_window import SpecialistBaseWindow


class ReportsWindow(SpecialistBaseWindow):
    active_tab = "reports"

    def __init__(self, user_data):
        super().__init__(user_data)
        self._athlete_id = None
        self._report_type = None
        self._start_date = None
        self._end_date = None
        self._load()

    def _load(self):
        layout = self._content_layout

        title = QLabel("ОТЧЕТЫ")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(16)

        outer = QFrame()
        outer.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 20px; background: #fafafa; }")
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(28, 22, 28, 22)
        outer_layout.setSpacing(16)

        # Filter section
        filter_title = QLabel("Параметры отчета")
        filter_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        outer_layout.addWidget(filter_title)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Спортсмен:"))
        self.athlete_combo = QComboBox()
        self.athlete_combo.setFixedHeight(52)
        self.athlete_combo.addItem("Все спортсмены")
        self._load_athletes()
        row1.addWidget(self.athlete_combo)
        row1.addStretch()
        outer_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Тип отчета:"))
        self.report_combo = QComboBox()
        self.report_combo.setFixedHeight(52)
        role = self.user_data.get('role', '')
        if role == 'тренер':
            self.report_combo.addItems([
                "Сводка тренировок",
                "Динамика нагрузок",
                "Выполнение плана",
                "Дневник нагрузок сводный",
            ])
        else:  # врач
            self.report_combo.addItems([
                "Медицинская сводка",
                "Динамика показателей",
                "Критичные показатели",
                "Общий отчет здоровья",
            ])
        row2.addWidget(self.report_combo)
        row2.addStretch()
        outer_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Период:"))
        row3.addWidget(QLabel("С:"))
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setFixedHeight(52)
        row3.addWidget(self.start_date)
        row3.addWidget(QLabel("По:"))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setFixedHeight(52)
        row3.addWidget(self.end_date)
        row3.addStretch()
        outer_layout.addLayout(row3)

        gen_btn = QPushButton("Сформировать отчет")
        gen_btn.setFixedHeight(56)
        gen_btn.clicked.connect(self._generate)
        outer_layout.addWidget(gen_btn)

        # Report display area
        self.report_scroll = QScrollArea()
        self.report_scroll.setWidgetResizable(True)
        self.report_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.report_widget = QWidget()
        self.report_layout = QVBoxLayout(self.report_widget)
        self.report_layout.setSpacing(12)
        self.report_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.report_scroll.setWidget(self.report_widget)
        outer_layout.addWidget(self.report_scroll)

        layout.addWidget(outer)

    def _load_athletes(self):
        from core.operations import get_my_athletes
        ok, msg, data = get_my_athletes(self.user_data['id'], page=1, per_page=100)
        if ok:
            for a in data.get('athletes', []):
                name = f"{a.get('last_name','')} {a.get('first_name','')}"
                self.athlete_combo.addItem(name, userData=a['id'])

    def _generate(self):
        while self.report_layout.count():
            item = self.report_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        athlete_idx = self.athlete_combo.currentIndex()
        athlete_id = None
        if athlete_idx > 0:
            athlete_id = self.athlete_combo.itemData(athlete_idx)

        report_type = self.report_combo.currentText()
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()

        from core.operations import generate_report
        ok, msg, report_data = generate_report(
            self.user_data['id'], athlete_id, report_type, start, end
        )

        if not ok:
            QMessageBox.warning(self, "Ошибка", msg)
            return

        if not report_data:
            empty = QLabel("Данных для отчета не найдено.")
            empty.setStyleSheet("color: #888; font-size: 20px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.report_layout.addWidget(empty)
            return

        # Render report sections
        for section in report_data:
            section_frame = QFrame()
            section_frame.setStyleSheet("""
                QFrame { background: white; border: 1px solid #e0e0e0;
                    border-radius: 16px; }
            """)
            sl = QVBoxLayout(section_frame)
            sl.setContentsMargins(20, 16, 20, 16)
            sl.setSpacing(8)

            sec_title = QLabel(section.get('title', ''))
            sec_title.setStyleSheet("font-size: 22px; font-weight: bold;")
            sl.addWidget(sec_title)

            for item in section.get('items', []):
                row = QHBoxLayout()
                lbl = QLabel(item.get('label', ''))
                lbl.setStyleSheet("font-size: 20px; font-weight: bold;")
                val = QLabel(str(item.get('value', '')))
                val.setStyleSheet("font-size: 20px; color: #555;")
                row.addWidget(lbl)
                row.addSpacing(8)
                row.addWidget(val)
                row.addStretch()
                sl.addLayout(row)

            self.report_layout.addWidget(section_frame)
        self.report_layout.addStretch()
