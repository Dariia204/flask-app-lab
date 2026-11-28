
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    abort,
)

from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app import db
from app.admin import admin_bp
from app.users.models import User
from app.posts.models import Post, Comment, Like
from app.posts.views import cleanup_image


@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin:
        abort(403)


def validate_action():
    if not FlaskForm().validate_on_submit():
        abort(400)


def count_records(model):
    return db.session.scalar(
        db.select(func.count()).select_from(model)
    )


@admin_bp.route("/")
def dashboard():

    stats = {
        "users": count_records(User),
        "posts": count_records(Post),
        "comments": count_records(Comment),
        "likes": count_records(Like),
    }

    users = db.session.scalars(
        db.select(User).order_by(User.id)
    ).all()

    posts = db.session.scalars(
        db.select(Post)
        .options(joinedload(Post.user))
        .order_by(Post.posted.desc())
    ).all()

    comments = db.session.scalars(
        db.select(Comment)
        .options(
            joinedload(Comment.user),
            joinedload(Comment.post)
        )
        .order_by(Comment.created_at.desc())
    ).all()

    return render_template(
        "admin/dashboard.html",
        title="Панель адміністратора",
        stats=stats,
        users=users,
        posts=posts,
        comments=comments,
        action_form=FlaskForm()
    )


@admin_bp.route(
    "/users/<int:user_id>/role",
    methods=["POST"]
)
def toggle_user_role(user_id):

    validate_action()

    user = db.get_or_404(User, user_id)

    if user.id == current_user.id:
        flash(
            "Не можна змінити власну роль.",
            "warning"
        )
        return redirect(url_for("admin.dashboard"))

    user.is_admin = not user.is_admin

    db.session.commit()

    flash(
        f"Роль користувача {user.username} змінено.",
        "success"
    )

    return redirect(
        url_for("admin.dashboard") + "#users"
    )


@admin_bp.route(
    "/posts/<int:post_id>/status",
    methods=["POST"]
)
def toggle_post_status(post_id):

    validate_action()

    post = db.get_or_404(Post, post_id)

    post.is_active = not post.is_active

    db.session.commit()

    flash(
        "Статус публікації змінено.",
        "success"
    )

    return redirect(
        url_for("admin.dashboard") + "#posts"
    )


@admin_bp.route(
    "/posts/<int:post_id>/delete",
    methods=["POST"]
)
def delete_post(post_id):

    validate_action()

    post = db.get_or_404(Post, post_id)

    image_name = post.image

    db.session.delete(post)
    db.session.commit()

    cleanup_image(image_name)

    flash(
        "Публікацію видалено адміністратором.",
        "success"
    )

    return redirect(
        url_for("admin.dashboard") + "#posts"
    )


@admin_bp.route(
    "/comments/<int:comment_id>/delete",
    methods=["POST"]
)
def delete_comment(comment_id):

    validate_action()

    comment = db.get_or_404(Comment, comment_id)

    db.session.delete(comment)
    db.session.commit()

    flash(
        "Коментар видалено адміністратором.",
        "success"
    )

    return redirect(
        url_for("admin.dashboard") + "#comments"
    )
