# test_diary_medical.py
from datetime import date
import bcrypt
from db.connection import db
from db.models import User, TrainingDiary, MedicalExam, MedicalMetric
from core.operations import edit_diary_entry, delete_diary_entry, get_medical_data

def run_tests():
    print("🔹 [1] Подготовка тестового спортсмена")
    try:
        athlete = User.get(User.email == "test_med@example.com")
    except Exception:
        hash_pw = bcrypt.hashpw(b"TestPass123", bcrypt.gensalt()).decode('utf-8')
        athlete = User.create(
            email="test_med@example.com", password_hash=hash_pw,
            last_name="Иванов", first_name="Тест", role="спортсмен", specialization="Бег"
        )
    uid = athlete.id
    print(f"   ✅ ID спортсмена: {uid}\n")

    today = date.today()

    print("🔹 [2] Создание записи дневника для теста")
    try:
        entry = TrainingDiary.create(
            athlete=uid, date=today, activity_type="Бег", duration=30,
            steps=5000, sleep_hours=7.0, fatigue=3, mood=8
        )
        eid = entry.id
    except Exception:
        # Если запись за сегодня уже есть, берем её ID
        entry = TrainingDiary.select().where(
            (TrainingDiary.athlete == uid) & (TrainingDiary.date == today)
        ).order_by(TrainingDiary.id.desc()).get()
        eid = entry.id
    print(f"   ✅ ID записи: {eid}\n")

    print("🔹 [3] Тест редактирования (FR-011)")
    res_edit = edit_diary_entry(eid, uid, today, "Плавание", 45, 6000, 8.0, 4, 9, "Тест коммент")
    print(f"   {'✅' if res_edit[0] else '❌'} {res_edit[1]}")
    if res_edit[0]: print(f"   🔍 Критичное изменение: {res_edit[2].get('needs_review')}\n")

    print("🔹 [4] Тест удаления (FR-012)")
    res_del = delete_diary_entry(eid, uid)
    print(f"   {'✅' if res_del[0] else '❌'} {res_del[1]}\n")

    print("🔹 [5] Тест просмотра медкарты (FR-014/015)")
    res_med = get_medical_data(uid)
    print(f"   {'✅' if res_med[0] else '❌'} {res_med[1]}")
    if res_med[0]:
        count = len(res_med[2])
        print(f"   📦 Найдено осмотров: {count}")
        if count > 0:
            d = res_med[2][0]
            print(f"   📅 {d['exam_date']} | {d['exam_type']} | 👨‍⚕️ {d['doctor_fio']}")
        print()

    print("♻️ Очистка тестовых данных...")
    try:
        TrainingDiary.delete().where(TrainingDiary.athlete == uid).execute()
        athlete.delete_instance()
        print("✅ База очищена. Тесты завершены.")
    except Exception as e:
        print(f"⚠️ Ошибка очистки: {e}")

if __name__ == "__main__":
    print("🚀 Тестирование FR-011, FR-012, FR-014/015")
    print("="*50)
    run_tests()
    print("="*50)