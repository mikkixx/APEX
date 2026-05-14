from peewee import (
    Model, CharField, IntegerField, FloatField, DateField, TimeField, DateTimeField, BooleanField, TextField, ForeignKeyField  
)
from db.connection import db
from datetime import datetime

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    email = CharField(unique = True)
    password_hash = CharField()
    last_name = CharField()
    first_name = CharField()
    middle_name = CharField(null = True)
    role = CharField()
    specialization = CharField()
    photo_path = CharField(null = True)

    class Meta:
        table_name = 'users'

class SpecialistBinding(BaseModel):
    athlete = ForeignKeyField(User, backref='bindings_athlete', column_name='athlete_id')
    specialist = ForeignKeyField(User, backref='bindings_specialist', column_name='specialist_id')
    status = CharField(default='активна')
    is_deleted = BooleanField(default=False)

    class Meta:
        table_name = 'specialist_bindings'

class TrainingPlan(BaseModel):
    athlete = ForeignKeyField(User, backref='plans', column_name='athlete_id')
    coach = ForeignKeyField(User, backref='created_plans', column_name='coach_id')
    title = CharField()
    start_date = DateField()
    end_date = DateField()
    is_deleted = BooleanField(default=False)

    class Meta:
        table_name = 'training_plans'

class Session(BaseModel):
    plan = ForeignKeyField(TrainingPlan, backref='sessions', column_name='plan_id')
    date = DateField()
    time = TimeField(null = True)
    activity_type = CharField()
    duration = IntegerField()
    status = CharField(default='запланировано')
    is_deleted = BooleanField(default=False)

    class Meta:
        table_name = 'sessions'

class TrainingDiary(BaseModel):
    athlete = ForeignKeyField(User, backref='diary', column_name='athlete_id')
    date = DateField()
    activity_type = CharField()
    duration = IntegerField()
    steps = IntegerField()
    sleep_hours = FloatField()
    fatigue = IntegerField()
    mood = IntegerField()
    comment = TextField(null = True)
    is_deleted = BooleanField(default=False)

    class Meta:
        table_name = 'training_diary'

class MedicalExam(BaseModel):
    athlete = ForeignKeyField(User, backref='medical_exams', column_name='athlete_id')
    doctor = ForeignKeyField(User, backref='conducted_exams', column_name='doctor_id')
    exam_date = DateField()
    exam_type = CharField()

    class Meta:
        table_name = 'medical_exams'

class MedicalMetric(BaseModel):
    exam = ForeignKeyField(MedicalExam, backref='metrics', column_name='exam_id')
    metric_type = CharField()
    value = FloatField()
    unit = CharField()
    ref_range = CharField()
    is_critical = BooleanField(default=False)

    class Meta:
        table_name = 'medical_metrics'

class Recommendation(BaseModel):
    author = ForeignKeyField(User, backref='recommendations_given', column_name='author_id')
    athlete = ForeignKeyField(User, backref='recommendations_received', column_name='athlete_id')
    linked_entity = CharField()
    linked_entity_id = IntegerField()
    text = TextField()

    class Meta:
        table_name = 'recommendations'

class Message(BaseModel):
    sender = ForeignKeyField(User, backref='sent_messages', column_name='sender_id')
    receiver = ForeignKeyField(User, backref='received_messages', column_name='receiver_id')
    text = TextField()
    sent_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'messages'

class ReadinessStatus(BaseModel):
    athlete = ForeignKeyField(User, backref='readiness_history', column_name='athlete_id')
    current_status = CharField()
    initiator = ForeignKeyField(User, backref='status_changes_made', column_name='initiator_id')
    lock_status = CharField(default='свободно')

    class Meta:
        table_name = 'readiness_status'

if __name__ == "__main__":
    print("Создание таблиц в базе данных...")
    db.create_tables([
        User, SpecialistBinding, TrainingPlan, Session, TrainingDiary, MedicalExam, MedicalMetric, Recommendation, Message, ReadinessStatus
    ], safe = True)
    print("Таблицы созданы")