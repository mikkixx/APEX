from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt

class BaseWindow(QMainWindow):
    active_tab = ""
    # ✅ Вкладки по умолчанию (Спортсмен)
    NAV_TABS = [
        ("Тренировочный план", "training"),
        ("Дневник нагрузок",   "diary"),
        ("Медкарта",           "medical"),
        ("Профиль",            "profile"),
        ("Чаты",               "chats"),
    ]

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setMinimumSize(1200, 750)
        self.setWindowTitle("APEX")

        central = QWidget()
        self.setCentralWidget(central)
        self._main_layout = QVBoxLayout(central)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._build_navbar()

        self.content = QWidget()
        self._content_layout = QVBoxLayout(self.content)
        self._content_layout.setContentsMargins(40, 32, 40, 32)
        self._main_layout.addWidget(self.content)

    def _build_navbar(self):
        from ui.navbar import NavBar
        # ✅ Передаем список вкладок и активный ключ
        self.navbar = NavBar(tabs=self.NAV_TABS, active_tab=self.active_tab)
        self.navbar.nav_requested.connect(self._navigate)
        self.navbar.nav_logout.connect(self._logout)
        self._main_layout.addWidget(self.navbar)

    def _navigate(self, tab):
        if tab == self.active_tab:
            return
        try:
            if tab == "training":
                from ui.training_plan_window import TrainingPlanWindow
                w = TrainingPlanWindow(self.user_data)
            elif tab == "diary":
                from ui.diary_window import DiaryWindow
                w = DiaryWindow(self.user_data)
            elif tab == "medical":
                from ui.medical_window import MedicalWindow
                w = MedicalWindow(self.user_data)
            elif tab == "profile":
                from ui.profile_window import ProfileWindow
                w = ProfileWindow(self.user_data)
            elif tab == "chats":
                from ui.chats_window import ChatsWindow
                w = ChatsWindow(self.user_data)
            else:
                return

            # ✅ Сохраняем ссылку на новое окно, скрываем текущее, затем показываем новое
            self._next_window = w
            self.hide()
            w.show()

        except Exception as e:
            import traceback
            import sys
            print(f"\n🔴 КРИТИЧЕСКАЯ ОШИБКА при открытии вкладки '{tab}':")
            traceback.print_exc()
            sys.stderr.flush()
            self.show()  # Восстанавливаем текущее окно если новое не открылось
            QMessageBox.critical(self, "Ошибка инициализации", f"Не удалось открыть окно:\n{e}")

    def _logout(self):
        from ui.login_window import LoginWindow
        self._login = LoginWindow()
        self._login.show()
        self.close()


class SpecialistBaseWindow(BaseWindow):
    """Базовое окно для тренера/врача. Наследует всю логику, переопределяет только вкладки."""
    # ✅ Переопределяем список вкладок для специалистов
    NAV_TABS = [
        ("Мои спортсмены", "athletes"),
        ("Отчеты",         "reports"),
        ("Профиль",        "profile"),
        ("Чаты",           "chats"),
    ]