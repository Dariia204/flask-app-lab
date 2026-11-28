
from sqlalchemy import String, Text, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash
from flask_login import UserMixin

from app import db, bcrypt, login_manager


followers = db.Table(
    "followers",
    db.Column(
        "follower_id",
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True
    ),
    db.Column(
        "followed_id",
        db.Integer,
        db.ForeignKey("users.id"),
        primary_key=True
    )
)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(80), unique=True, nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )

    password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    full_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    bio: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("0"),
        nullable=False
    )

    posts: Mapped[list["Post"]] = relationship(
        "Post", back_populates="user"
    )

    following: Mapped[list["User"]] = relationship(
        "User",
        secondary=followers,
        primaryjoin=id == followers.c.follower_id,
        secondaryjoin=id == followers.c.followed_id,
        back_populates="followers"
    )

    followers: Mapped[list["User"]] = relationship(
        "User",
        secondary=followers,
        primaryjoin=id == followers.c.followed_id,
        secondaryjoin=id == followers.c.follower_id,
        back_populates="following"
    )

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    def check_password(self, password):
        try:
            if self.password.startswith(("$2a$", "$2b$", "$2y$")):
                return bcrypt.check_password_hash(
                    self.password, password
                )

            return check_password_hash(
                self.password, password
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
