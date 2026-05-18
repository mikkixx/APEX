import re
import bcrypt
from peewee import fn, DoesNotExist, IntegrityError, OperationalError
from datetime import date, timedelta, datetime
from db.models import User, ReadinessStatus, TrainingDiary, Recommendation, MedicalExam, MedicalMetric, TrainingPlan, Session, Message, SpecialistBinding
from db.connection import db
import os

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

        formatted_comments = []
        for comment in comments:
            author = User.get_by_id(comment.author_id)
            formatted_comments.append({
                'text': comment.text,
                'author_fio': f"{author.last_name} {author.first_name} {author.middle_name or ''}".strip(),
                'author_role': author.role
            })

        return True, 'Данные загружены', {
            'entry': entry,
            'comments': formatted_comments 
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
            conditions.append(MedicalExam.exam_date == exam_date)
        
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
                'metrics': [
                    {
                        'type': m.metric_type,
                        'value': m.value,
                        'unit': m.unit,
                        'is_critical': m.is_critical  
                    } 
                    for m in metrics
                ],
                'recommendations': list(recommendations),
                'exam': exam
            })

        return True, 'Медицинские данные загружены', result
    except OperationalError as e:
        return False, f"Ошибка подключения: {e}", None
    
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
            'specialization': partner.specialization, 
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
    

def get_my_athletes(specialist_id, page=1, per_page=5, search=None, sport_type=None, status=None):
    try:
        if db.is_closed():
            db.connect()

        # 1. Получаем ID спортсменов, привязанных к специалисту
        binding_ids = list(
            SpecialistBinding.select(SpecialistBinding.athlete)
            .where(
                (SpecialistBinding.specialist == specialist_id) &
                (SpecialistBinding.status == 'активна') &
                (SpecialistBinding.is_deleted == False)
            ).tuples()
        )
        athlete_ids = [row[0] for row in binding_ids]

        if not athlete_ids:
            return True, 'Список пуст', {'athletes': [], 'total': 0, 'page': page, 'per_page': per_page}

        # 2. Базовый запрос к таблице пользователей
        query = User.select().where(User.id << athlete_ids)

        # 3. Фильтр поиска (по ФИО)
        if search and len(search.strip()) >= 3:
            q = search.strip().lower()
            query = query.where(
                (fn.LOWER(User.last_name).contains(q)) |
                (fn.LOWER(User.first_name).contains(q)) |
                (fn.LOWER(User.middle_name).contains(q))
            )

        # 4. Фильтр по виду спорта
        if sport_type and sport_type.strip():
            query = query.where(fn.LOWER(User.specialization).contains(sport_type.strip().lower()))

        # 5. Фильтр по статусу готовности (применяем ДО пагинации!)
        if status and status.strip():
            status_val = status.strip()
            valid_ids = []
            for aid in athlete_ids:
                try:
                    s = ReadinessStatus.select().where(ReadinessStatus.athlete == aid).order_by(ReadinessStatus.id.desc()).get()
                    if s.current_status == status_val:
                        valid_ids.append(aid)
                except DoesNotExist:
                    pass
            query = query.where(User.id << valid_ids)

        # 6. Считаем общее количество ПОСЛЕ всех фильтров, но ДО пагинации
        total = query.count()

        # 7. Сортировка и пагинация
        users = list(query.order_by(User.last_name.asc()).paginate(page, per_page))

        result = []
        for athlete in users:
            try:
                latest_status = ReadinessStatus.select().where(
                    ReadinessStatus.athlete == athlete.id
                ).order_by(ReadinessStatus.id.desc()).get()
                current_status = latest_status.current_status
            except DoesNotExist:
                current_status = 'Не установлен'

            result.append({
                'id': athlete.id,
                'last_name': athlete.last_name,
                'first_name': athlete.first_name,
                'middle_name': athlete.middle_name or '',
                'specialization': athlete.specialization,
                'current_status': current_status,
                'email': athlete.email,
                'photo_path': athlete.photo_path
            })

        return True, 'Список загружен', {
            'athletes': result,
            'total': total,
            'page': page,
            'per_page': per_page
        }

    except OperationalError as e:
        return False, f"Ошибка подключения к БД: {e}", None
    except Exception as e:
        return False, f"Неожиданная ошибка: {e}", None
    
