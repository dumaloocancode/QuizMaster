from flask import redirect, url_for, render_template
from flask import session, request, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask import current_app as app
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from datetime import datetime, time
import pytz
import os
from .models import *
from . import db

# --------------- SETTING UP THE LOGIN MANAGER, AUTH AND DATETIME ------------------
loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login' # this is the route handler where the app will redirect to if the user is not logged in

# this decorator allows us to get the user who is currently logged in
@loginManager.user_loader
def loadUser(user_id):
    return User.query.get(int(user_id))

# this decorator helps us validate a user based on their role to have access to the site
def role_required(role):
    def innieDecorator(f):
        @wraps(f)
        def decoratedFunction(*args, **kwargs):
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)

        return decoratedFunction

    return innieDecorator

IST = pytz.timezone('Asia/Kolkata')

# ----------------------- SETTING UP THE ADMIN ------------------------
admin = User(name = 'admin', email = 'admin@gmail.com', role = 'admin',
             password_hash = generate_password_hash('admin1234'))
user = User.query.filter_by(email = 'admin@gmail.com').first()
if not user:
    db.session.add(admin)
    db.session.commit()

# ------------------ ENTRY POINT OF THE APPLICATION ! ---------------------
@app.route('/')
def main():
    return render_template('index.html')


