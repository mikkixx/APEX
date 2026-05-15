# test_manual.py
import sys
import os
import bcrypt
import time as std_time  # 🔧 Исправлен конфликт с datetime.time
from datetime import date, time, timedelta, datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.connection import db
from db.models import (User, SpecialistBinding, TrainingPlan, Session, TrainingDiary,
                       MedicalExam, MedicalMetric, Recommendation, Message, ReadinessStatus)
from core.operations import (
    register, login, logout, change_password, get_profile, edit_profile,
    get_diary_entries, get_diary_entry_details, add_diary_entry, edit_diary_entry, delete_diary_entry,
    get_medical_data, create_medical_exam, add_medical_metric, add_medical_recommendation,
    get_training_plan, sync_overdue_sessions, update_session_status, add_session,
    edit_session, delete_session, get_session_details, add_recommendation_to_session,
    delete_training_plan, create_training_plan, get_chat_partners, get_chat_partner_info,
    get_chat_messages, send_message, add_chat_partner, get_my_athletes,
    add_athlete_by_email, get_athlete_profile_full, update_athlete_status,
    remove_athlete_from_list, get_athlete_diary, add_diary_recommendation,
    get_athlete_plan_for_doctor, get_athlete_medical_data_for_coach, generate_report
)

# ============================================================================
# 📦 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def _safe_call(func, *args, expected_success=True, desc="", **kwargs):
    try:
        res = func(*args, **kwargs)
        if isinstance(res, bool):
            success = res == expected_success
            print(f"   {'✅' if success else '❌'} {desc}: {'Выполнено' if success else 'Вернуло False'}")
            return (success, "bool", None)
        status = '✅' if res[0] == expected_success else '❌'
        print(f"   {status} {desc}: {res[1]}")
        return res
    except Exception as e:
        print(f"   ❌ {desc}: Исключение — {type(e).__name__}: {e}")
        return (False, f"Exception: {e}", None)

def _create_test_user(role, email, spec, pwd="Test123"):
    try:
        return User.get(User.email == email).id
    except User.DoesNotExist:
        pw_hash = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
        u = User.create(
            last_name="Тестов", first_name="Пользователь", middle_name=None,
            email=email, password_hash=pw_hash, role=role, specialization=spec,
            photo_path=None, is_active=True
        )
        return u.id

def _bind_users(athlete_id, specialist_id):
    if not SpecialistBinding.select().where(
        SpecialistBinding.athlete == athlete_id, SpecialistBinding.specialist == specialist_id,
        SpecialistBinding.is_deleted == False
    ).exists():
        SpecialistBinding.create(athlete=athlete_id, specialist=specialist_id, status='активна', is_deleted=False)

def _create_test_plan(coach_id, athlete_id):
    plan = TrainingPlan.select().where(
        TrainingPlan.coach == coach_id, TrainingPlan.athlete == athlete_id, TrainingPlan.is_deleted == False
    ).first()
    if not plan:
        plan = TrainingPlan.create(
            athlete=athlete_id, coach=coach_id, title="Тестовый план",
            start_date=date.today(), end_date=date.today() + timedelta(days=7), is_deleted=False
        )
    return plan.id

# ============================================================================
# 🚀 ОСНОВНАЯ ЛОГИКА
# ============================================================================

def prepare_environment():
    print("📂 Подготовка тестового окружения...")
    ts = int(std_time.time())
    
    athlete_id = _create_test_user('спортсмен', f'athlete_{ts}@test.com', 'Бег')
    coach_id   = _create_test_user('тренер',    f'coach_{ts}@test.com', 'Лёгкая атлетика')
    doctor_id  = _create_test_user('врач',      f'doctor_{ts}@test.com', 'Спортивная медицина')
    
    _bind_users(athlete_id, coach_id)
    _bind_users(athlete_id, doctor_id)
    plan_id = _create_test_plan(coach_id, athlete_id)
    
    print(f"   ✅ Спортсмен: ID {athlete_id} | {f'athlete_{ts}@test.com'}")
    print(f"   ✅ Тренер:     ID {coach_id}   | {f'coach_{ts}@test.com'}")
    print(f"   ✅ Врач:       ID {doctor_id}  | {f'doctor_{ts}@test.com'}")
    print(f"   ✅ План:       ID {plan_id}")
    print("-" * 50)
    
    return athlete_id, coach_id, doctor_id, plan_id, f'athlete_{ts}@test.com', f'coach_{ts}@test.com'

