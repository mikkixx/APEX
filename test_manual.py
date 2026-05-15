# test_coach_plan_med.py
import sys
from datetime import date, timedelta
import bcrypt
from db.connection import db
from db.models import User, SpecialistBinding, TrainingPlan, Session, Recommendation, MedicalExam, MedicalMetric
from core.operations import (
    get_athlete_sessions, create_training_plan, edit_session,
    delete_training_plan, add_recommendation_to_session, get_athlete_medical_data_for_coach
)

def run_tests():
    print("🔹 [0] Подготовка тестовых пользователей")
    try:
        coach = User.get(User.email == "coach_test@test.ru")
        athlete = User.get(User.email == "ath_test@test.ru")
    except Exception:
        pw = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode('utf-8')
        coach = User.create(email="coach_test@test.ru", password_hash=pw, last_name="Тренер", first_name="Тест", role="тренер", specialization="Плавание")
        athlete = User.create(email="ath_test@test.ru", password_hash=pw, last_name="Спортсмен", first_name="Тест", role="спортсмен", specialization="Бег")

    # Привязка
    SpecialistBinding.get_or_create(athlete=athlete, specialist=coach, defaults={'status': 'активна', 'is_deleted': False})
    print(f"   ✅ ID Тренера: {coach.id}, Спортсмена: {athlete.id}\n")

    today = date.today()
    start_d = today
    end_d = today + timedelta(days=14)

    print("🔹 [28] Создание плана")
    res_c = create_training_plan(coach.id, athlete.id, start_d, end_d, "План на месяц")
    print(f"   {'✅' if res_c[0] else '❌'} {res_c[1]}")
    plan_id = res_c[2]['plan_id'] if res_c[0] else None

    # Создаём тестовое занятие вручную
    if plan_id:
        sess = Session.create(plan=plan_id, date=today, activity_type="Бег", duration=30, status="запланировано", is_deleted=False)
        print(f"   📝 Создано занятие ID: {sess.id}\n")

    print(" [27] Просмотр плана (пагинация 3 записи)")
    res_v = get_athlete_sessions(coach.id, athlete.id)
    print(f"   {'✅' if res_v[0] else '❌'} {res_v[1]} (Занятий: {len(res_v[2]['sessions'])})")
    
    sess_id = None
    if res_v[0] and res_v[2]['sessions']:
        sess_id = res_v[2]['sessions'][0]['id']
        print(f"    Заголовок карточки: {res_v[2]['sessions'][0]['plan_header']}")

        print("\n🔹 [29] Редактирование занятия")
        res_e = edit_session(coach.id, sess_id, today, None, "Интервалы", 45)
        print(f"   {'✅' if res_e[0] else '❌'} {res_e[1]}")

        print("\n🔹 [29] Блокировка редактирования (статус 'выполнено')")
        Session.update(status='выполнено').where(Session.id == sess_id).execute()
        res_block = edit_session(coach.id, sess_id, today, None, "Бег", 30)
        print(f"   {'✅ (ожидаемо)' if not res_block[0] else '❌'} {res_block[1]}")

        print("\n🔹 [31] Рекомендация (сначала вернём статус 'запланировано')")
        Session.update(status='запланировано').where(Session.id == sess_id).execute()
        res_rec_fail = add_recommendation_to_session(coach.id, sess_id, "Тест")
        print(f"   {'✅ (ожидаемо)' if not res_rec_fail[0] else '❌'} {res_rec_fail[1]}")

        # Ставим 'выполнено' и пробуем снова
        Session.update(status='выполнено').where(Session.id == sess_id).execute()
        res_rec = add_recommendation_to_session(coach.id, sess_id, "Отличная техника, держи темп!")
        print(f"   {'✅' if res_rec[0] else '❌'} {res_rec[1]}")

        print("\n🔹 [30] Удаление плана")
        res_d = delete_training_plan(coach.id, plan_id)
        print(f"   {'✅' if res_d[0] else '❌'} {res_d[1]}")

    print("\n🔹 [32] Медданные (с фильтрами)")
    exam = MedicalExam.create(athlete=athlete, doctor=coach, exam_date=today, exam_type="Плановый", is_deleted=False)
    MedicalMetric.create(exam=exam, metric_type="Пульс", value=72, unit="уд/мин", is_critical=False)

    res_m = get_athlete_medical_data_for_coach(coach.id, athlete.id, exam_date=today)
    print(f"   {'✅' if res_m[0] else '❌'} {res_m[1]} (Осмотров: {len(res_m[2])})")
    if res_m[0] and res_m[2]:
        d = res_m[2][0]
        print(f"   📅 {d['exam_date']} | {d['exam_type']} | Врач: {d['doctor_fio']} ({d['doctor_email']})")

    print("\n♻️ Очистка тестовых данных...")
    try:
        Recommendation.delete().execute()
        MedicalMetric.delete().execute()
        MedicalExam.delete().execute()
        Session.delete().execute()
        TrainingPlan.delete().execute()
        SpecialistBinding.delete().execute()
        User.delete().execute()
        print("✅ База очищена. Тесты завершены.")
    except Exception as e:
        print(f"⚠️ Ошибка очистки: {e}")

if __name__ == "__main__":
    print("🚀 Тестирование FR-027 – FR-032")
    print("="*50)
    run_tests()
    print("="*50)