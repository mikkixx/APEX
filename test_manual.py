import sys
from core.operations import register, login, logout, change_password, get_profile
from db.models import User
from db.connection import db

def run_tests():
    print("🔹 [1] Тест регистрации (опциональное отчество)")
    res = register(
        last_name="Иванов", first_name="Алексей", middle_name="",  # Пустое отчество
        email="test_ivanov@example.com", password="SecurePass1", 
        confirm_password="SecurePass1", role="спортсмен", specialization="Плавание"
    )
    print(f"   ✅ Результат: {res[0]} | Сообщение: {res[1]}\n")
    if not res[0]: return

    print("🔹 [2] Тест входа")
    res = login("test_ivanov@example.com", "SecurePass1")
    print(f"   ✅ Результат: {res[0]} | Сообщение: {res[1]}")
    if res[0]:
        user_data = res[2]
        print(f"   📦 Данные сессии: {user_data}\n")
        
        print("🔹 [3] Тест просмотра профиля")
        res_prof = get_profile(user_data['id'])
        print(f"   ✅ Результат: {res_prof[0]} | Сообщение: {res_prof[1]}")
        if res_prof[0]: print(f"   📄 Профиль: {res_prof[2]}\n")

        print("🔹 [4] Тест смены пароля")
        res_pw = change_password(user_data['id'], "SecurePass1", "NewSecurePass2", "NewSecurePass2")
        print(f"   ✅ Результат: {res_pw[0]} | Сообщение: {res_pw[1]}\n")

    print("🔹 [5] Тест выхода")
    res_out = logout()
    print(f"   ✅ Результат: {res_out[0]} | Сообщение: {res_out[1]}\n")

    # 🧹 Очистка тестовых данных
    try:
        test_user = User.get(User.email == "test_ivanov@example.com")
        test_user.delete_instance()
        print("♻️ Тестовый пользователь удалён из БД.")
    except Exception:
        pass

if __name__ == "__main__":
    print("🚀 Запуск ручных тестов бизнес-логики...")
    print("="*50)
    run_tests()
    print("="*50)
    print("✅ Тестирование завершено.")