def add_athlete_by_email(specialist_id, athlete_email):
    if not athlete_email or not athlete_email.strip():
        return False, 'Введите email спортсмена', None

    clean_email = athlete_email.strip()
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', clean_email):
        return False, 'Неверный формат email', None

    try:
        if db.is_closed():
            db.connect()

        athlete = User.get(User.email == clean_email)
        if athlete.role != 'спортсмен':
            return False, 'Пользователь не является спортсменом', None

        specialist = User.get_by_id(specialist_id)
        specialist_role = specialist.role

        already_bound = SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete.id) &
            (SpecialistBinding.specialist == specialist_id) &
            (SpecialistBinding.status == 'активна') &
            (SpecialistBinding.is_deleted == False)
        ).exists()
        if already_bound:
            return False, 'Этот спортсмен уже закреплён за вами', None

        bound_ids = [b.specialist_id for b in SpecialistBinding.select(SpecialistBinding.specialist_id).where(
            (SpecialistBinding.athlete == athlete.id) &
            (SpecialistBinding.status == 'активна') &
            (SpecialistBinding.is_deleted == False)
        )]

        if bound_ids:
            existing_roles = set(u.role for u in User.select(User.role).where(User.id << bound_ids))

            if specialist_role == 'тренер' and 'тренер' in existing_roles:
                return False, 'У спортсмена уже есть активный тренер', None
            if specialist_role == 'врач' and 'врач' in existing_roles:
                return False, 'У спортсмена уже есть активный врач', None

        with db.atomic():
            SpecialistBinding.create(
                athlete=athlete.id,
                specialist=specialist_id,
                status='активна',
                is_deleted=False
            )

        return True, 'Спортсмен успешно добавлен', {
            'id': athlete.id,
            'full_name': f"{athlete.last_name} {athlete.first_name}".strip(),
            'email': athlete.email
        }

    except DoesNotExist:
        return False, 'Пользователь с таким email не найден', None
    except IntegrityError:
        return False, 'Ошибка целостности данных', None
    except OperationalError as e:
        return False, f"Ошибка подключения к БД: {e}", None
    
def get_athlete_profile_full(specialist_id, athlete_id):
    try:
        if db.is_closed():
            db.connect()

        binding = SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == specialist_id) &
            (SpecialistBinding.status == 'активна') &
            (SpecialistBinding.is_deleted == False)
        ).exists()

        if not binding:
            return False, 'Спортсмен не закреплён за вами', None

        athlete = User.get_by_id(athlete_id)
        try:
            last_status_rec = ReadinessStatus.select().where(
                ReadinessStatus.athlete == athlete_id
            ).order_by(ReadinessStatus.id.desc()).get()
            
            current_status = last_status_rec.current_status
            lock_status = last_status_rec.lock_status
        except DoesNotExist:
            current_status = 'Не установлен'
            lock_status = 'свободно'

        return True, 'Данные загружены', {
            'id': athlete.id,
            'full_name': f"{athlete.last_name} {athlete.first_name} {athlete.middle_name or ''}".strip(),
            'photo_path': athlete.photo_path,
            'role': athlete.role,
            'specialization': athlete.specialization,
            'email': athlete.email,
            'current_status': current_status,
            'lock_status': lock_status 
        }

    except DoesNotExist:
        return False, 'Спортсмен не найден', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None

