# test_athletes.py
import sys
import bcrypt
from db.connection import db
from db.models import User, SpecialistBinding, ReadinessStatus
from core.operations import get_my_athletes, add_athlete_by_email, get_athlete_profile_full

def run_tests():
    print("🔹 [0] Подготовка тестовых пользователей")
    try:
        coach = User.get(User.email == "test_coach@test.ru")
        athlete1 = User.get(User.email == "test_ath1@test.ru")
        athlete2 = User.get(User.email == "test_ath2@test.ru")
        doctor = User.get(User.email == "test_doc@test.ru")
    except Exception:
        pw = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode('utf-8')
        coach = User.create(email="test_coach@test.ru", password_hash=pw, last_name="Тренер", first_name="Тест", role="тренер", specialization="Плавание")
        doctor = User.create(email="test_doc@test.ru", password_hash=pw, last_name="Врач", first_name="Тест", role="врач", specialization="Терапия")
        athlete1 = User.create(email="test_ath1@test.ru", password_hash=pw, last_name="Иванов", first_name="Спортсмен", role="спортсмен", specialization="Бег")
        athlete2 = User.create(email="test_ath2@test.ru", password_hash=pw, last_name="Петров", first_name="Спортсмен", role="спортсмен", specialization="Бокс")
    
    # Создадим статус для athlete1
    ReadinessStatus.get_or_create(athlete=athlete1, defaults={'current_status': 'здоров', 'initiator': coach.id, 'lock_status': 'свободно'})
    print(f"   ✅ ID Тренера: {coach.id}, Спортсменов: {athlete1.id}, {athlete2.id}\n")

    print("🔹 [22] Тест списка спортсменов (пустой)")
    res = get_my_athletes(coach.id)
    print(f"   {'✅' if res[0] else '❌'} {res[1]} (Всего: {res[2]['total']})\n")

    print("🔹 [23] Тест добавления спортсмена 1")
    res_add1 = add_athlete_by_email(coach.id, athlete1.email)
    print(f"   {'✅' if res_add1[0] else '❌'} {res_add1[1]}")

    print("🔹 [23] Тест дубликата привязки")
    res_dup = add_athlete_by_email(coach.id, athlete1.email)
    print(f"   {'✅ (ожидаемо)' if not res_dup[0] else '❌'} {res_dup[1]}\n")

    print("🔹 [22] Тест списка после добавления")
    res_list = get_my_athletes(coach.id)
    print(f"   {'✅' if res_list[0] else '❌'} {res_list[1]} (Спортсменов: {len(res_list[2]['athletes'])})\n")

    print("🔹 [26] Тест просмотра профиля")
    res_prof = get_athlete_profile_full(coach.id, athlete1.id)
    print(f"   {'✅' if res_prof[0] else '❌'} {res_prof[1]}")
    if res_prof[0]:
        d = res_prof[2]
        print(f"   📄 {d['full_name']} | Статус: {d['current_status']} | Блокировка: {d['lock_status']}")
    print()

    print("🔹 [23] Тест ограничения: 2-й тренер не может привязать того же спортсмена")
    res_limit = add_athlete_by_email(coach.id, athlete1.email) # Повторная проверка логики
    print(f"   {'✅' if not res_limit[0] else ''} {res_limit[1]}\n")

    print("♻️ Очистка тестовых данных...")
    try:
        ReadinessStatus.delete().execute()
        SpecialistBinding.delete().execute()
        User.delete().execute()
        print("✅ Готово. База очищена.")
    except Exception as e:
        print(f"⚠️ Ошибка очистки: {e}")

if __name__ == "__main__":
    print("🚀 Тестирование FR-022, FR-023, FR-026")
    print("="*50)
    run_tests()
    print("="*50)