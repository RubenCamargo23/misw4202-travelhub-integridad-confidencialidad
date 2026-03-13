import os
import logging
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from modelos import db, Usuario
from vistas import VistaLogin, VistaSignUp
from passlib.context import CryptContext

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('USERS_DB_URL', f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../users.db'))}")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'secret-key')
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    CORS(app)
    db.init_app(app)
    JWTManager(app)
    
    api = Api(app)
    api.add_resource(VistaLogin, '/login')
    api.add_resource(VistaSignUp, '/signup')
    
    return app

app = create_app()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

with app.app_context():
    db.create_all()
    # Populate test users
    if Usuario.query.count() == 0:
        db.session.add(Usuario(username="admin_ar", password_hash=pwd_context.hash("admin123"), rol="admin", pais="AR"))
        db.session.add(Usuario(username="user_co", password_hash=pwd_context.hash("user123"), rol="user", pais="CO"))
        db.session.add(Usuario(username="user_ar", password_hash=pwd_context.hash("user123"), rol="user", pais="AR"))
        db.session.add(Usuario(username="admin_co", password_hash=pwd_context.hash("admin123"), rol="admin", pais="CO"))
        db.session.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=False)
