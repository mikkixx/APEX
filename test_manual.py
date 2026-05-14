# test_diary_profile.py
import sys
from datetime import date
import bcrypt
from db.connection import db
from db.models import User, TrainingDiary
from core.operations import (
    edit_profile,
    get_diary_entries,
    get_diary_entry_details,
    add_diary_entry
)

def run_tests():
    print("🔹 [1] Подготовка тестового пользователя")
    try:
        user = User.get(User.email == "test_diary@example.com")
    except Exception:
        hash_pw = bcrypt.hashpw(b"TestPass123", bcrypt.gensalt()).decode('utf-8')
        user = User.create(
            email="test_diary@example.com", password_hash=hash_pw,
            last_name="Тестов", first_name="Спортсмен", role="спортсмен", specialization="Бег"
        )
    print(f"   ✅ ID пользователя: {user.id}\n")

    uid = user.id
    today = date.today()

    print("🔹 [2] Тест редактирования профиля")
    res = edit_profile(uid, "Иванов", "Иван", None, "new@mail.ru", "Плавание")
    print(f"   {'✅' if res[0] else '❌'} {res[1]}\n")

    print("🔹 [3] Тест добавления записи в дневник")
    res_add = add_diary_entry(
        athlete_id=uid, entry_date=today, activity_type="Кросс",
        duration=45, steps=8500, sleep_hours=7.5, fatigue=4, mood=8
    )
    print(f"   {'✅' if res_add[0] else '❌'} {res_add[1]}\n")

    # Получаем ID созданной записи для следующих тестов
    entry_id = None
    if res_add[0]:
        entry = TrainingDiary.select().where(
            (TrainingDiary.athlete == uid) & (TrainingDiary.date == today)
        ).order_by(TrainingDiary.id.desc()).get()
        entry_id = entry.id

    print("🔹 [4] Тест дубликата (тот же день)")
    res_dup = add_diary_entry(uid, today, "Ходьба", 30, 5000, 8, 3, 7)
    print(f"   {'✅ (ожидаемо)' if not res_dup[0] else '❌'} {res_dup[1]}\n")

    print("🔹 [5] Тест просмотра дневника (пагинация)")
    res_list = get_diary_entries(uid)
    if res_list[0]:
        print(f"   ✅ Записей найдено: {res_list[2]['total']}, Страница: {res_list[2]['page']}")
    else:
        print(f"   ❌ {res_list[1]}")
    print()

    if entry_id:
        print("🔹 [6] Тест просмотра деталей записи")
        res_detail = get_diary_entry_details(entry_id, uid)
        print(f"   {'✅' if res_detail[0] else '❌'} {res_detail[1]}")
        if res_detail[0]:
            d = res_detail[2]
            print(f"   📄 Тип: {d['entry'].activity_type} | Шаги: {d['entry'].steps}")
            print(f"   💬 Комментариев специалистов: {len(d['comments'])}")
        print()

    # 🧹 Очистка
    print("♻️ Очистка тестовых данных...")
    try:
        TrainingDiary.delete().where(TrainingDiary.athlete == uid).execute()
        user.delete_instance()
        print("✅ Готово. База очищена.")
    except Exception as e:
        print(f"⚠️ Ошибка очистки: {e}")

if __name__ == "__main__":
    print("🚀 Тестирование FR-006 – FR-010")
    print("="*50)
    run_tests()
    print("="*50)