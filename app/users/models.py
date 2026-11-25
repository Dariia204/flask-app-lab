
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash
from flask_login import UserMixin

from app import db, bcrypt, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="user"
    )

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    def check_password(self, password):
        try:
            if self.password.startswith(("$2a$", "$2b$", "$2y$")):
                return bcrypt.check_password_hash(
                    self.password,
                    password
                )

            return check_password_hash(
                self.password,
                password
            )

        except (ValueError, TypeError):
            return False

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None