def test_auth_and_profile(athlete_id, coach_id, athlete_email):
    print("\n🔐 [ГРУППА 1] Авторизация и профиль")
    _safe_call(register, "Иванов", "Иван", None, athlete_email, "Pass123", "Pass123", "спортсмен", "Бег",
               expected_success=False, desc="Регистрация дубликата email")
    _safe_call(register, "Петров", "Пётр", "Сергеевич", f"new_{int(std_time.time())}@test.com", "NewPass123", "NewPass123", "спортсмен", "Плавание",
               expected_success=True, desc="Регистрация нового пользователя")
    _safe_call(login, athlete_email, "WrongPass", expected_success=False, desc="Вход с неверным паролем")
    _safe_call(login, athlete_email, "Test123", expected_success=True, desc="Успешный вход")
    _safe_call(get_profile, athlete_id, expected_success=True, desc="Получение профиля спортсмена")
    _safe_call(edit_profile, athlete_id, "Иванов", "Иван", "Иванович", f"edit_{int(std_time.time())}@test.com", "Бег", None,
               expected_success=True, desc="Редактирование профиля")
    _safe_call(change_password, athlete_id, "Test123", "NewTest456", "NewTest456", expected_success=True, desc="Смена пароля")
    _safe_call(change_password, athlete_id, "NewTest456", "Test123", "Test123", expected_success=True, desc="Возврат пароля")
    _safe_call(logout, expected_success=True, desc="Выход из системы")

def test_diary(athlete_id):
    print("\n📓 [ГРУППА 2] Дневник нагрузок")
    _safe_call(add_diary_entry, athlete_id, date.today(), "Бег", 45, 5000, 7.5, 4, 8, "Норма",
               expected_success=True, desc="Добавление записи в дневник")
    _safe_call(add_diary_entry, athlete_id, date.today(), "Плавание", 30, 2000, 8.0, 3, 9, "Легко",
               expected_success=False, desc="Дубликат записи на дату")
    res = _safe_call(get_diary_entries, athlete_id, date.today()-timedelta(days=7), date.today(),
                     expected_success=True, desc="Получение списка записей")
    if res[0] and res[2]['entries']:
        entry_id = res[2]['entries'][0].id
        _safe_call(get_diary_entry_details, entry_id, athlete_id, expected_success=True, desc="Получение деталей записи")
        _safe_call(edit_diary_entry, entry_id, athlete_id, date.today(), "Бег", 50, 5500, 7.0, 5, 7, "Устал",
                   expected_success=True, desc="Редактирование записи")
        _safe_call(delete_diary_entry, entry_id, athlete_id, expected_success=True, desc="Удаление записи (мягкое)")
    _safe_call(get_diary_entries, athlete_id, activity_type="Бег", expected_success=True, desc="Фильтрация по типу активности")

def test_medical(athlete_id, doctor_id, coach_id):
    print("\n🏥 [ГРУППА 3] Медицинские данные")
    ts = int(std_time.time()) % 10000
    res = _safe_call(create_medical_exam, doctor_id, athlete_id, date.today(), f"Плановый осмотр {ts}",
                     expected_success=True, desc="Создание карточки осмотра")
    if res[0] and res[2]:
        exam_id = res[2]['exam_id']
        _safe_call(add_medical_metric, exam_id, doctor_id, "Пульс", 72, "уд/мин", 60, 100, expected_success=True, desc="Добавление показателя")
        _safe_call(add_medical_recommendation, doctor_id, exam_id, "Следить за давлением", expected_success=True, desc="Мед. рекомендация")
    _safe_call(get_medical_data, athlete_id, expected_success=True, desc="Просмотр медданных (спортсмен)")
    _safe_call(get_athlete_medical_data_for_coach, coach_id, athlete_id, expected_success=True, desc="Просмотр медданных (тренер)")

def test_plans_and_sessions(athlete_id, coach_id, plan_id):
    print("\n📅 [ГРУППА 4] Тренировочные планы и занятия")
    _safe_call(get_training_plan, athlete_id, expected_success=True, desc="Просмотр плана (спортсмен)")
    res = _safe_call(add_session, coach_id, plan_id, date.today()+timedelta(days=1), time(10,0), "Силовая", 60, expected_success=True, desc="Добавление занятия")
    if res[0]:
        session = Session.select().where(Session.plan == plan_id).order_by(Session.id.desc()).first()
        if session:
            _safe_call(get_session_details, coach_id, session.id, expected_success=True, desc="Просмотр деталей занятия")
            _safe_call(update_session_status, session.id, athlete_id, 'выполнено', expected_success=True, desc="Обновление статуса занятия")
            _safe_call(add_recommendation_to_session, coach_id, session.id, "Отличная техника!", expected_success=True, desc="Рекомендация к занятию")
            _safe_call(sync_overdue_sessions, athlete_id, expected_success=False, desc="Синхронизация просроченных (нет просрочек)")
    _safe_call(create_training_plan, coach_id, athlete_id, date.today()+timedelta(days=10), date.today()+timedelta(days=17), "Подготовительный", expected_success=True, desc="Создание нового плана")
    future_plan = TrainingPlan.select().where(TrainingPlan.coach == coach_id, TrainingPlan.start_date > date.today()).first()
    if future_plan:
        _safe_call(delete_training_plan, coach_id, future_plan.id, expected_success=True, desc="Удаление тестового плана")