def get_athlete_sessions(specialist_id, athlete_id, start_date=None, end_date=None, page=1, per_page=3):
    try:
        if db.is_closed():
            db.connect()

        if not SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == specialist_id) &
            (SpecialistBinding.status == 'активна') &
            (SpecialistBinding.is_deleted == False)
        ).exists():
            return False, 'Спортсмен не закреплён за вами', None

        if start_date is None or end_date is None:
            today = date.today()
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif (end_date - start_date).days > 90:
            return False, 'Диапазон не должен превышать 3 месяца', None

        query = (Session
            .select(Session, TrainingPlan)
            .join(TrainingPlan, on=(Session.plan == TrainingPlan.id))
            .where(
                (TrainingPlan.athlete == athlete_id) &
                (Session.date >= start_date) &
                (Session.date <= end_date) &
                (Session.is_deleted == False) &
                (TrainingPlan.is_deleted == False)
            )
            .order_by(Session.date.desc(), Session.time.desc()))

        total = query.count()
        sessions = list(query.paginate(page, per_page))

        result = []
        for s in sessions:
            plan_header = f"{s.plan.title} ({s.plan.start_date.strftime('%d.%m.%Y')} - {s.plan.end_date.strftime('%d.%m.%Y')})"
            
            result.append({
                'id': s.id,
                'plan_header': plan_header, 
                'date': s.date,
                'time': s.time,
                'activity_type': s.activity_type,
                'duration': s.duration,
                'status': s.status
            })

        return True, 'План загружен', {
            'sessions': result,
            'total': total,
            'page': page,
            'per_page': per_page
        }
    except OperationalError as e:
        return False, f"Ошибка подключения к БД: {e}", None
       
def create_training_plan(specialist_id, athlete_id, start_date, end_date, title='Новый план'):
    try:
        if db.is_closed():
            db.connect()

        if not SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == specialist_id) &
            (SpecialistBinding.status == 'активна')
        ).exists():
            return False, 'Нет прав на создание плана для этого спортсмена', None

        if start_date < date.today():
            return False, 'Дата начала не может быть в прошлом', None
        if end_date <= start_date:
            return False, 'Дата окончания должна быть позже даты начала', None

        with db.atomic():
            plan = TrainingPlan.create(
                athlete=athlete_id,
                coach=specialist_id,
                title=title,
                start_date=start_date,
                end_date=end_date,
                is_deleted=False
            )
        return True, 'План создан', {'plan_id': plan.id}
    except IntegrityError as e:
        return False, 'Ошибка целостности данных', None
    except OperationalError as e:
        return False, f"Ошибка подключения: {e}", None
    
def edit_session(specialist_id, session_id, date, time, activity_type, duration):
    if duration <= 0:
        return False, 'Длительность должна быть больше 0', None

    try:
        if db.is_closed():
            db.connect()

        session = Session.get_by_id(session_id)
        
        if session.plan.coach_id != specialist_id:
            return False, 'Доступ запрещён', None

        if session.status in ['выполнено', 'пропущено']:
            return False, 'Занятие выполнено. Редактирование невозможно', None

        with db.atomic():
            session.date = date
            session.time = time
            session.activity_type = activity_type
            session.duration = duration
            session.save()
            
        return True, 'Занятие изменено', None
    except DoesNotExist:
        return False, 'Занятие не найдено', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def delete_training_plan(specialist_id, plan_id):
    try:
        if db.is_closed():
            db.connect()

        plan = TrainingPlan.get_by_id(plan_id)
        if plan.coach_id != specialist_id:
            return False, 'Доступ запрещён', None

        if plan.end_date <= date.today():
            return False, 'Удаление доступно только до окончания периода плана', None

        with db.atomic():
            plan.is_deleted = True
            plan.save()
            
            Session.update(is_deleted=True).where(
                (Session.plan == plan_id) &
                (Session.is_deleted == False)
            ).execute()
            
        return True, 'План удалён', None
    except DoesNotExist:
        return False, 'План не найден', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def add_recommendation_to_session(specialist_id, session_id, text):
    clean_text = text.strip()
    if not clean_text:
        return False, 'Текст рекомендации не может быть пустым', None
    if len(clean_text) > 500:
        return False, 'Текст не должен превышать 500 символов', None

    try:
        if db.is_closed():
            db.connect()

        session = Session.get_by_id(session_id)
        if session.plan.coach_id != specialist_id:
            return False, 'Доступ запрещён', None
        if session.status != 'выполнено':
            return False, 'Рекомендацию можно оставить только к выполненному занятию', None

        existing = Recommendation.select().where(
            (Recommendation.author == specialist_id) &
            (Recommendation.athlete == session.plan.athlete_id) &
            (Recommendation.linked_entity == 'тренировочное занятие') &
            (Recommendation.linked_entity_id == session_id)
        ).first()

        if existing:
            return False, 'Рекомендация уже существует.', None

        with db.atomic():
            Recommendation.create(
                author=specialist_id,
                athlete=session.plan.athlete_id,
                linked_entity_type='тренировочное занятие',
                linked_entity_id=session_id,
                text=clean_text
            )
        return True, 'Рекомендация сохранена', None
    except DoesNotExist:
        return False, 'Занятие не найдено', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def get_athlete_medical_data_for_coach(specialist_id, athlete_id, exam_date=None, exam_type=None):
    try:
        if db.is_closed():
            db.connect()

        if not SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == specialist_id) &
            (SpecialistBinding.status == 'активна') &
            (SpecialistBinding.is_deleted == False)
        ).exists():
            return False, 'Спортсмен не закреплён за вами', None

        conditions = [MedicalExam.athlete == athlete_id]

        if exam_date:
            if exam_date > date.today():
                return False, 'Дата не может быть в будущем', None
            conditions.append(MedicalExam.exam_date == exam_date)  
        
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
    
