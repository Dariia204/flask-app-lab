from flask import Flask

app = Flask(__name__)
app.config.from_pyfile("../config.py")

# Імпортуємо головні маршрути views
from app import views

# Імпортуємо та реєструємо Blueprint users
from app.users import users_bp
app.register_blueprint(users_bp)