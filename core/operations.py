import re
import bcrypt
from peewee import fn, DoesNotExist, IntegrityError, OperationalError
from datetime import date, timedelta, datetime


from db.models import User, ReadinessStatus, TrainingDiary, Recommendation, MedicalExam, MedicalMetric, TrainingPlan, Session, Message, SpecialistBinding
from db.connection import db

def _is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))

def register(last_name, first_name, middle_name, email, password, confirm_password, role, specialization):
    if not all ([last_name, first_name, email, password, confirm_password, role, specialization]):
        return False, 'Заполните все обязательные поля', None
    if not _is_valid_email(email):
        return False, 'Неверный формат email', None
    if len(password) < 6:
        return False, 'Пароль должен содержать не менее 6 символов', None
    if password != confirm_password:
        return False, 'Пароли не совпадают', None
    
    try:
        if User.select().where(User.email == email).exists():
            return False, 'Пользователь с таким email уже существует. Пожалуйста, войдите в систему.', None
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        User.create(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name or None,
            email=email,
            password_hash=password_hash,
            role=role,
            specialization=specialization
        )
        return True, 'Регистрация прошла успешно. Перейдите к авторизации.', None
    except OperationalError as e:
        return False, f"Ошибка подключения к БД: {e}", None
    
def login(email, password):
    if not email or not password:
        return False, 'Заполните поля email и пароль', None
    
    try:
        user = User.get(User.email == email)

        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            user_data = {
                'id': user.id,
                'last_name': user.last_name,
                'first_name': user.first_name,
                'middle_name': user.middle_name or "",
                'role': user.role,
                'specialization': user.specialization
            }
            return True, 'Вход выполнен успешно', user_data
        else:
            return False, 'Неверный пароль', None
        
    except DoesNotExist:
        return False, 'Пользователь с таким email не найден. Пожалуйста, зарегистрируйтесь.', None
    except OperationalError as e:
        return False, f"Ошибка подключения: {e}", None
    
def logout():
    try:
        if not db.is_closed():
            db.close()
        return True, 'Сеанс завершен. Соединение закрыто.', None
    except Exception as e:
        return False, f"Ошибка при выходе: {e}", None
    
