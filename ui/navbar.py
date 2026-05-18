from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class NavBar(QWidget):
    # ✅ Один универсальный сигнал: передает ключ вкладки (training, diary, athletes...)
    nav_requested = pyqtSignal(str)
    nav_logout = pyqtSignal()

    def __init__(self, tabs=None, active_tab=""):
        super().__init__()
        # Если список не передан, используем дефолтный (спортсмен)
        self.tabs = tabs or [
            ("Тренировочный план", "training"),
            ("Дневник нагрузок",   "diary"),
            ("Медкарта",           "medical"),
            ("Профиль",            "profile"),
            ("Чаты",               "chats"),
        ]
        self.active_tab = active_tab
        self._build()

    def _build(self):
        self.setFixedHeight(64)
        self.setStyleSheet("""
            NavBar { background: #ffffff; border-bottom: 1px solid #e0e0e0; }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(0)

        # Логотип
        logo_label = QLabel()
        logo_pix = QPixmap("img/logo.png")
        if not logo_pix.isNull():
            logo_label.setPixmap(logo_pix.scaledToHeight(44, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_label.setText("APEX")
            logo_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        logo_label.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(logo_label)

        layout.addStretch(1)

        # Контейнер для динамических вкладок
        tabs_widget = QWidget()
        tabs_layout = QHBoxLayout(tabs_widget)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(0)

        for label, key in self.tabs:
            btn = QPushButton(label)
            btn.setFlat(True)
            is_active = (key == self.active_tab)
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {'#1a1a1a' if is_active else '#888888'};
                    font-size: 20px;
                    font-weight: {'bold' if is_active else 'normal'};
                    border: none;
                    padding: 4px 16px;
                }}
                QPushButton:hover {{ color: #1a1a1a; }}
            """)
            # ✅ При клике отправляем ключ вкладки в универсальный сигнал
            btn.clicked.connect(lambda checked, k=key: self.nav_requested.emit(k))
            tabs_layout.addWidget(btn)

        layout.addWidget(tabs_widget)
        layout.addStretch(1)

        logout_btn = QPushButton("Выйти")
        logout_btn.setFixedWidth(110)
        logout_btn.clicked.connect(self.nav_logout.emit)
        layout.addWidget(logout_btn)