def update_athlete_status(specialist_id, athlete_id, new_status):
    valid_statuses = ['здоров', 'устал', 'болен'] #
    if new_status not in valid_statuses:
        return False, 'Недопустимый статус', None

    try:
        if db.is_closed():
            db.connect()

        if not SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == specialist_id) &
            (SpecialistBinding.status == 'активна')
        ).exists():
            return False, 'Спортсмен не закреплён за вами', None

        specialist = User.get_by_id(specialist_id)
        specialist_role = specialist.role

        try:
            last_status = ReadinessStatus.select().where(
                ReadinessStatus.athlete == athlete_id
            ).order_by(ReadinessStatus.id.desc()).get()

            if last_status.lock_status == 'заблокировано':
                initiator = last_status.initiator
                if initiator.role == 'врач' and specialist_role == 'тренер':
                    return False, 'Статус заблокирован врачом. Действие отменено.', None
        except DoesNotExist:
            pass 

        with db.atomic():

            lock_status = 'заблокировано' if specialist_role == 'врач' else 'свободно'
            
            ReadinessStatus.create(
                athlete=athlete_id,
                initiator=specialist_id,
                current_status=new_status,
                lock_status=lock_status  
            )
            
        return True, 'Статус обновлён', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def delete_session(specialist_id, session_id):
    try:
        if db.is_closed():
            db.connect()

        session = Session.get_by_id(session_id)
        
        if session.plan.coach_id != specialist_id:
            return False, 'Доступ запрещён', None

        if session.date < date.today():
            return False, 'Удаление возможно только до начала даты занятия', None

        if session.status == 'выполнено':
            return False, 'Нельзя удалить выполненное занятие', None

        with db.atomic():
            session.is_deleted = True
            session.save()
        return True, 'Занятие удалено', None
    except DoesNotExist:
        return False, 'Занятие не найдено', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def get_session_details(specialist_id, session_id):
    try:
        if db.is_closed():
            db.connect()

        session = Session.get_by_id(session_id)
        
        if session.plan.coach_id != specialist_id:
            return False, 'Доступ запрещён', None

        return True, 'Данные загружены', {
            'id': session.id,
            'plan_id': session.plan.id,
            'plan_title': session.plan.title,
            'date': session.date,
            'time': session.time,
            'activity_type': session.activity_type,
            'duration': session.duration,
            'status': session.status
        }
    except DoesNotExist:
        return False, 'Занятие не найдено', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def add_session(specialist_id, plan_id, session_date, session_time, activity_type, duration):
    if duration <= 0:
        return False, 'Длительность должна быть больше 0', None
    if session_date < date.today():
        return False, 'Дата не может быть в прошлом', None

    try:
        if db.is_closed():
            db.connect()

        plan = TrainingPlan.get_by_id(plan_id)
        if plan.coach_id != specialist_id:
            return False, 'Доступ запрещён', None

        conflict = Session.select().where(
            (Session.plan == plan_id) &
            (Session.date == session_date) &
            (Session.time == session_time) &
            (Session.is_deleted == False)
        ).exists()

        if conflict:
            return False, 'На это время уже запланировано другое занятие', None

        with db.atomic():
            Session.create(
                plan=plan_id,
                date=session_date,
                time=session_time,
                activity_type=activity_type,
                duration=duration,
                status='запланировано',
                is_deleted=False
            )
            
        return True, 'Занятие создано', None
    except DoesNotExist:
        return False, 'План не найден', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def get_athlete_diary(specialist_id, athlete_id, start_date=None, end_date=None, page=1, per_page=10):
    try:
        if db.is_closed():
            db.connect()

        if not SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == specialist_id) &
            (SpecialistBinding.status == 'активна')
        ).exists():
            return False, 'Спортсмен не закреплён за вами', None

        if start_date is None or end_date is None:
            today = date.today()
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        conditions = [
            (TrainingDiary.athlete == athlete_id),
            (TrainingDiary.is_deleted == False)
        ]

        if start_date and end_date:
            conditions.append((TrainingDiary.date >= start_date) & (TrainingDiary.date <= end_date))
        
        query = TrainingDiary.select().where(*conditions).order_by(TrainingDiary.date.desc())
        total = query.count()
        entries = list(query.paginate(page, per_page))

        result = [{
            'id': e.id, 'date': e.date, 'activity_type': e.activity_type,
            'duration': e.duration, 'steps': e.steps, 'sleep_hours': e.sleep_hours,
            'fatigue': e.fatigue, 'mood': e.mood
        } for e in entries]

        return True, 'Дневник загружен', {
            'entries': result, 'total': total, 'page': page, 'per_page': per_page
        }
    except OperationalError as e:
        return False, f"Ошибка подключения: {e}", None
    
