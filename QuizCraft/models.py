# this module should consist of all the database models/schema which I have defined
from . import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(50), unique = True, nullable = False)
    role = db.Column(db.String(10), nullable = False)
    password_hash = db.Column(db.String(256), nullable = False)
    dob = db.Column(db.DateTime, nullable = True, default = None)
    qualification = db.Column(db.String(50), nullable = True, default = 'undergraduate')
    rank = db.Column(db.String(30), nullable = True, default = 'Apprentince Thinker')
    profile_picture = db.Column(db.String(128), nullable = True)
    userCreationDate = db.Column(db.DateTime(timezone = True), nullable = True, server_default = func.now())
    flag = db.Column(db.Boolean, default = False)

    # a user can take part in many quizzes so it is only logical that they can have multiple results 
    quiz_results = db.relationship('QuizResult', backref = 'user', cascade = 'all, delete-orphan', lazy = True)



class Subject(db.Model):
    subject_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(128), nullable = False, unique = True)
    description = db.Column(db.Text, nullable  = False) # --> --> --> -->
    subject_image = db.Column(db.String(256), nullable = True)

    # each subject can have multiple chapters
    chapters = db.relationship('Chapter', backref = 'subject', cascade = 'all, delete-orphan', lazy = True)



class Chapter(db.Model):
    chapter_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(128), nullable = False, unique = True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'), nullable = False)
    description = db.Column(db.Text) # --> --> --> -->

    # a chapter can have many quizzes
    quizzes = db.relationship('Quiz', backref = 'chapter', cascade = 'all, delete-orphan', lazy = True)



class Quiz(db.Model):
    quiz_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(50), nullable = False, unique = True)
    # since a quiz is for chapters, so this is logical
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.chapter_id'), nullable = False)
    marking_scheme_pos = db.Column(db.Integer, nullable = False)
    marking_scheme_neg = db.Column(db.Integer, nullable = False)
    time_duration = db.Column(db.Time, nullable = False)
    deadline = db.Column(db.DateTime, nullable = True)

    # well a quiz can have many questions and many results --> (attempted by different users)
    questions = db.relationship('Question', backref = 'quiz', cascade = 'all, delete-orphan' ,lazy = True)
    quizResults = db.relationship('QuizResult', backref = 'quiz', cascade = 'all, delete-orphan', lazy = True)
 


class Question(db.Model):
    question_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable = False)
    statement = db.Column(db.Text, nullable = False) # --> --> --> -->

    # q question can have many options (max 4 and one correct only)
    options = db.relationship('Option', backref = 'question', cascade = 'all, delete-orphan' ,lazy = True)



class Option(db.Model):
   option_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
   question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'), nullable = False)
   text = db.Column(db.Text, nullable = False) # --> --> --> -->
   is_correct = db.Column(db.Boolean, default = False)



class UserAnswer(db.Model):
    userAnswer_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    result_id = db.Column(db.Integer, db.ForeignKey('quiz_result.quizResult_id'), nullable = False) 
    question_id = db.Column(db.Integer, db.ForeignKey('question.question_id'), nullable = False)
    selectedOption_id = db.Column(db.Integer, db.ForeignKey('option.option_id'), nullable = True)
    isCorrect = db.Column(db.Boolean, default = False)

    questions = db.relationship('Question', backref = 'user_answer', single_parent = True, lazy = True)
    options = db.relationship('Option', backref = 'user_answer', single_parent = True, lazy = True)


class QuizResult(db.Model):
    quizResult_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    attempt_no = db.Column(db.Integer, default = 1)
    # trying this timezone = True and func.now() --> func calls the now() function in SQL to set the time
    # by the server instead of the application
    attempt_started_at = db.Column(db.DateTime(), nullable = False)
    # will keep a track of this manually and then calculate the time taken
    attempt_ended_at = db.Column(db.DateTime, nullable = True)
    marks_scored = db.Column(db.Integer, default = 0, nullable = False)
    total_marks = db.Column(db.Integer, default = 0, nullable = False)
    quiz_status = db.Column(db.String(28), default = 'ongoing', nullable = False)

    # quiz result can have multuple users' answers
    user_answers = db.relationship('UserAnswer', backref = 'quiz_result', cascade = 'all, delete-orphan', lazy = True)