def test_chat(athlete_id, coach_id, coach_email):
    print("\n💬 [ГРУППА 5] Чат и сообщения")
    _safe_call(add_chat_partner, athlete_id, coach_email, expected_success=True, desc="Добавление тренера в чат")
    _safe_call(get_chat_partners, athlete_id, expected_success=True, desc="Список собеседников")
    _safe_call(get_chat_partner_info, coach_id, expected_success=True, desc="Информация о собеседнике")
    _safe_call(send_message, athlete_id, coach_id, "Привет, тренер!", expected_success=True, desc="Отправка сообщения")
    _safe_call(get_chat_messages, athlete_id, coach_id, expected_success=True, desc="Получение истории чата")
    _safe_call(get_chat_messages, athlete_id, coach_id, search_query="тренер", expected_success=True, desc="Поиск по чату")

def test_athlete_management(coach_id, athlete_id, doctor_id, athlete_email):
    print("\n👥 [ГРУППА 6] Управление спортсменами")
    _safe_call(get_my_athletes, coach_id, expected_success=True, desc="Список спортсменов тренера")
    _safe_call(add_athlete_by_email, coach_id, athlete_email, expected_success=False, desc="Добавление уже привязанного спортсмена")
    _safe_call(get_athlete_profile_full, coach_id, athlete_id, expected_success=True, desc="Полный профиль спортсмена")
    _safe_call(update_athlete_status, coach_id, athlete_id, 'устал', expected_success=True, desc="Смена статуса: устал")
    _safe_call(update_athlete_status, doctor_id, athlete_id, 'болен', expected_success=True, desc="Блокировка статуса врачом")
    _safe_call(update_athlete_status, coach_id, athlete_id, 'здоров', expected_success=False, desc="Попытка тренера снять блокировку врача")
    _safe_call(get_athlete_diary, coach_id, athlete_id, expected_success=True, desc="Просмотр дневника (тренер)")
    diary_entry = TrainingDiary.select().where(TrainingDiary.athlete == athlete_id).first()
    if diary_entry:
        _safe_call(add_diary_recommendation, coach_id, diary_entry.id, "Следи за восстановлением!", expected_success=True, desc="Рекомендация к дневнику")
    _safe_call(get_athlete_plan_for_doctor, doctor_id, athlete_id, expected_success=True, desc="Просмотр плана (врач)")

def test_reports(coach_id, athlete_id):
    print("\n📊 [ГРУППА 7] Отчёты")
    _safe_call(generate_report, coach_id, athlete_id, 'training', date.today()-timedelta(days=7), date.today(), 'excel', expected_success=True, desc="Генерация тренировочного отчёта")
    _safe_call(generate_report, coach_id, athlete_id, 'medical', date.today()-timedelta(days=30), date.today(), 'excel', expected_success=True, desc="Генерация медицинского отчёта")
    _safe_call(generate_report, coach_id, athlete_id, 'invalid', date.today(), date.today(), 'excel', expected_success=False, desc="Неподдерживаемый тип отчёта")

def main():
    print("🚀 Запуск полного набора тестов APEX")
    print("=" * 60)
    try:
        if db.is_closed():
            db.connect()
        print("✅ Подключение к БД успешно")
        
        athlete_id, coach_id, doctor_id, plan_id, ath_email, coach_email = prepare_environment()
        
        test_auth_and_profile(athlete_id, coach_id, ath_email)
        test_diary(athlete_id)
        test_medical(athlete_id, doctor_id, coach_id)
        test_plans_and_sessions(athlete_id, coach_id, plan_id)
        test_chat(athlete_id, coach_id, coach_email)
        test_athlete_management(coach_id, athlete_id, doctor_id, ath_email)
        test_reports(coach_id, athlete_id)
        
        print("\n" + "=" * 60)
        print("🏁 Все тесты завершены.")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if not db.is_closed():
            db.close()
            print("🔌 Соединение с БД закрыто")

if __name__ == "__main__":
    main()