from utils import resource_path, reports_dir
import os
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QComboBox, QFrame,
    QMessageBox, QDateEdit, QFileDialog, QLineEdit, QCheckBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from ui.base_window import SpecialistBaseWindow
from pathlib import Path

class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal()
    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

class ReportsWindow(SpecialistBaseWindow):
    active_tab = "reports"

    def __init__(self, user_data):
        super().__init__(user_data)
        self._load()

    def _load(self):
        layout = self._content_layout
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("ОТЧЕТЫ")
        title.setStyleSheet("font-size: 48px; font-weight: bold; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        layout.addSpacing(12)

        outer = QFrame()
        outer.setStyleSheet("""
            QFrame { border: none; border-radius: 18px; background: #fafafa; }
            QLabel, QDateEdit, QComboBox, QPushButton, QLineEdit, QCheckBox { font-size: 20px; }
        """)
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(36, 28, 36, 28)
        outer_layout.setSpacing(16)

        sec_title = QLabel("Параметры отчёта")
        sec_title.setStyleSheet("font-size: 28px; font-weight: bold; border: none; background: transparent;")
        sec_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        outer_layout.addWidget(sec_title)

        FIELD_H    = 52
        LBL_W      = 200   
        LBL_STYLE  = "font-size: 20px; border: none; background: transparent;"

        INPUT_STYLE = """
            QLineEdit {
                border: 1.5px solid #cccccc;
                border-radius: 20px;
                padding: 0 16px;
                font-size: 20px;
                background: #ffffff;
            }
        """
        COMBO_STYLE = """
            QComboBox {
                border: 1.5px solid #cccccc;
                border-radius: 20px;
                padding: 0 16px;
                font-size: 20px;
                background: #ffffff;
            }
            QComboBox::drop-down { border: none; padding-right: 12px; }
        """
        DATE_STYLE = """
            QDateEdit {
                background: #ffffff;
            }
        """

        IMG_PATH = (Path(__file__).parent.parent / "img" / "ok.png").resolve()

        CB_STYLE = f"""
            QCheckBox {{
                font-size: 20px;
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border: 1.5px solid #cccccc;
                border-radius: 6px;
                background: #ffffff;
            }}
            QCheckBox::indicator:checked {{
                background: #ffffff;
                border: 1.5px solid #1a1a1a;
                image: url({IMG_PATH.as_posix()});
            }}
        """

        def make_row(label_text, widget):
            """Строка: фиксированная подпись + растягиваемое поле."""
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet(LBL_STYLE)
            lbl.setFixedWidth(LBL_W)
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            row.addWidget(lbl)
            row.addWidget(widget)
            return row

        self.report_name = QLineEdit()
        self.report_name.setPlaceholderText("Например: Отчёт за июнь 2025")
        self.report_name.setFixedHeight(FIELD_H)
        self.report_name.setStyleSheet(INPUT_STYLE)
        outer_layout.addLayout(make_row("Название отчёта:", self.report_name))

        self.type_combo = QComboBox()
        self.type_combo.setFixedHeight(FIELD_H)
        self.type_combo.setStyleSheet(COMBO_STYLE)
        self.type_combo.addItem("Общий (все данные)", "general")
        self.type_combo.addItem("Медицинский", "medical")
        self.type_combo.addItem("Тренировочный", "training")
        self.type_combo.addItem("Дневник нагрузок", "diary")
        outer_layout.addLayout(make_row("Тип отчёта:", self.type_combo))

        self.athlete_combo = QComboBox()
        self.athlete_combo.setFixedHeight(FIELD_H)
        self.athlete_combo.setStyleSheet(COMBO_STYLE)
        self.athlete_combo.addItem("Все спортсмены", None)
        self._load_athletes()
        outer_layout.addLayout(make_row("Спортсмен:", self.athlete_combo))

        period_row = QHBoxLayout()
        period_lbl = QLabel("Период:")
        period_lbl.setStyleSheet(LBL_STYLE)
        period_lbl.setFixedWidth(LBL_W)
        period_row.addWidget(period_lbl)

        lbl_from = QLabel("С:")
        lbl_from.setStyleSheet(LBL_STYLE)
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setFixedHeight(FIELD_H)
        self.start_date.setStyleSheet(DATE_STYLE)

        lbl_to = QLabel("По:")
        lbl_to.setStyleSheet(LBL_STYLE)
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setFixedHeight(FIELD_H)
        self.end_date.setStyleSheet(DATE_STYLE)

        period_row.addWidget(lbl_from)
        period_row.addSpacing(6)
        period_row.addWidget(self.start_date)
        period_row.addSpacing(16)
        period_row.addWidget(lbl_to)
        period_row.addSpacing(6)
        period_row.addWidget(self.end_date)
        outer_layout.addLayout(period_row)

        fmt_row = QHBoxLayout()
        fmt_lbl = QLabel("Формат:")
        fmt_lbl.setStyleSheet(LBL_STYLE)
        fmt_lbl.setFixedWidth(LBL_W)
        fmt_row.addWidget(fmt_lbl)

        self.cb_pdf = QCheckBox("PDF")
        self.cb_pdf.setChecked(True)
        self.cb_pdf.setStyleSheet(CB_STYLE)
        
        self.cb_excel = QCheckBox("Excel (.xlsx)")
        self.cb_excel.setStyleSheet(CB_STYLE)

        self.cb_pdf.toggled.connect(lambda on: self.cb_excel.setChecked(not on) if on else None)
        self.cb_excel.toggled.connect(lambda on: self.cb_pdf.setChecked(not on) if on else None)

        fmt_row.addWidget(self.cb_pdf)
        fmt_row.addSpacing(32)
        fmt_row.addWidget(self.cb_excel)
        fmt_row.addStretch()
        outer_layout.addLayout(fmt_row)

        self.path_input = ClickableLineEdit(reports_dir())
        self.path_input.setReadOnly(True)
        self.path_input.setFixedHeight(FIELD_H)
        self.path_input.setStyleSheet(INPUT_STYLE)
        self.path_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.path_input.clicked.connect(self._browse_path)
        outer_layout.addLayout(make_row("Сохранить в:", self.path_input))

        outer_layout.addSpacing(8)
        gen_btn = QPushButton("Сформировать отчёт")
        gen_btn.setFixedHeight(54)
        gen_btn.setFixedWidth(320)
        gen_btn.setStyleSheet("""
            QPushButton {
                background: #1a1a1a; color: white; border-radius: 20px;
                font-size: 20px; font-weight: bold;
            }
            QPushButton:hover { background: #333; }
        """)
        gen_btn.clicked.connect(self._generate)

        btn_wrap = QHBoxLayout()
        btn_wrap.addStretch()
        btn_wrap.addWidget(gen_btn)
        btn_wrap.addStretch()
        outer_layout.addLayout(btn_wrap)

        layout.addWidget(outer)
        layout.addStretch()

    def _load_athletes(self):
        from core.operations import get_my_athletes
        ok, msg, data = get_my_athletes(self.user_data['id'], page=1, per_page=200)
        if ok:
            for a in data.get('athletes', []):
                name = f"{a.get('last_name','')} {a.get('first_name','')}".strip()
                self.athlete_combo.addItem(name, a['id'])

    def _browse_path(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку для сохранения",
            self.path_input.text() or reports_dir()
        )
        if folder:
            self.path_input.setText(folder)

    def _generate(self):
        report_name = self.report_name.text().strip() or "Отчёт"
        report_type = self.type_combo.currentData()
        athlete_id  = self.athlete_combo.itemData(self.athlete_combo.currentIndex())

        start = self.start_date.date().toPyDate()
        end   = self.end_date.date().toPyDate()

        if start > end:
            self._show_msg("Ошибка", "Дата начала не может быть позже даты окончания.", error=True)
            return

        fmt = "pdf" if self.cb_pdf.isChecked() else "excel"
        save_dir = self.path_input.text().strip() or "./reports"
        os.makedirs(save_dir, exist_ok=True)

        from core.operations import generate_report
        ok, msg, result = generate_report(
            specialist_id=self.user_data['id'],
            athlete_id=athlete_id,
            report_type=report_type,
            start_date=start,
            end_date=end,
            fmt=fmt,
            save_dir=save_dir,
            report_name=report_name,
        )

        if ok:
            path = result.get('path', '')
            self._show_msg("Готово", f"Отчёт успешно сохранён:\n{path}", error=False)
        else:
            self._show_msg("Ошибка", msg, error=True)

    def _show_msg(self, title, text, error=False):
        from PyQt6.QtGui import QFont
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Critical if error else QMessageBox.Icon.Information)
        msg.setFont(QFont("Alegreya", 20))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.button(QMessageBox.StandardButton.Ok).setText("Хорошо")
        msg.exec()
