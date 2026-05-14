# test_plan_chat.py
import sys
from datetime import date, timedelta
import bcrypt
from db.connection import db
from db.models import User, TrainingPlan, Session, Message
from core.operations import (
    get_training_plan, sync_overdue_sessions, update_session_status,
    get_chat_partners, get_chat_partner_info, get_chat_messages,
    send_message, add_chat_partner, delete_account
)

def run_tests():
    print("🔹 [1] Подготовка тестовых пользователей")
    try:
        u1 = User.get(User.email == "test_athlete@test.ru")
        u2 = User.get(User.email == "test_coach@test.ru")
    except Exception:
        pw = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode('utf-8')
        u1 = User.create(email="test_athlete@test.ru", password_hash=pw, last_name="Спортсмен", first_name="Тест", role="спортсмен", specialization="Бег")
        u2 = User.create(email="test_coach@test.ru", password_hash=pw, last_name="Тренер", first_name="Тест", role="тренер", specialization="Лёгкая атлетика")
    print(f"   ✅ ID спортсмена: {u1.id}, ID тренера: {u2.id}\n")

    print("🔹 [2] Тест плана и занятий (FR-016)")
    today = date.today()
    plan, _ = TrainingPlan.get_or_create(athlete=u1, coach=u2, title="Тест план", start_date=today, end_date=today+timedelta(days=6), defaults={'is_deleted': False})
    sess, _ = Session.get_or_create(plan=plan, date=today, activity_type="Бег", duration=30, status="запланировано", defaults={'is_deleted': False})
    
    res_plan = get_training_plan(u1.id)
    print(f"   {'✅' if res_plan[0] else '❌'} {res_plan[1]} (Занятий: {len(res_plan[2][0]['sessions'])})\n")

    print("🔹 [3] Тест синхронизации статусов (FR-017)")
    res_sync = sync_overdue_sessions(u1.id)
    print(f"   ✅ Просроченные обновлены: {res_sync}")
    
    res_upd = update_session_status(sess.id, u1.id, "выполнено")
    print(f"   {'✅' if res_upd[0] else '❌'} {res_upd[1]}\n")

    print("🔹 [4] Тест чата: добавление, отправка, чтение (FR-018/019/046)")
    res_add = add_chat_partner(u1.id, u2.email)
    print(f"   {'✅' if res_add[0] else '❌'} {res_add[1]}")
    
    res_send = send_message(u1.id, u2.id, "Привет, как план?")
    print(f"   {'✅' if res_send[0] else '❌'} {res_send[1]}")
    
    res_msg = get_chat_messages(u1.id, u2.id)
    print(f"   {'✅' if res_msg[0] else '❌'} {res_msg[1]} (Сообщений: {len(res_msg[2])})\n")

    print("🔹 [5] Тест списка партнёров и удаления (FR-021)")
    res_part = get_chat_partners(u1.id)
    print(f"   {'✅' if res_part[0] else ''} {res_part[1]} (Партнёров: {len(res_part[2])})")
    
    # Тест удаления (не закрываем БД, чтобы не ломать следующие тесты, просто помечаем)
    res_del = delete_account(u1.id)
    print(f"   {'✅' if res_del[0] else '❌'} {res_del[1]}\n")

    print("♻️ Очистка тестовых данных...")
    try:
        Message.delete().execute()
        Session.delete().execute()
        TrainingPlan.delete().execute()
        u1.delete_instance()
        u2.delete_instance()
        print("✅ Готово. База очищена.")
    except Exception as e:
        print(f"⚠️ Ошибка очистки: {e}")

if __name__ == "__main__":
    print("🚀 Тестирование FR-016 – FR-021, FR-046")
    print("="*50)
    run_tests()
    print("="*50)