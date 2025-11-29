# models.py
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.String(5), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    dept_name = db.Column(db.String(255))
    tot_cred = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Student {self.id} {self.name}>"
    
class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.String(8), primary_key=True)
    title = db.Column(db.String(50))
    dept_name = db.Column(db.String(20))
    credits = db.Column(db.Numeric(2,0))

class Section(db.Model):
    __tablename__ = 'section'
    course_id = db.Column(db.String(8), db.ForeignKey('course.course_id'), primary_key=True)
    sec_id = db.Column(db.String(8), primary_key=True)
    semester = db.Column(db.String(6), primary_key=True)
    year = db.Column(db.Numeric(4,0), primary_key=True)
    building = db.Column(db.String(15))
    room_number = db.Column(db.String(7))
    time_slot_id = db.Column(db.String(4))

class Classroom(db.Model):
    __tablename__ = 'classroom'
    building = db.Column(db.String(15), primary_key=True)
    room_number = db.Column(db.String(7), primary_key=True)
    capacity = db.Column(db.Numeric(4,0))

class Takes(db.Model):
    __tablename__ = 'takes'
    id = db.Column(db.String(5), db.ForeignKey('student.id'), primary_key=True)
    course_id = db.Column(db.String(8), db.ForeignKey('course.course_id'), primary_key=True)
    sec_id = db.Column(db.String(8), primary_key=True)
    semester = db.Column(db.String(6), primary_key=True)
    year = db.Column(db.Numeric(4,0), primary_key=True)
    grade = db.Column(db.String(2))
