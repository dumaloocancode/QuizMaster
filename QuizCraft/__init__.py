from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# create the db instance
db = SQLAlchemy()
# define the database name and Path
DB_NAME = 'testDatabase.sqlite3'
DB_PATH = os.path.join(os.getcwd(), 'QuizCraft', DB_NAME)
UPLOAD_FOLDER = os.path.join('QuizCraft/static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '7x2g18y39g8hf1buidbqw1w76'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app) # this command always initializes SQLAlchemy within the app
    app.app_context().push()
    return app
    
def create_database(app):
    if not os.path.exists(DB_PATH):
        with app.app_context():
            db.create_all()
            print('Database created successfully!')