def change_password(user_id, current_password, new_password, confirm_password):
    if not all([current_password, new_password, confirm_password]):
        return False, 'Заполните все поля', None
    if not (6 <= len(new_password) <= 32):
        return False, 'Пароль должен быть от 6 до 32 символов', None
    if not (re.search(r'[A-Z]', new_password) and re.search(r'[a-z]', new_password) and re.search(r'\d', new_password)):
        return False, 'Пароль должен содержать буквы разного регистра и цифры', None
    if new_password != confirm_password:
        return False, 'Пароли не совпадают', None
    if new_password == current_password:
        return False, 'Новый пароль не должен совпадать с текущим', None
    
    try:
        user = User.get_by_id(user_id)
        if not bcrypt.checkpw(current_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return False, 'Неверный текущий пароль', None
        
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password_hash = new_hash
        user.save()
        return True, 'Пароль успешно изменен', None
    except DoesNotExist:
        return False, 'Пользователь не найден', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def get_profile(user_id):
    try:
        if db.is_closed():
            db.connect()

        user = User.get_by_id(user_id)
        profile_data = {
            'id': user.id,
            'last_name': user.last_name,
            'first_name': user.first_name,
            'middle_name': user.middle_name or "",
            'role': user.role,
            'specialization': user.specialization,
            'photo_path': user.photo_path
        }

        if user.role == 'спортсмен':
            try:
                latest = ReadinessStatus.select().where(ReadinessStatus.athlete == user_id).order_by(ReadinessStatus.id.desc()).get()
                profile_data['current_status'] = latest.current_status
            except DoesNotExist:
                profile_data['current_status'] = 'Не установлен'

        return True, 'Данные профиля загружены', profile_data
    
    except DoesNotExist:
        return False, 'Профиль не найден', None
    except OperationalError as e:
        return False, f"Ошибка подключения к БД: {e}", None
                                                   
def edit_profile(user_id, last_name, first_name, middle_name, email, specialization, photo_path=None):
    if not all([last_name, first_name, email, specialization]):
        return False, 'Заполните все обязательные поля', None
    if not _is_valid_email(email):
        return False, 'Неверный формат email', None
    
    try:
        if db.is_closed():
            db.connect()
        
        user = User.get_by_id(user_id)

        if User.select().where((User.email == email) & (User.id != user_id)).exists():
            return False, 'Этот email уже занят другим пользователем', None
        
        with db.atomic():
            user.last_name = last_name
            user.first_name = first_name
            user.middle_name = middle_name or None
            user.email = email
            user.specialization = specialization
            if photo_path is not None:
                user.photo_path = photo_path
            user.save()

        return True, 'Профиль успешно обновлен', None
    except DoesNotExist:
        return False, 'Пользователь не найден', None
    except OperationalError as e:
        return False, f"Ошибка подключения к БД: {e}", None
    
def _get_current_week():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

def get_diary_entries(athlete_id, start_date=None, end_date=None, page=1, per_page=3, activity_type=None):
    try:
        if db.is_closed():
            db.connect()

        if start_date is None or end_date is None:
            start_date, end_date = _get_current_week()
        elif (end_date - start_date).days > 180:
            return False, 'Диапазон не должен превышать 6 месяцев', None
        
        conditions = [
            TrainingDiary.athlete == athlete_id,
            TrainingDiary.date >= start_date,
            TrainingDiary.date <= end_date,
            TrainingDiary.is_deleted == False
        ]

        if activity_type and activity_type.strip():
            conditions.append(TrainingDiary.activity_type == activity_type.strip())
        
        query = TrainingDiary.select().where(*conditions).order_by(TrainingDiary.date.desc())
        total_count = query.count()
        entries = list(query.paginate(page, per_page))

        return True, 'Дневник загружен', {
            'entries': entries,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'start_date': start_date,
            'end_date': end_date
        }
    except OperationalError as e:
        return False, f"Ошибка подключения к БД: {e}", None
    
def get_diary_entry_details(entry_id, athlete_id):
    try:
        entry = TrainingDiary.get_by_id(entry_id)

        if entry.athlete_id != athlete_id or entry.is_deleted:
            return False, 'Запись не найдена или доступ запрещен', None
        
        comments = Recommendation.select().where(
            (Recommendation.linked_entity == 'дневник нагрузок') &
            (Recommendation.linked_entity_id == entry_id)
        ).order_by(Recommendation.id.desc())

        return True, 'Данные загружены', {
            'entry': entry,
            'comments': list(comments)
        }
    except DoesNotExist:
        return False, 'Запись не найдена или доступ запрещен', None
    except OperationalError as e:
        return False, f"Ошибка подключения к БД: {e}", None
    
def add_diary_entry(athlete_id, entry_date, activity_type, duration, steps, sleep_hours, fatigue, mood, comment=None):
    if not all([entry_date, activity_type, duration, sleep_hours, fatigue, mood]):
        return False, 'Заполните все обязательные поля', None
    if not (1 <= duration <= 300):
        return False, 'Длительность занятия должна быть от 1 до 300 мин', None
    if steps < 0:
        return False, 'Количество шагов не может быть отрицательным числом', None
    if not (1 <= fatigue <= 10):
        return False, 'Усталость: шкала от 1 до 10', None
    if not (1 <= mood <= 10):
        return False, 'Настроение: шкала от 1 до 10', None
    if entry_date > date.today():
        return False, 'Дата не может быть в будущем', None
    
    clean_comment = comment.strip() if comment else None
    
    try:
        if db.is_closed():
            db.connect()

        existing = TrainingDiary.select().where(
            (TrainingDiary.athlete == athlete_id) &
            (TrainingDiary.date == entry_date) &
            (TrainingDiary.is_deleted == False)
        ).first()

        if existing:
            return False, f"Запись за {entry_date} уже существует. Отредактируйте ее.", {"existing_id": existing.id}
        
        with db.atomic():
            TrainingDiary.create(
                athlete = athlete_id,
                date = entry_date,
                activity_type = activity_type,
                duration = duration,
                steps = steps,
                sleep_hours = sleep_hours,
                fatigue = fatigue,
                mood = mood,
                comment = clean_comment
            )
        return True, 'Запись добавлена', None
    except OperationalError as e:
        return False, f"Ошибка подключения к БД: {e}", None
    
def edit_diary_entry(entry_id, athlete_id, entry_date, activity_type, duration, steps, sleep_hours, fatigue, mood, comment=None):
    if not all([entry_date, activity_type, duration, sleep_hours, fatigue, mood]):
        return False, 'Заполните все обязательные поля', None
    if not (1 <= duration <= 300):
        return False, 'Длительность занятия должна быть от 1 до 300 мин', None
    if steps < 0:
        return False, 'Количество шагов не может быть отрицательным числом', None
    if not (1 <= fatigue <= 10):
        return False, 'Усталость: шкала от 1 до 10', None
    if not (1 <= mood <= 10):
        return False, 'Настроение: шкала от 1 до 10', None
    if entry_date > date.today():
        return False, 'Дата не может быть в будущем', None
    
    clean_comment = comment.strip() if comment else None

    try:
        entry = TrainingDiary.get_by_id(entry_id)
        if entry.athlete_id != athlete_id:
            return False, 'Доступ запрещен', None
        
        critical_changed = (entry.date != entry_date) or (entry.activity_type != activity_type)

        with db.atomic():
                entry.date = entry_date
                entry.activity_type = activity_type
                entry.duration = duration
                entry.steps = steps
                entry.sleep_hours = sleep_hours
                entry.fatigue = fatigue
                entry.mood = mood
                entry.comment = clean_comment
                entry.save()

                if critical_changed:
                    Recommendation.delete().where(
                        (Recommendation.linked_entity == 'дневник нагрузок') &
                        (Recommendation.linked_entity_id == entry_id)
                    ).execute()
            
        return True, 'Изменения сохранены', {'needs_review': critical_changed}
    except DoesNotExist:
        return False, 'Запись не найдена', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def delete_diary_entry(entry_id, athlete_id):
    try:
        entry = TrainingDiary.get_by_id(entry_id)
        if entry.athlete_id != athlete_id:
            return False, 'Доступ запрещен', None
        
        with db.atomic():
            entry.is_deleted = True
            entry.save()
        return True, 'Запись удалена', None
    except DoesNotExist:
        return False, 'Запись не найдена', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def get_medical_data(athlete_id, exam_date=None, exam_type=None):
    try:
        if db.is_closed():
            db.connect()

        conditions = [MedicalExam.athlete == athlete_id]

        if exam_date:
            if exam_date > date.today():
                return False, 'Дата не может быть в будущем', None
            conditions.append(MedicalExam.exam_date == exam_date.strip())
        
        if exam_type and exam_type.strip():
            conditions.append(MedicalExam.exam_type == exam_type.strip())


        exams = MedicalExam.select().where(*conditions).order_by(MedicalExam.exam_date.desc())

        result = []
        for exam in exams:
            metrics = MedicalMetric.select().where(
                MedicalMetric.exam == exam
            ).order_by(MedicalMetric.id.desc())

            recommendations = Recommendation.select().where(
                (Recommendation.linked_entity == 'медкарта') &
                (Recommendation.linked_entity_id == exam.id)
            ).order_by(Recommendation.id.desc())

            doctor = exam.doctor
            doctor_fio = f"{doctor.last_name} {doctor.first_name} {doctor.middle_name or ''}".strip()

            result.append({ 
                'exam_date': exam.exam_date,
                'exam_type': exam.exam_type,
                'doctor_fio': doctor_fio,
                'doctor_email': doctor.email,
                'metrics': list(metrics),
                'recommendations': list(recommendations),
                'exam': exam
            })

        return True, 'Медицинские данные загружены', result
    except OperationalError as e:
        return False, f"Ошибка подключения: {e}", None
    
from datetime import datetime, date, timedelta
from peewee import fn, DoesNotExist, OperationalError
from db.models import Message, User, TrainingPlan, Session
from db.connection import db

def get_training_plan(athlete_id, start_date=None, end_date=None):
    try:
        if db.is_closed():
            db.connect()

        if start_date is None or end_date is None:
            start_date, end_date = _get_current_week()

        plans = TrainingPlan.select().where(
            (TrainingPlan.athlete == athlete_id) &
            (TrainingPlan.start_date <= end_date) &
            (TrainingPlan.end_date >= start_date) &
            (TrainingPlan.is_deleted == False)
        )

        result = []
        for plan in plans:
            sessions = Session.select().where(
                (Session.plan == plan) &
                (Session.is_deleted == False) &
                (Session.date >= start_date) &
                (Session.date <= end_date)
            ).order_by(Session.date.asc(), Session.time.asc())

            result.append({'plan': plan, 'sessions': list(sessions)})
        return True, 'План загружен', result
    except OperationalError as e:
        return False, f"Ошибка подключения: {e}", None
    
def sync_overdue_sessions(athlete_id):
    try:
        cutoff_date = date.today() - timedelta(days=1)
        overdue_ids = [
            s.id for s in Session.select().join(TrainingPlan).where(
                (TrainingPlan.athlete == athlete_id) &
                (Session.status == 'запланировано') &
                (Session.date < cutoff_date) &
                (Session.is_deleted == False)
            )
        ]
        if overdue_ids:
            Session.update(status='пропущено').where(Session.id << overdue_ids).execute()
            return True
        return False
    except OperationalError:
        return False

def update_session_status(session_id, athlete_id, new_status):
    valid_statuses = ['запланировано', 'выполнено', 'пропущено']
    if new_status not in valid_statuses:
        return False, 'Недопустимый статус', None
    
    try:
        session = Session.get_by_id(session_id)
        if session.plan.athlete_id != athlete_id:
            return False, 'Доступ запрещен', None
        
        today = date.today()
        if session.date < today - timedelta(days=1) and new_status != 'пропущено':
            return False, 'Изменение статуса доступно только в день занятия или в течение 24 часов после', None
        
        with db.atomic():
            session.status = new_status
            session.save()
        return True, 'Статус сохранен', None
    except DoesNotExist:
        return False, 'Занятие не найдено', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def get_chat_partners(current_user_id):
    try:
        if db.is_closed():
            db.connect()
    
        # 🔹 Оптимизировано: выбираем только ID, чтобы не грузить объекты User
        sent_ids = [m.receiver_id for m in Message.select(Message.receiver_id).where(Message.sender == current_user_id).distinct()]
        recv_ids = [m.sender_id for m in Message.select(Message.sender_id).where(Message.receiver == current_user_id).distinct()]
        partner_ids = list(set(sent_ids + recv_ids))

        if not partner_ids:
            return True, 'Список пуст', []
        
        partners = User.select().where(User.id << partner_ids).order_by(User.last_name)
        result = [{'id': p.id, 'full_name': f"{p.last_name} {p.first_name}".strip(), 'photo_path': p.photo_path} for p in partners]
        return True, 'Список загружен', result
    except OperationalError as e:
        return False, f"Ошибка подключения: {e}", None

def get_chat_partner_info(partner_id):
    try:
        if db.is_closed():
            db.connect()
        partner = User.get_by_id(partner_id)
        return True, 'Данные загружены', {
            'full_name': f"{partner.last_name} {partner.first_name} {partner.middle_name or ''}".strip(),
            'role': partner.role,
            'specialization': partner.specialization or "",  #  Защита от None
            'photo_path': partner.photo_path
        }    
    except DoesNotExist:
        return False, 'Собеседник не найден', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None

def get_chat_messages(current_user_id, partner_id, search_query=None, start_date=None, end_date=None):
    try:
        if db.is_closed():
            db.connect()

        conditions = [
            ((Message.sender == current_user_id) & (Message.receiver == partner_id)) |
            ((Message.sender == partner_id) & (Message.receiver == current_user_id))
        ]

        if start_date and end_date:
            if end_date < start_date:
                return False, 'Дата начала должна быть раньше даты окончания', None
            if start_date > date.today() or end_date > date.today():
                return False, 'Даты не могут быть в будущем', None
            conditions.append(Message.sent_at >= datetime.combine(start_date, datetime.min.time()))
            conditions.append(Message.sent_at <= datetime.combine(end_date, datetime.max.time()))

        if search_query and search_query.strip():
            clean_q = search_query.strip()
            if len(clean_q) < 3:
                return False, 'Поисковый запрос должен содержать минимум 3 символа', None
            conditions.append(fn.LOWER(Message.text).contains(clean_q.lower()))

        messages = (Message.select(Message, User)
            .join(User, on=(Message.sender == User.id))
            .where(*conditions)
            .order_by(Message.sent_at.asc()))
                
        result = []
        for msg in messages:
            is_mine = (msg.sender.id == current_user_id)
            result.append({
                'id': msg.id, 'text': msg.text, 'sent_at': msg.sent_at,
                'is_mine': is_mine, 'sender_name': 'Вы' if is_mine else f"{msg.sender.last_name} {msg.sender.first_name}"
            })
        return True, 'Сообщения загружены', result
    except OperationalError as e:
        return False, f"Ошибка подключения: {e}", None

def send_message(sender_id, receiver_id, text):
    clean_text = text.strip()
    if not clean_text:
        return False, 'Сообщение не может быть пустым', None
    if len(clean_text) > 500:
        return False, 'Сообщение не может превышать 500 символов', None

    try:
        with db.atomic():
            Message.create(sender=sender_id, receiver=receiver_id, text=clean_text, sent_at=datetime.now()) # 🔹 Исправлено sent_at
        return True, 'Сообщение отправлено', None
    except OperationalError as e:
        return False, f"Ошибка отправки: {e}", None   

def add_chat_partner(current_user_id, target_email):
    if not target_email or not target_email.strip():
        return False, 'Введите email собеседника', None
    clean_email = target_email.strip()
    
    try:
        if db.is_closed():
            db.connect()
        try:
            target_user = User.get(User.email == clean_email)
        except DoesNotExist:
            return False, 'Пользователь с таким email не найден', None

        if target_user.id == current_user_id:
            return False, 'Нельзя добавить самого себя в собеседники', None
        
        return True, 'Собеседник добавлен', {
            'id': target_user.id, 'full_name': f"{target_user.last_name} {target_user.first_name}".strip(),
            'photo_path': target_user.photo_path, 'role': target_user.role, 'specialization': target_user.specialization
        }
    except OperationalError as e:
        return False, f"Ошибка подключения к базе: {e}", None  

def delete_account(user_id):
    try:
        user = User.get_by_id(user_id)
        if hasattr(User, 'is_active'):
            user.is_active = False
        else:
            user.email = f"disabled_{user.id}@deleted.local"
        user.save()
        db.close()
        return True, 'Аккаунт деактивирован. Сессия завершена.', None
    except DoesNotExist:
        return False, 'Пользователь не найден', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None