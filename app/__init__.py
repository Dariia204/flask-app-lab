
from flask import Flask

from config import Config


app = Flask(__name__)
app.config.from_object(Config)


from app.products import products_bp
from app.users import users_bp


app.register_blueprint(products_bp)
app.register_blueprint(users_bp)


from app import views