def add_diary_recommendation(specialist_id, entry_id, text):
    clean_text = text.strip()
    if not clean_text:
        return False, 'Текст не может быть пустым', None
    if len(clean_text) > 500:
        return False, 'Текст не должен превышать 500 символов', None

    try:
        if db.is_closed():
            db.connect()

        entry = TrainingDiary.get_by_id(entry_id)
        
        if not SpecialistBinding.select().where(
            (SpecialistBinding.athlete == entry.athlete_id) &
            (SpecialistBinding.specialist == specialist_id) &
            (SpecialistBinding.status == 'активна')
        ).exists():
            return False, 'Спортсмен не закреплён за вами', None

        with db.atomic():
            Recommendation.create(
                author=specialist_id,
                athlete=entry.athlete_id,
                linked_entity_type='дневник нагрузок',
                linked_entity_id=entry_id,
                text=clean_text
            )
            
        return True, 'Рекомендация сохранена', None
    except DoesNotExist:
        return False, 'Запись дневника не найдена', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def get_athlete_plan_for_doctor(doctor_id, athlete_id, start_date=None, end_date=None):
    try:
        if db.is_closed():
            db.connect()

        if not SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == doctor_id) &
            (SpecialistBinding.status == 'активна') &
            (SpecialistBinding.is_deleted == False)
        ).exists():
            return False, 'Спортсмен не закреплён за вами', None

        conditions = [
            (TrainingPlan.athlete == athlete_id),
            (TrainingPlan.is_deleted == False)
        ]

        if start_date and end_date:
            conditions.append((TrainingPlan.start_date <= end_date) & (TrainingPlan.end_date >= start_date))

        plans = TrainingPlan.select().where(*conditions).order_by(TrainingPlan.start_date.desc())

        result = []
        for plan in plans:
            sessions = Session.select().where(
                (Session.plan == plan) &
                (Session.is_deleted == False)
            ).order_by(Session.date.asc(), Session.time.asc())

            result.append({
                'plan_id': plan.id,
                'title': plan.title,
                'start_date': plan.start_date,
                'end_date': plan.end_date,
                'sessions': [{
                    'id': s.id,
                    'date': s.date,
                    'time': s.time,
                    'activity_type': s.activity_type,
                    'duration': s.duration,
                    'status': s.status
                } for s in sessions]
            })

        return True, 'План загружен', result
    except OperationalError as e:
        return False, f"Ошибка подключения: {e}", None
    