# ------------  SIGNUP ROUTE ! ---------------
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        # get all the form attributes and validate
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        dob = request.form.get('dob')
        dob = datetime.strptime(dob, '%Y-%m-%dT%H:%M')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')

        # query the database to see if the user exists or not
        user = User.query.filter_by(email = email).first()

        if user:
            flash('Email already exists! Please login', category = 'error')
            redirect(url_for('login'))
        elif not username:
            flash('Name cannot be empty!', category = 'error')
        elif len(email) < 3:
            flash('Email must be greater than 3 characters', category = 'error')
        elif role == "pleaseSelect":
            flash('please select a valid role', category = 'error')
        elif len(password) < 8:
            flash('password must be at least 8 characters', category = 'error')
        elif password != confirmPassword:
            flash('passwords do not match!', category = 'error')
        else:
            new_user = User(
                name = username,
                email = email,
                password_hash = generate_password_hash(password),
                dob = dob,
                role = role
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', category = 'success')
            return redirect(url_for('login'))
        
    return render_template('signUp.html')

# ------------ LOGIN ROUTE ! ----------------
@app.route('/login', methods=['POST', 'GET']) 
def login():

    userName = request.form.get('username') 
    userPassword = request.form.get('password')
    userRole = request.form.get('role') 

    if request.method == 'POST':
        user = User.query.filter_by(name = userName).first()
        if user:
            if user.role == userRole:
                if check_password_hash(user.password_hash, userPassword):
                    login_user(user)
                    flash('Logged in Successfully!', category = 'success')
                    if user.role == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    elif user.role == 'user':
                        return redirect(url_for('user_dashboard'))
                else:
                    flash('Wrong password. Try again!', category = 'error')
            else:
                flash('Incorrect role selected! Please try again', category = 'error')
        else:
            flash('User does not exist! Redirected to sign-up page', category = 'error')
            return redirect(url_for('signup'))

    return render_template('login.html')


# -------------- LOGOUT ROUTE ! -----------------
@app.route('/logout', methods = ['GET'])
@login_required
def logout():
    role = current_user.role
    logout_user()
    if role == 'user':
        flash('Logged out! Time to reflect on all those wrong answers.. or just log back in!', category = 'success')
    else:
        flash('Might wanna come back soon to add more quizzes!', category = 'success')
    return redirect(url_for('login'))


# ------------- ADMIN DASHBOARD ROUTE ! ---------------
@app.route('/admin/dashboard', methods=['GET', 'POST'])
@role_required('admin')
@login_required
def admin_dashboard():
    subject = Subject.query.all()

    return render_template('adminDashboard.html', userName = current_user.name,subject = subject)


# ------------- ADMIN CREATE SUBJECT ROUTE ! ---------------
@app.route('/admin/subject/create', methods=['GET', 'POST'])
@role_required('admin')
@login_required
def create_subject():

    if request.method == 'POST':
        subjectImage = request.files['subjectImage']
        subjectName = request.form.get('subjectName')
        subjectDescription = request.form.get('subjectDescription')

        if subjectImage:
            imageFile = secure_filename(subjectImage.filename)
            savePath = os.path.join(app.config['UPLOAD_FOLDER'], imageFile)
            db_path = os.path.join('uploads', imageFile).replace('\\', '/')
            subjectImage.save(savePath)
        else:
            db_path = None

        subject = Subject.query.filter_by(name = subjectName).first()

        if subject:
            flash('Subject already exists!', category = 'error')
            return redirect(url_for('create_subject'))
        else:
            new_subject = Subject(
                name = subjectName,
                description = subjectDescription,
                subject_image = db_path)
            
            db.session.add(new_subject)
            db.session.commit()
            flash('New Subject added successfully!', category = 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('adminCreateSubject.html', userName = current_user.name)


# ------------- ADMIN SHOW SUBJECT ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>')
@role_required('admin')
@login_required
def show_subject(subjectID):
    subject = Subject.query.filter_by(subject_id = subjectID).first()
    # subject_chapters = subject.chapters
    if not subject:
        flash('Subject Does not exist!', category = 'error')
        return redirect(url_for('admin_dashboard'))

    return render_template('adminShowSubject.html', userName = current_user.name, subject = subject)


# ------------- ADMIN EDIT SUBJECT ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>/edit', methods = ['POST', 'GET'])
@role_required('admin')
@login_required
def edit_subject(subjectID):

    subject = Subject.query.filter_by(subject_id = subjectID).first()

    if not subject:
        flash('Subject Does not exist!', category = 'error')
        return redirect(url_for('show_subject'), userName = current_user.name)

    if request.method == 'POST':
        changedName = request.form.get('subjectName')
        changedDescription = request.form.get('subjectDescription')
        changedPhoto = request.files['subjectImage']
        changedPhotoFileName = secure_filename(changedPhoto.filename)
        
        if changedName:
            subject.name = changedName
        
        if changedDescription:
            subject.description = changedDescription
        
        if changedPhoto:
            savePath = os.path.join(app.config['UPLOAD_FOLDER'], changedPhotoFileName)
            db_path = os.path.join('uploads', changedPhotoFileName).replace('\\', '/')
            changedPhoto.save(savePath)
            subject.subject_image = db_path
        
        db.session.commit()
        flash(f'Edited {subject.name} succesfully!', category = 'success')
        return redirect(url_for('show_subject', subjectID = subject.subject_id))

    
    return render_template('adminEditSubject.html', userName = current_user.name)



# ------------- ADMIN DELETE SUBJECT ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>/delete', methods = ['POST', 'GET'])
@role_required('admin')
@login_required
def delete_subject(subjectID):

    subject = Subject.query.filter_by(subject_id = subjectID).first()

    if subject:
        subjectName = subject.name
        db.session.delete(subject)
        db.session.commit()
        flash(f'Deleted {subjectName} successfully!', category = 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('No such subject exists!', category = 'error')


# ------------- ADMIN CREATE CHAPTER ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>/chapter/create', methods = ['POST', 'GET'])
@role_required('admin')
@login_required
def create_chapter(subjectID):

    subject = Subject.query.filter_by(subject_id = subjectID).first()
    
    if not subject:
        flash('Subject does not exist!', category = 'error')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        chapterName = request.form.get('chapterName')
        chapterDescription = request.form.get('chapterDescription')

        if chapterName != '' and chapterDescription != '':
            new_chapter = Chapter(name = chapterName,
                                  description = chapterDescription, 
                                  subject = subject)
            db.session.add(new_chapter)
            db.session.commit()
            flash('Created a new chapter successfully!', category = 'success')
            return redirect(url_for('show_subject', subjectID = subject.subject_id))
            
    return render_template('adminCreateChapter.html', userName = current_user.name)


# ------------- ADMIN EDIT CHAPTER ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>/chapter/<int:chapterID>/edit', methods = ['POST', 'GET'])
@role_required('admin')
@login_required
def edit_chapter(subjectID, chapterID):

    subject = Subject.query.filter_by(subject_id = subjectID).first()
    chapter = Chapter.query.filter_by(chapter_id = chapterID).first()

    if not subject:
        flash('Subject does not exist!', category = 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not chapter:
        flash('Chapter does not exist!', category = 'error')
        return redirect(url_for('show_subject', subjectID = subject.subject_id))

    if request.method == 'POST':
        prevChapName = chapter.name
        changedChapterName = request.form.get('chapterName')
        changedChapterDescription = request.form.get('chapterDescription')

        if changedChapterName:
            chapter.name = changedChapterName
        
        if changedChapterDescription:
            chapter.description = changedChapterDescription
        
        db.session.commit()
        flash(f'Edited {prevChapName} successfully!', category = 'success')
        return redirect(url_for('show_subject', subjectID = subject.subject_id))

    return render_template('adminEditChapter.html', userName = current_user.name, chapter = chapter)

# ------------- ADMIN DELETE CHAPTER ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>/chapter/<int:chapterID>/delete', methods = ['POST', 'GET'])
@role_required('admin')
@login_required
def delete_chapter(subjectID, chapterID):

    subject = Subject.query.filter_by(subject_id = subjectID).first()
    chapter = Chapter.query.filter_by(chapter_id = chapterID).first()

    if not subject:
        flash('Subject does not exist!', category = 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not chapter:
        flash('Chapter does not exist!', category = 'error')
        return redirect(url_for('show_subject', subjectID = subject.subject_id))

    if chapter:
        chapterName = chapter.name
        db.session.delete(chapter)
        db.session.commit()
        flash(f'Deleted {chapterName} successfully!', category = 'success')
        return redirect(url_for('show_subject', subjectID = subject.subject_id))
    

# ------------- ADMIN SHOW CHAPTER ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>/chapter/<int:chapterID>', methods = ['POST', 'GET'])
@role_required('admin')
@login_required
def show_chapter(subjectID, chapterID):
    subject = Subject.query.filter_by(subject_id = subjectID).first()
    chapter = Chapter.query.filter_by(chapter_id = chapterID).first()

    if not subject:
        flash('Subject does not exist!', category = 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not chapter:
        flash('Chapter does not exist!', category = 'error')
        return redirect(url_for('show_subject', subjectID = subject.subject_id))
    

    return render_template('adminShowChapter.html', userName = current_user.name, chapter = chapter, subject = subject)


# ------------- ADMIN CREATE QUIZ ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>/chapter/<int:chapterID>/quiz/add', methods = ['POST', 'GET'])
@role_required('admin')
@login_required
def create_quiz(subjectID, chapterID):
    chapter = Chapter.query.filter_by(chapter_id = chapterID).first()
    subject = Subject.query.filter_by(subject_id = subjectID).first()

    if not subject:
        flash('Subject does not exist!', category = 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not chapter:
        flash('Chapter does not exist!', category = 'error')
        return redirect(url_for('show_subject', subjectID = subject.subject_id))
    
    if request.method == 'POST':

        quizName = request.form.get('quizName')
        markingSchemePos = request.form.get('markingSchemePos')
        markingSchemeNeg = request.form.get('markingSchemeNeg')
        timeDuration = request.form.get('timeDuration')
        timeDurationList = timeDuration.split(':')  # Split "HH:MM" into hours and minutes
        time_duration = time(hour = int(timeDurationList[0]), minute = int(timeDurationList[1]))
        deadline = request.form.get('deadline')

        if quizName == '':
            flash('Quiz name cannot be empty!', category = 'error')
            return(redirect(url_for('create_quiz', subjectID = subject.subject_id, chapterID = chapter.chapter_id)))
        
        if timeDuration == '':
            flash('Time duration cannot be empty!', category = 'error')
            return(redirect(url_for('create_quiz', subjectID = subject.subject_id, chapterID = chapter.chapter_id)))
        
        if markingSchemeNeg > markingSchemePos:
            flash('Marking scheme for negative cannot be greater than positive', category = 'error')
            return(redirect(url_for('create_quiz', subjectID = subject.subject_id, chapterID = chapter.chapter_id)))
        
        if deadline:
            new_quiz = Quiz(name = quizName,
                        chapter = chapter,
                        marking_scheme_pos = markingSchemePos, 
                        marking_scheme_neg = markingSchemeNeg, 
                        time_duration = time_duration,
                        deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M'))
        else:
            new_quiz = Quiz(name = quizName,
                        chapter = chapter,
                        marking_scheme_pos = markingSchemePos, 
                        marking_scheme_neg = markingSchemeNeg, 
                        time_duration = time_duration)
            
        db.session.add(new_quiz)
        db.session.commit()
        quiz = Quiz.query.filter_by(name = quizName).first()
        flash('Quiz Created successfully!', category = 'success')
        return redirect(url_for('add_questions', subjectID = subject.subject_id, chapterID = chapter.chapter_id, quizID = quiz.quiz_id))

    return render_template('adminCreateQuiz.html', userName = current_user.name)



# ------------- ADMIN ADD QUESTIONS ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>/chapter/<int:chapterID>/quiz/<int:quizID>/add/question', methods = ['POST', 'GET'])
@role_required('admin')
@login_required
def add_questions(subjectID, chapterID, quizID):

    chapter = Chapter.query.filter_by(chapter_id = chapterID).first()
    subject = Subject.query.filter_by(subject_id = subjectID).first()
    quiz = Quiz.query.filter_by(quiz_id = quizID).first()

    if not subject:
        flash('Subject does not exist!', category = 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not chapter:
        flash('Chapter does not exist!', category = 'error')
        return redirect(url_for('show_subject', subjectID = subject.subject_id))

    if not quiz:
        flash('No quiz found for this chapter!', category='error')
        return redirect(url_for('show_chapter', subjectID=subject.subject_id, chapterID=chapter.chapter_id))

    if request.method == 'POST':
        
        questionStatement = request.form.get('question')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correctOption = request.form.get('correctOption')

        new_question = Question(quiz = quiz, statement = questionStatement)
        db.session.add(new_question)
        db.session.flush()

        optionsList = [
        {"text": option1, "is_correct": correctOption == "1"},
        {"text": option2, "is_correct": correctOption == "2"},
        {"text": option3, "is_correct": correctOption == "3"},
        {"text": option4, "is_correct": correctOption == "4"}
        ]

        for options in optionsList:
            new_option = Option(question_id=new_question.question_id, text=options["text"], is_correct=options["is_correct"])
            db.session.add(new_option)
        
        db.session.commit()
        flash('Question added successfully!', category = 'success')

        return redirect(url_for('add_questions', subjectID=subject.subject_id, chapterID=chapter.chapter_id, quizID = quiz.quiz_id))
        
        

    return render_template('adminAddQuestions.html', userName = current_user.name, subject = subject, chapter = chapter, quiz = quiz)


# ------------- ADMIN EDIT QUIZ ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>/chapter/<int:chapterID>/quiz/<int:quizID>/edit', methods = ['POST', 'GET'])
@role_required('admin')
@login_required
def edit_quiz(subjectID, chapterID, quizID):

    chapter = Chapter.query.filter_by(chapter_id = chapterID).first()
    subject = Subject.query.filter_by(subject_id = subjectID).first()
    quiz = Quiz.query.filter_by(quiz_id = quizID).first()

    if not subject:
        flash('Subject does not exist!', category = 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not chapter:
        flash('Chapter does not exist!', category = 'error')
        return redirect(url_for('show_subject', subjectID = subject.subject_id))

    if not quiz:
        flash('No quiz found for this chapter!', category='error')
        return redirect(url_for('show_chapter', subjectID=subject.subject_id, chapterID=chapter.chapter_id))
    
    if request.method == 'POST':

        quizName = request.form.get('quizName')
        marking_scheme_pos = request.form.get('markingSchemePos')
        marking_scheme_neg = request.form.get('markingSchemeNeg')
        time_duration = request.form.get('timeDuration')
        deadline = request.form.get('deadline')
        
        if quizName:
            quiz.name = quizName
        if marking_scheme_pos:
            quiz.marking_scheme_pos = marking_scheme_pos
        if marking_scheme_neg:
            quiz.marking_scheme_neg = marking_scheme_neg
        if time_duration:
            timeDurationList = time_duration.split(':')
            timeDurationActual = time(hour = int(timeDurationList[0]), minute = int(timeDurationList[1]))
            quiz.time_duration = timeDurationActual
        if deadline:
            quiz.deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M')
        
        for question in quiz.questions:
            questionID = f'question_{question.question_id}'
            newQuestionStatement = request.form.get(questionID)
            
            if newQuestionStatement:
                question.statement = newQuestionStatement
            
            for option in question.options:

                optionID = f'option_{option.option_id}'
                newOptionText = request.form.get(optionID)
                
                if newOptionText:
                    option.text = newOptionText
        

            correctOptionID = request.form.get(f'correctOption_{question.question_id}')
            if correctOptionID:
                for option in question.options:
                    option.is_correct = (str(option.option_id) == correctOptionID)
        
        db.session.commit()
        flash('Quiz updated successfully!', category='success')
        return redirect(url_for('show_chapter', subjectID=subjectID, chapterID=chapterID))

    return render_template('adminEditQuiz.html', userName = current_user.name, subject = subject, chapter = chapter, quiz = quiz)


# ------------- ADMIN DELETE QUIZ ROUTE ! ---------------
@app.route('/admin/Subject/<int:subjectID>/chapter/<int:chapterID>/quiz/<int:quizID>/delete', methods = ['POST', 'GET'])
@role_required('admin')
@login_required
def delete_quiz(subjectID, chapterID, quizID):

    chapter = Chapter.query.filter_by(chapter_id = chapterID).first()
    subject = Subject.query.filter_by(subject_id = subjectID).first()
    quiz = Quiz.query.filter_by(quiz_id = quizID).first()
    
    if quiz:
        quizName = quiz.name

    if not subject:
        flash('Subject does not exist!', category = 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not chapter:
        flash('Chapter does not exist!', category = 'error')
        return redirect(url_for('show_subject', subjectID = subject.subject_id))
    
    if not quiz:
        flash('No quiz found for this chapter!', category='error')
        return redirect(url_for('show_chapter', subjectID = subject.subject_id, chapterID = chapter.chapter_id))

    db.session.delete(quiz)
    db.session.commit()
    flash(f'{quizName} deleted successfully!', category = 'success')

    return redirect(url_for('show_chapter', subjectID = subject.subject_id, chapterID = chapter.chapter_id))


# ------------- ADMIN USER DETAILS ROUTE ! ---------------
@app.route('/admin/users')
@role_required('admin')
@login_required
def admin_users():

    users = User.query.all()
    users = users[1:]
    totalUsers = len(users)
    
    return render_template('adminUsers.html', userName = current_user.name, totalUsers = totalUsers, users = users)


# ------------- ADMIN USER DETAILS ROUTE ! ---------------
@app.route('/admin/users/<int:userID>')
@role_required('admin')
@login_required
def admin_user_details(userID):

    user = User.query.filter_by(id = userID).first()

    if not user:
        flash('user does not exist!', category = 'error')
        return redirect(url_for('admin_summary'))

    return render_template('adminUserDetail.html', userName = current_user.name, user = user)


# ------------- ADMIN USER RESULT DETAILS ROUTE ! ---------------
@app.route('/admin/user/<int:userID>/quiz/<int:quizID>/result/<int:resultID>', methods = ['POST', 'GET'])
@role_required('admin')
@login_required    
def admin_user_result(userID, quizID, resultID):

    user = User.query.filter_by(id = userID).first()
    result = QuizResult.query.filter_by(quizResult_id = resultID).first()
    quiz = Quiz.query.filter_by(quiz_id = quizID).first()

    if not user:
        flash('user does not exist!', category = 'error')
        return redirect(url_for('admin_user_details', userID = user.id))
    
    if not quiz:
        flash('no such quiz exists!', category = 'error')
        return redirect(url_for('admin_user_details', userID = user.id))

    
    if not result:
        flash('no such result exists for this quiz!', category = 'error')
        return redirect(url_for('admin_user_details', userID = user.id))
    
    
    return render_template('userQuizResult.html', userName = current_user.name, result = result)


# ------------- ADMIN DELETE USER ROUTE ! ---------------
@app.route('/admin/users/delete/<int:userID>')
@role_required('admin')
@login_required
def admin_delete_user(userID):

    user = User.query.filter_by(id = userID).first()

    if not user:
        flash('no user exists!', category = 'error')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', category = 'success')


# ------------- ADMIN SUMMARY ROUTE ! ---------------
@app.route('/admin/summary')
@role_required('admin')
@login_required
def admin_summary():
   
    stats = {
        'totalUsers': User.query.count() - 1,
        'totalSubjects': Subject.query.count(),
        'totalChapters': Chapter.query.count(),
        'totalQuizzes': Quiz.query.count()
    }
    
    subjects = Subject.query.all()
    subject_data = []
    
    for subject in subjects:
        
        chapters = Chapter.query.filter_by(subject_id=subject.subject_id).all()
        chapter_ids = [chapter.chapter_id for chapter in chapters]
        
        quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
        quiz_ids = [quiz.quiz_id for quiz in quizzes]
        
        quiz_results = QuizResult.query.filter(QuizResult.quiz_id.in_(quiz_ids)).all()
        
        total_score_percentage = 0
        for result in quiz_results:
            if result.total_marks > 0:  
                score_percentage = (result.marks_scored / result.total_marks) * 100
                total_score_percentage += score_percentage
        
        avg_score = total_score_percentage / len(quiz_results) if quiz_results else 0
        
        subject_data.append({'subject': subject.name, 'averageScore': round(avg_score, 2), 
                             'attemptCount': len(quiz_results)})
    
    chapter_data = []
    chapters = Chapter.query.all()
    
    for chapter in chapters:

        quizzes = Quiz.query.filter_by(chapter_id=chapter.chapter_id).all()
        quiz_ids = [quiz.quiz_id for quiz in quizzes]
        
        if quiz_ids:  
            results = QuizResult.query.filter(QuizResult.quiz_id.in_(quiz_ids)).all()
            
            if results:  
                total_score_percentage = 0
                for result in results:
                    if result.total_marks > 0:  
                        score_percentage = (result.marks_scored / result.total_marks) * 100
                        total_score_percentage += score_percentage
                
                avg_score = total_score_percentage / len(results)
                
                chapter_data.append({
                    'chapter': f"{chapter.subject.name}: {chapter.name}",
                    'averageScore': round(avg_score, 2),
                    'attemptCount': len(results)
                })
    
    return render_template('adminSummaryChart.html', userName = current_user.name, stats = stats, subject_data = subject_data, chapter_data = chapter_data)


# --------------- SEOMTHING NEW : TO PASS FUNCTIONS IN JINJA -----------------
@app.context_processor
def deltaDate():

    def convertDeltaDate(delta):

        totalSeconds = abs(delta.total_seconds())

        hours = int(totalSeconds // 3600)
        minutes = int((totalSeconds % 3600) // 60)
        seconds = int(totalSeconds % 60)

        return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    
    return dict(convertDeltaDate = convertDeltaDate)  


# ------------- USER DASHBOARD ROUTE ! ---------------
@app.route('/dashboard/user', methods=['POST', 'GET'])
@role_required('user')
@login_required
def user_dashboard():

    result = current_user.quiz_results


    if current_user.flag == False:
        current_user.flag = True
        db.session.commit()
        return(redirect(url_for('complete_profile', userID = current_user.id)))
        
    return render_template('userDashboard.html', userName = current_user.name, user = current_user, result = result)


# ------------- USER COMPLETE PROFILE ROUTE ! ---------------
@app.route('/user/<int:userID>/profile', methods=['POST', 'GET'])
@role_required('user')
@login_required
def complete_profile(userID):

    if request.method == 'POST':
    
        userImage = request.files['userImage']
        userQualification = request.form.get('userQualification')
        userImageFileName = secure_filename(userImage.filename)
        
        if userImage:
            savePath = os.path.join(app.config['UPLOAD_FOLDER'], userImageFileName)
            db_path = os.path.join('uploads', userImageFileName).replace('\\', '/')
            userImage.save(savePath)
            current_user.profile_picture = db_path

        if userQualification:
            current_user.qualification = userQualification
        
        db.session.commit()
        flash('Profile completed!', category='success')
        return redirect(url_for('user_dashboard'))

    return render_template('userCompleteProfile.html', userName = current_user.name, user = current_user)


# ------------- USER EDIT PROFILE ROUTE ! ---------------
@app.route('/user/<int:userID>/profile/edit', methods=['POST', 'GET'])
@role_required('user')
@login_required
def edit_profile(userID):

    if request.method == 'POST':
    
        userUpdatedImage = request.files['userImage']
        userUpdatedQualification = request.form.get('userQualification')
        userUpdatedEmail = request.form.get('userEmail')
        userImageFileName = secure_filename(userUpdatedImage.filename)
        userUpdatedPassword = request.form.get('userPassword')
        userConfirmPassword = request.form.get('userConfirmPassword')
        
        if userUpdatedImage:
            savePath = os.path.join(app.config['UPLOAD_FOLDER'], userImageFileName)
            db_path = os.path.join('uploads', userImageFileName).replace('\\', '/')
            userUpdatedImage.save(savePath)
            current_user.profile_picture = db_path

        if userUpdatedQualification:
            current_user.qualification = userUpdatedQualification

        if userUpdatedEmail:
            current_user.email = userUpdatedEmail
        
        if userUpdatedPassword:

            if not userConfirmPassword:
                flash('Confirm Password field cannot be empty!', category = 'error')
                return redirect(url_for('edit_profile', userID = current_user.id))
            
            if userUpdatedPassword != userConfirmPassword:
                flash('Passwords do not match!', category = 'error')
                return redirect(url_for('edit_profile', userID = current_user.id))
            else:
                current_user.password = generate_password_hash(userUpdatedPassword)
        
        db.session.commit()
        flash('Profile updated successfully!', category='success')
        return redirect(url_for('user_dashboard'))

    return render_template('userEditProfile.html', userName = current_user.name, user = current_user)

# ------------- USER DISPLAY SUBJECT ROUTE ! ---------------
@app.route('/user/subjects', methods=['POST', 'GET'])
@role_required('user')
@login_required
def display_subjects():

    subject = Subject.query.all()

    return render_template('userDisplaySubjects.html', userName = current_user.name, user = current_user, subject = subject)


# ------------- USER SHOW SUBJECT ROUTE ! ---------------
@app.route('/user/<int:userID>/subject/<int:subjectID>', methods=['POST', 'GET'])
@role_required('user')
@login_required
def show_user_subject(userID, subjectID):

    
    subject = Subject.query.filter_by(subject_id = subjectID).first()
    

    return render_template('userShowSubjects.html', userName = current_user.name, user = current_user, subject = subject)


# ------------- USER SHOW CHAPTER ROUTE ! ---------------
@app.route('/user/<int:userID>/subject/<int:subjectID>/chapter/<int:chapterID>', methods=['POST', 'GET'])
@role_required('user')
@login_required
def show_user_chapter(userID, subjectID, chapterID):

    subject = Subject.query.filter_by(subject_id = subjectID).first()
    chapter = Chapter.query.filter_by(chapter_id = chapterID).first()


    return render_template('userShowChapter.html', userName = current_user.name, subject = subject, user = current_user, chapter = chapter)



# ------------- USER ATTEMPT QUIZ ROUTE ! ---------------
@app.route('/user/<int:userID>/subject/<int:subjectID>/chapter/<int:chapterID>/quiz/<int:quizID>/attempt', methods=['POST', 'GET'])
@role_required('user')
@login_required
def attempt_quiz(userID, subjectID, chapterID, quizID):
    
    quiz = Quiz.query.filter_by(quiz_id = quizID).first()
    user = User.query.filter_by(id = userID).first()

    if not user:
        flash('user does not exist!', category = 'error')
        return redirect(url_for('user_dashboard'))

    prevRank = user.rank

    existingAttempt = QuizResult.query.filter_by(quiz_id = quizID, user_id = current_user.id, quiz_status = 'ongoing').first()
    
    if existingAttempt:
        quiz_result = existingAttempt
    else:
        attempt_count = QuizResult.query.filter_by(quiz_id = quizID, user_id = current_user.id).count()
        
        quiz_result = QuizResult(quiz = quiz, user = current_user, attempt_no = attempt_count + 1,
                                 total_marks = len(quiz.questions) * quiz.marking_scheme_pos,
                                 attempt_started_at = datetime.now(IST))
        db.session.add(quiz_result)
        db.session.commit()
    
    if request.method == 'POST':
        # yaha submitting answers
        for question in quiz.questions:

            selectedOptionID = request.form.get(f'question_{question.question_id}')
            
            if selectedOptionID:
                selectedOption = Option.query.get(selectedOptionID)
                is_correct = selectedOption.is_correct if selectedOption else False
            
                existingAnswer = UserAnswer.query.filter_by(result_id = quiz_result.quizResult_id, question_id = question.question_id).first()
                
                if existingAnswer:
                    existingAnswer.selectedOption_id = selectedOptionID
                    existingAnswer.isCorrect = is_correct
                else:
                    # user anseer toh banana hai how can i miss this?
                    user_answer = UserAnswer(
                        result_id = quiz_result.quizResult_id,
                        question_id = question.question_id,
                        selectedOption_id = selectedOptionID,
                        isCorrect = is_correct
                    )
                    db.session.add(user_answer)
            else:
                is_correct = False
                user_answer = UserAnswer(
                        result_id = quiz_result.quizResult_id,
                        question_id = question.question_id,
                        isCorrect = is_correct
                    )
                db.session.add(user_answer)

        correctAnswers = UserAnswer.query.filter_by(result_id = quiz_result.quizResult_id,isCorrect = True).count()
        
        incorrectAnswers = UserAnswer.query.filter_by(result_id = quiz_result.quizResult_id,isCorrect = False).count()
        
        quiz_result.marks_scored = (correctAnswers * quiz.marking_scheme_pos) - (incorrectAnswers * quiz.marking_scheme_neg)
        quiz_result.attempt_ended_at = datetime.now(IST)
        quiz_result.quiz_status = 'completed'
        
        db.session.commit()
        flash('Quiz submitted successfully!', 'success')

        uniqueQuizAttempts = QuizResult.query.filter_by(user_id = userID).group_by(QuizResult.quiz_id).count()
        print(uniqueQuizAttempts)
    
        if uniqueQuizAttempts > 150:
            user.rank = "Quiz Radiant"
        elif uniqueQuizAttempts > 100:
            user.rank = "Sage of Quizzes"
        elif uniqueQuizAttempts > 50:
            user.rank = "Brainiac"
        elif uniqueQuizAttempts > 20:
            user.rank = "Climbing Trooper"
        elif uniqueQuizAttempts > 10:
            user.rank = "Thinker in training"
        
        db.session.commit()
        if prevRank != user.rank:
            return redirect(url_for('user_rank_update'))
            
        return redirect(url_for('quiz_result', quizID = quiz.quiz_id, resultID = quiz_result.quizResult_id))
    
    user_answers = {}
    if existingAttempt:
        for answer in existingAttempt.user_answers:
            user_answers[answer.question_id] = answer.selectedOption_id
    
    
    return render_template('userAttemptQuiz.html', userName = current_user.name, quiz = quiz, quiz_result = quiz_result, user_answers = user_answers, user = current_user)


# ------------- USER RANK UPDATE ROUTE ! ---------------
@app.route('/user/rank/updated', methods = ['GET'])
@role_required('user')
@login_required
def user_rank_update():

    return render_template('updatedUserRank.html', userName = current_user.name, user = current_user)



# ------------- USER QUIZ RESULT ROUTE ! ---------------
@app.route('/user/quiz/<int:quizID>/result/<int:resultID>', methods=['POST', 'GET'])
@role_required('user')
@login_required    
def quiz_result(quizID, resultID):

    result = QuizResult.query.filter_by(quizResult_id = resultID).first()
    quiz = Quiz.query.filter_by(quiz_id = quizID).first()
    
    if result.user_id != current_user.id:
        flash('You are not authorized to view this result', category = 'error')
        return redirect(url_for('user_dashboard'))
    
    return render_template('userQuizResult.html', userName = current_user.name, result=result)


# ------------- USER SUMMARY CHART ROUTE ! ---------------
@app.route('/user/summary', methods=['POST', 'GET'])
@role_required('user')
@login_required
def user_summary():

    quiz_results = QuizResult.query.filter_by(user_id=current_user.id).all()
    
    results_data = []
    for result in quiz_results:
 
        quiz = result.quiz
        chapter = quiz.chapter
        subject = chapter.subject
        
        result_dict = {
            'quizResult_id': result.quizResult_id,
            'marks_scored': result.marks_scored,
            'total_marks': result.total_marks,
            'attempt_no': result.attempt_no,
            'attempt_started_at': result.attempt_started_at.isoformat(),
            'attempt_ended_at': result.attempt_ended_at.isoformat() if result.attempt_ended_at else None,
            'quiz': {
                'quiz_id': quiz.quiz_id,
                'name': quiz.name,
                'chapter': {
                    'chapter_id': chapter.chapter_id,
                    'name': chapter.name,
                    'subject': {
                        'subject_id': subject.subject_id,
                        'name': subject.name
                    }
                }
            }
        }
        results_data.append(result_dict)
    
    
    return render_template('userSummaryChart.html', userName = current_user.name, quiz_results=results_data)


# ------------- ERROR HANDLING ROUTES ! --------------
@app.errorhandler(403)
def forbiddenAccess(error):
    return render_template('403.html'), 403