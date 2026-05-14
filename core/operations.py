import re
import bcrypt
from peewee import DoesNotExist, IntegrityError, OperationalError
from datetime import date, timedelta


from db.models import User, ReadinessStatus, TrainingDiary, Recommendation
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

def get_diary_entries(athlete_id, start_date=None, end_date=None, page=1, per_page=3):
    try:
        if db.is_closed():
            db.connect()

        if start_date is None or end_date is None:
            start_date, end_date = _get_current_week()
        elif (end_date - start_date).days > 180:
            return False, 'Диапазон не должен превышать 6 месяцев', None
        
        query = TrainingDiary.select().where(
            (TrainingDiary.athlete == athlete_id) &
            (TrainingDiary.date >= start_date) &
            (TrainingDiary.date <= end_date) &
            (TrainingDiary.is_deleted == False)
        ).order_by(TrainingDiary.date.desc())

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