def get_athlete_medical_records(doctor_id, athlete_id):
    try:
        if db.is_closed():
            db.connect()

        if not SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == doctor_id) &
            (SpecialistBinding.status == 'активна')
        ).exists():
            return False, 'Спортсмен не закреплён за вами', None

        exams = MedicalExam.select().where(
            MedicalExam.athlete == athlete_id
        ).order_by(MedicalExam.exam_date.desc())

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
                'exam_id': exam.id,
                'exam_date': exam.exam_date,
                'exam_type': exam.exam_type,
                'doctor_fio': doctor_fio,
                'doctor_email': doctor.email,
                'metrics': [{
                    'id': m.id,
                    'type': m.metric_type,
                    'value': m.value,
                    'unit': m.unit,
                    'is_critical': m.is_critical
                } for m in metrics],
                'recommendations': [{
                    'id': r.id,
                    'text': r.text,
                    'created_at': r.created_at
                } for r in recommendations]
            })

        return True, 'Медицинские данные загружены', result
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def create_medical_exam(doctor_id, athlete_id, exam_date, exam_type):
    if not exam_type or not exam_type.strip():
        return False, 'Укажите тип осмотра', None
    if exam_date > date.today():
        return False, 'Дата не может быть в будущем', None

    try:
        if db.is_closed():
            db.connect()

        if not SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == doctor_id) &
            (SpecialistBinding.status == 'активна')
        ).exists():
            return False, 'Спортсмен не закреплён за вами', None

        existing = MedicalExam.select().where(
            (MedicalExam.athlete == athlete_id) &
            (MedicalExam.exam_date == exam_date) &
            (MedicalExam.exam_type == exam_type.strip())
        ).exists()

        if existing:
            return False, 'Осмотр этого типа уже существует за указанную дату', None

        with db.atomic():
            exam = MedicalExam.create(
                athlete=athlete_id,
                doctor=doctor_id,
                exam_date=exam_date,
                exam_type=exam_type.strip(),
                is_deleted=False
            )

            base_metrics = [
                ('Пульс', 'уд/мин'),
                ('Давление (систолическое)', 'мм рт.ст.'),
                ('Давление (диастолическое)', 'мм рт.ст.'),
                ('Вес', 'кг'),
                ('Рост', 'см')
            ]

            for metric_type, unit in base_metrics:
                MedicalMetric.create(
                    exam=exam.id,
                    metric_type=metric_type,
                    value=0.0,  
                    unit=unit,
                    ref_range='', 
                    is_critical=False
                )

        return True, 'Карточка осмотра создана', {'exam_id': exam.id}
    except IntegrityError:
        return False, 'Ошибка целостности данных', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def add_medical_metric(exam_id, doctor_id, metric_type, value, unit, ref_min=None, ref_max=None):
    try:
        if db.is_closed():
            db.connect()

        exam = MedicalExam.get_by_id(exam_id)
        
        if exam.doctor_id != doctor_id:
            return False, 'Доступ запрещён', None

        is_critical = False
        if value is not None and ref_min is not None and ref_max is not None:
            try:
                val = float(value)
                if val < ref_min or val > ref_max:
                    is_critical = True
            except (ValueError, TypeError):
                pass

        with db.atomic():
            metric, created = MedicalMetric.get_or_create(
                exam=exam_id,
                metric_type=metric_type,
                defaults={
                    'value': value,
                    'unit': unit,
                    'is_critical': is_critical
                }
            )

            if not created:
                metric.value = value
                metric.unit = unit
                metric.is_critical = is_critical
                metric.save()

        return True, 'Показатель сохранён', {'is_critical': is_critical}
    except DoesNotExist:
        return False, 'Осмотр не найден', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def add_medical_recommendation(doctor_id, exam_id, text):
    clean_text = text.strip()
    if not clean_text:
        return False, 'Текст рекомендации не может быть пустым', None
    if len(clean_text) > 500:
        return False, 'Текст не должен превышать 500 символов', None

    try:
        if db.is_closed():
            db.connect()

        exam = MedicalExam.get_by_id(exam_id)
        
        if exam.doctor_id != doctor_id:
            return False, 'Доступ запрещён', None

        with db.atomic():
            Recommendation.create(
                author=doctor_id,
                athlete=exam.athlete_id,
                linked_entity='медкарта',
                linked_entity_id=exam_id,
                text=clean_text
            )

        return True, 'Рекомендация подписана', None
    except DoesNotExist:
        return False, 'Осмотр не найден', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def generate_report(specialist_id, athlete_id, report_type, start_date, end_date, format='excel'):
    try:
        if db.is_closed():
            db.connect()

        if not SpecialistBinding.select().where(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == specialist_id) &
            (SpecialistBinding.status == 'активна')
        ).exists():
            return False, 'Спортсмен не закреплён за вами', None

        os.makedirs('./reports', exist_ok=True)
        filename = f"./reports/report_{athlete_id}_{date.today().strftime('%Y%m%d')}.{format}"

        sessions_data = []
        exams = []
        
        if report_type == 'training':
            plans = TrainingPlan.select().where(
                (TrainingPlan.athlete == athlete_id) &
                (TrainingPlan.start_date >= start_date) &
                (TrainingPlan.end_date <= end_date)
            )
            for plan in plans:
                sessions = Session.select().where(
                    (Session.plan == plan) & (Session.is_deleted == False)
                )
                for s in sessions:
                    sessions_data.append({
                        'date': str(s.date),
                        'activity': s.activity_type,
                        'duration': s.duration,
                        'status': s.status
                    })
                    
        elif report_type == 'medical':
            exams = MedicalExam.select().where(
                (MedicalExam.athlete == athlete_id) &
                (MedicalExam.exam_date >= start_date) &
                (MedicalExam.exam_date <= end_date)
            )
        else:
            return False, 'Неподдерживаемый тип отчёта. Доступно: training, medical', None

        if format == 'excel':
            try:
                from openpyxl import Workbook
                wb = Workbook()
                ws = wb.active
                ws.title = 'Тренировки' if report_type == 'training' else 'Медосмотры'
                
                if report_type == 'training':
                    ws.append(['Дата', 'Активность', 'Длительность (мин)', 'Статус'])
                    for row in sessions_data:
                        ws.append([row['date'], row['activity'], row['duration'], row['status']])
                else:
                    ws.append(['Дата', 'Тип осмотра', 'Показатель', 'Значение', 'Ед.изм.', 'Критично'])
                    for exam in exams:
                        metrics = MedicalMetric.select().where(MedicalMetric.exam == exam)
                        for m in metrics:
                            ws.append([
                                str(exam.exam_date), exam.exam_type, m.metric_type,
                                str(m.value) if m.value is not None else '', m.unit,
                                'Да' if m.is_critical else 'Нет'
                            ])
                wb.save(filename)
            except ImportError:
                return False, 'Установите openpyxl: pip install openpyxl', None

        elif format == 'pdf':
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                import os as os_sys

                font_path = "C:\\Windows\\Fonts\\arial.ttf"
                if os_sys.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Arial', font_path))
                    font_name = 'Arial'
                else:
                    font_name = 'Helvetica'  

                doc = SimpleDocTemplate(filename, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()
                
                # Заголовок
                title_style = styles['Heading1']
                title_style.fontName = font_name
                title = Paragraph(f"Отчёт: {report_type.capitalize()}", title_style)
                elements.append(title)
                elements.append(Spacer(10, 10))

                table_data = []
                if report_type == 'training':
                    headers = ['Дата', 'Активность', 'Длительность (мин)', 'Статус']
                    table_data = [headers] + [[s['date'], s['activity'], str(s['duration']), s['status']] for s in sessions_data]
                else:
                    headers = ['Дата', 'Тип осмотра', 'Показатель', 'Значение', 'Ед.изм.', 'Критично']
                    table_data = [headers]
                    for exam in exams:
                        metrics = MedicalMetric.select().where(MedicalMetric.exam == exam)
                        for m in metrics:
                            table_data.append([
                                str(exam.exam_date), exam.exam_type, m.metric_type,
                                str(m.value) if m.value is not None else '', m.unit,
                                'Да' if m.is_critical else 'Нет'
                            ])

                col_widths = [doc.width / len(headers)] * len(headers)
                table = Table(table_data, colWidths=col_widths)
                table.setStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), font_name),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('FONTNAME', (0, 1), (-1, -1), font_name),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ])
                elements.append(table)
                doc.build(elements)
                
            except ImportError:
                return False, 'Установите reportlab: pip install reportlab', None
            except Exception as pdf_err:
                return False, f'Ошибка генерации PDF: {pdf_err}', None
        else:
            return False, 'Неподдерживаемый формат. Используйте excel или pdf', None

        return True, f"Отчёт сохранён: {filename}", {'path': filename}

    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    except Exception as e:
        return False, f"Ошибка генерации: {e}", None
    
