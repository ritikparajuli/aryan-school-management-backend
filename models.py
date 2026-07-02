# models.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Time
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    full_name = Column(String(255), nullable=False)

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    employee_id = Column(String(50), unique=True)
    department = Column(String(100))
    phone = Column(String(20))
    profile_pic = Column(Text)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    roll_no = Column(String(50), unique=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    date_of_birth = Column(Date)
    phone = Column(String(20))
    parent_phone = Column(String(20))
    address = Column(Text)
    profile_pic = Column(Text)

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    section = Column(String(10))
    academic_year = Column(String(20))

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    credits = Column(Integer, default=1)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    date = Column(Date, nullable=False)
    status = Column(String(10), nullable=False)
    marked_by = Column(Integer, ForeignKey("teachers.id"))

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_url = Column(Text, nullable=False)
    total_marks = Column(Integer)
    due_date = Column(Date)
    uploaded_by = Column(Integer, ForeignKey("teachers.id"))

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_url = Column(Text, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("teachers.id"))

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    exam_type = Column(String(50), nullable=False)
    marks_obtained = Column(Float, nullable=False)
    total_marks = Column(Float, nullable=False)
    grade = Column(String(2))
    percentage = Column(Float)

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_date = Column(Date, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    event_type = Column(String(50))
    created_by = Column(Integer, ForeignKey("users.id"))