
from datetime import datetime, timezone

from sqlalchemy import (
    String, Text, DateTime, Enum,
    Boolean, ForeignKey, text
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


post_tags = db.Table(
    "post_tags",
    db.Column(
        "post_id", db.Integer,
        db.ForeignKey("posts.id"),
        primary_key=True
    ),
    db.Column(
        "tag_id", db.Integer,
        db.ForeignKey("tags.id"),
        primary_key=True
    )
)


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    posted: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now
    )

    category: Mapped[str] = mapped_column(
        Enum("news", "publication", "tech", "other"),
        default="other",
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("1"),
        nullable=False
    )

    image: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="posts"
    )

    tags: Mapped[list["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts"
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    likes: Mapped[list["Like"]] = relationship(
        "Like",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Post {self.id}: {self.title}>"


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )

    posts: Mapped[list["Post"]] = relationship(
        secondary=post_tags,
        back_populates="tags"
    )

    def __repr__(self):
        return f"<Tag {self.name}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"), nullable=False
    )

    user: Mapped["User"] = relationship("User")

    post: Mapped["Post"] = relationship(
        "Post", back_populates="comments"
    )


class Like(db.Model):
    __tablename__ = "likes"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"), primary_key=True
    )

    user: Mapped["User"] = relationship("User")

    post: Mapped["Post"] = relationship(
        "Post", back_populates="likes"
    )
