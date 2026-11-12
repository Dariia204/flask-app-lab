
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    session,
)

from flask_wtf import FlaskForm

from app import db
from app.posts import post_bp
from app.posts.models import Post
from app.posts.forms import PostForm


def get_post_author():
    return str(
        session.get("username")
        or session.get("user")
        or "Anonymous"
    )[:20]


@post_bp.route("/")
@post_bp.route("")
def all_posts():
    stmt = (
        db.select(Post)
        .where(Post.is_active.is_(True))
        .order_by(Post.posted.desc())
    )

    posts = db.session.scalars(stmt).all()

    return render_template(
        "posts/all_posts.html",
        posts=posts,
        title="Усі пости",
    )


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            posted=form.posted.data,
            is_active=form.is_active.data,
            author=get_post_author(),
        )

        db.session.add(post)
        db.session.commit()

        flash(
            "Пост успішно додано!",
            "success",
        )

        return redirect(
            url_for("posts.detail_post", id=post.id)
        )

    return render_template(
        "posts/add_post.html",
        form=form,
        title="Додати пост",
        heading="Створення поста",
    )


@post_bp.route("/<int:id>")
def detail_post(id):
    post = db.get_or_404(Post, id)

    return render_template(
        "posts/detail_post.html",
        post=post,
        title=post.title,
    )


@post_bp.route(
    "/<int:id>/update",
    methods=["GET", "POST"],
)
def update_post(id):
    post = db.get_or_404(Post, id)

    form = PostForm(obj=post)

    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.commit()

        flash(
            "Пост успішно оновлено!",
            "success",
        )

        return redirect(
            url_for("posts.detail_post", id=post.id)
        )

    return render_template(
        "posts/add_post.html",
        form=form,
        post=post,
        title="Редагувати пост",
        heading="Редагування поста",
    )


@post_bp.route(
    "/<int:id>/delete",
    methods=["GET", "POST"],
)
def delete_post(id):
    post = db.get_or_404(Post, id)

    form = FlaskForm()

    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()

        flash(
            "Пост успішно видалено!",
            "success",
        )

        return redirect(
            url_for("posts.all_posts")
        )

    return render_template(
        "posts/delete_confirm.html",
        post=post,
        form=form,
        title="Видалити пост",
    )
