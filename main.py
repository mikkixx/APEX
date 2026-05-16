# main.py
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QFontDatabase

# Добавляем корень проекта в путь импортов
sys.path.insert(0, str(Path(__file__).parent))

from db.connection import db

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.login_window = None
        self.register_window = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("APEX — Система мониторинга здоровья студентов-спортсменов")
        self.setMinimumSize(1024, 720)
        self.setStyleSheet(self._get_stylesheet())
        self._load_fonts()
        
        # При запуске сразу показываем окно входа
        self._show_login_screen()

    def _load_fonts(self):
        """Подгружает шрифт Alegreya из папки fonts"""
        font_path = Path(__file__).parent / "fonts" / "Alegreya-Regular.ttf"
        if font_path.exists():
            QFontDatabase.addApplicationFont(str(font_path))
            bold_path = font_path.parent / "Alegreya-Bold.ttf"
            if bold_path.exists():
                QFontDatabase.addApplicationFont(str(bold_path))

    def _get_stylesheet(self):
        """Глобальные стили в точном соответствии с вайрфреймами"""
        return """
        QMainWindow { background-color: #FFFFFF; }
        QWidget#main-container { background-color: #FFFFFF; }
        
        QLabel { color: #73A15D; font-family: 'Alegreya', 'Times New Roman', serif; }
        QLabel#logo { font-size: 26px; font-weight: bold; letter-spacing: 2px; color: #73A15D; }
        QLabel#page-title { font-size: 30px; font-weight: bold; margin-bottom: 20px; color: #73A15D; }
        QLabel#auth-subtitle { color: #73A15D; font-size: 16px; margin-bottom: 30px; }

        /* Навигация */
        QFrame#top-bar { border-bottom: 1px solid #E5E5E5; background-color: #FFFFFF; }
        QPushButton#nav-btn {
            background: transparent; border: none; color: #73A15D;
            font-family: 'Alegreya', serif; font-size: 16px; padding: 10px 18px;
            border-radius: 10px;
        }
        QPushButton#nav-btn:hover { background-color: #F4F7F0; color: #557A42; }
        QPushButton#nav-btn:checked, QPushButton#nav-btn.active {
            background-color: #73A15D; color: white; font-weight: bold;
        }
        QPushButton#logout-btn {
            background-color: #111111; color: white; border: none;
            border-radius: 20px; padding: 8px 24px; font-family: 'Alegreya', serif; font-size: 15px;
        }
        QPushButton#logout-btn:hover { background-color: #333333; }

        /* Кнопки авторизации */
        QPushButton#auth-btn {
            background-color: #73A15D; color: white; border: none;
            border-radius: 12px; padding: 14px 40px; font-size: 17px; font-weight: bold;
            font-family: 'Alegreya', serif; margin: 0 10px;
        }
        QPushButton#auth-btn:hover { background-color: #638F4D; }
        QPushButton#auth-btn:pressed { background-color: #557A42; }

        /* Ссылки */
        QPushButton#link-btn {
            background: transparent; border: none; color: #73A15D;
            font-size: 15px; font-family: 'Alegreya', serif;
        }
        QPushButton#link-btn:hover { color: #557A42; }
        """

    def _show_login_screen(self):
        """Открывает окно входа"""
        from ui.login_window import LoginWindow
        if self.login_window:
            self.login_window.close()
            
        self.login_window = LoginWindow(
            show_register_callback=self._show_register_screen
        )
        self.login_window.show()

    def _show_register_screen(self):
        """Открывает окно регистрации"""
        from ui.register_window import RegisterWindow
        if self.register_window:
            self.register_window.close()
            
        self.register_window = RegisterWindow(
            show_login_callback=self._show_login_screen
        )
        self.register_window.show()

    def _handle_login_success(self, user_data):
        """Вызывается после успешного входа/регистрации"""
        self.current_user = user_data
        
        # Закрываем окна авторизации
        if self.login_window:
            self.login_window.close()
        if self.register_window:
            self.register_window.close()
            
        # Строим главное окно
        self._setup_dashboard()

    def _setup_dashboard(self):
        """Строит главное окно с навигацией под роль"""
        if self.centralWidget():
            self.setCentralWidget(None)

        main_widget = QWidget(objectName="main-container")
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Верхняя панель навигации
        top_bar = QFrame(objectName="top-bar")
        nav_layout = QHBoxLayout(top_bar)
        nav_layout.setContentsMargins(24, 12, 24, 12)

        logo = QLabel("APEX")
        logo.setObjectName("logo")
        nav_layout.addWidget(logo)

        self.nav_buttons = []
        self.stacked_widget = QStackedWidget()
        role = self.current_user.get('role', '')

        # Настройка меню в зависимости от роли
        if role == 'спортсмен':
            pages = ['Тренировочный план', 'Дневник нагрузок', 'Медкарта', 'Профиль', 'Чаты']
        else:  # тренер или врач
            pages = ['Мои спортсмены', 'Отчеты', 'Профиль', 'Чаты']

        for page_name in pages:
            btn = QPushButton(page_name)
            btn.setObjectName("nav-btn")
            btn.clicked.connect(lambda _, name=page_name: self._switch_page(name))
            nav_layout.addWidget(btn)
            self.nav_buttons.append((btn, page_name))

            # Создаём заготовку страницы
            page = self._create_page_widget(page_name)
            self.stacked_widget.addWidget(page)

        nav_layout.addStretch()

        logout_btn = QPushButton("Выйти")
        logout_btn.setObjectName("logout-btn")
        logout_btn.clicked.connect(self._logout)
        nav_layout.addWidget(logout_btn)

        main_layout.addWidget(top_bar)
        main_layout.addWidget(self.stacked_widget)
        self.setCentralWidget(main_widget)

        # Активируем первую вкладку по умолчанию
        self._switch_page(pages[0])

    def _switch_page(self, page_name):
        """Переключает вкладку и обновляет стили кнопок"""
        for btn, name in self.nav_buttons:
            is_active = (name == page_name)
            btn.setChecked(is_active)
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        index = next(i for i, (_, name) in enumerate(self.nav_buttons) if name == page_name)
        self.stacked_widget.setCurrentIndex(index)

    def _create_page_widget(self, title):
        """Создаёт пустую страницу-заготовку"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 30, 40, 40)

        label = QLabel(title)
        label.setObjectName("page-title")
        layout.addWidget(label)

        info = QLabel("Интерфейс раздела будет подключён здесь.\nНавигация и стили уже настроены.")
        info.setStyleSheet("color: #73A15D; font-size: 16px; line-height: 1.5;")
        layout.addWidget(info)
        layout.addStretch()

        return widget

    def _logout(self):
        """Выход из системы"""
        self.current_user = None
        
        # Закрываем главное окно
        if self.centralWidget():
            self.setCentralWidget(None)
            
        try:
            from core.operations import logout
            logout()
        except Exception:
            pass
            
        # Возвращаемся на экран входа
        self._show_login_screen()

    def closeEvent(self, event):
        """Корректное закрытие БД при выходе"""
        try:
            if not db.is_closed():
                db.close()
        except Exception:
            pass
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Alegreya", 11))  # Шрифт по умолчанию для всего приложения
    
    window = MainWindow()
    # Не показываем главное окно сразу, оно покажет само login_window
    sys.exit(app.exec())