def remove_athlete_from_list(specialist_id, athlete_id):
    try:
        if db.is_closed():
            db.connect()

        binding = SpecialistBinding.get(
            (SpecialistBinding.athlete == athlete_id) &
            (SpecialistBinding.specialist == specialist_id) &
            (SpecialistBinding.is_deleted == False)
        )

        with db.atomic():
            binding.status = 'прекращена'
            binding.is_deleted = True
            binding.save()

        return True, 'Спортсмен исключён из списка', None
    except DoesNotExist:
        return False, 'Привязка не найдена', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def get_session_recommendations(session_id):
    try:
        recommendations = Recommendation.select().where(
            (Recommendation.linked_entity == 'тренировочное занятие') &
            (Recommendation.linked_entity_id == session_id)
        ).order_by(Recommendation.id.desc())
        
        result = []
        for rec in recommendations:
            author = User.get_by_id(rec.author_id)
            result.append({
                'text': rec.text,
                'author_fio': f"{author.last_name} {author.first_name}".strip(),
                'author_role': author.role
            })
        
        return True, 'Рекомендации загружены', result
    except DoesNotExist:
        return False, 'Занятие не найдено', None
    except OperationalError as e:
        return False, f"Ошибка БД: {e}", None
    
def get_recommendations_for_entry(entry_id):
    try:
        recs = Recommendation.select().where(
            (Recommendation.linked_entity == 'дневник нагрузок') &
            (Recommendation.linked_entity_id == entry_id)
        ).order_by(Recommendation.id.desc())
        
        result = []
        for rec in recs:
            author = User.get_by_id(rec.author_id)
            result.append({
                'text': rec.text,
                'author_fio': f"{author.last_name} {author.first_name}".strip(),
                'author_role': author.role
            })
        return True, 'Загружены', result
    except Exception as e:
        return False, str(e), None
    
