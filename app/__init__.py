
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from config import Config


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


app = Flask(__name__)
app.config.from_object(Config)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lab8.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)

migrate = Migrate(app, db)

from app.products import products_bp
from app.users import users_bp
from app.posts import post_bp

from app.products import models
from app.users import models as user_models

app.register_blueprint(products_bp)
app.register_blueprint(users_bp)
app.register_blueprint(post_bp)

from app import views
