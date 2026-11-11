
import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.config import config


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv(
            "FLASK_CONFIG",
            "development"
        )

    app = Flask(__name__)

    app.config.from_object(
        config.get(config_name, config["development"])
    )

    db.init_app(app)
    migrate.init_app(app, db)

    from app.products import products_bp
    from app.users import users_bp
    from app.posts import post_bp
    from app.views import main_bp

    app.register_blueprint(products_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(main_bp)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template(
            "404.html",
            title="Сторінку не знайдено"
        ), 404

    return app


app = create_app()
