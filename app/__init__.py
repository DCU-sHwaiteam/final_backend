from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_cors import CORS
from flask_migrate import Migrate
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
     
    app.secret_key = os.getenv('FLASK_SECRET_KEY')  

    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    Session(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
     
    print("SQLALCHEMY_DATABASE_URI =", app.config['SQLALCHEMY_DATABASE_URI'])
 
    db.init_app(app)
    Migrate(app, db)
    CORS(app, supports_credentials=True)

    from app.routes.attendance import bp as attendance_bp
    app.register_blueprint(attendance_bp)

    from app.routes.user import bp as user_bp
    app.register_blueprint(user_bp)
    
    from app.routes.club import bp as club_bp
    app.register_blueprint(club_bp)

    from app.routes.clubmembership import bp as clubmembership_bp
    app.register_blueprint(clubmembership_bp)   
    
    return app
