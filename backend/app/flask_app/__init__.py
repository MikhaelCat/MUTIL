from flask import Flask
from app.core.config import settings
from app.core.database import engine
from app.models.models import Base

def create_flask_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация расширений
    from app.flask_app import routes
    app.register_blueprint(routes.bp)
    
    # Создание таблиц 
    with app.app_context():
        Base.metadata.create_all(bind=engine)
    
    return app