def get_activity_types(athlete_id: int):
    try:
        from db.connection import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT activity_type 
            FROM diary_entries 
            WHERE athlete_id = ? AND activity_type IS NOT NULL
            ORDER BY activity_type
        """, (athlete_id,))
        types = [row[0] for row in cursor.fetchall()]
        return True, "OK", types
    except Exception as e:
        return False, str(e), []

def get_diary_entries(athlete_id, start_date=None, end_date=None, page=1, per_page=3, activity_type=None):
    try:
        
        query = TrainingDiary.select().where(
            (TrainingDiary.athlete_id == athlete_id) &
            (TrainingDiary.is_deleted == False)
        )

        if start_date is not None:
            query = query.where(TrainingDiary.date >= start_date)
        if end_date is not None:
            query = query.where(TrainingDiary.date <= end_date)
        if activity_type is not None and activity_type.strip() != "":
            query = query.where(TrainingDiary.activity_type == activity_type)

        # Сортировка: новые записи сверху
        query = query.order_by(TrainingDiary.date.desc())

        # Пагинация
        total = query.count()
        offset = (page - 1) * per_page
        entries = list(query.limit(per_page).offset(offset))

        return True, "OK", {"entries": entries, "total": total}
    except Exception as e:
        print(f"Ошибка get_diary_entries: {e}")
        return False, str(e), {"entries": [], "total": 0}
    
def get_examination_types(athlete_id):
    try:
        query = (
            MedicalExam
            .select(MedicalExam.exam_type)
            .where(MedicalExam.athlete_id == athlete_id)
            .distinct()
            .order_by(MedicalExam.exam_type)
        )
        
        types = [exam.exam_type for exam in query]
        
        return True, "OK", types
    except Exception as e:
        print(f"Ошибка загрузки типов осмотров: {e}")
        return False, str(e), []