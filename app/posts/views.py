
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from flask_wtf import FlaskForm

from app import db
from app.posts import post_bp
from app.posts.models import Post, Tag
from app.posts.forms import PostForm
from app.users.models import User
from sqlalchemy.orm import joinedload, selectinload

def set_form_choices(form):
    authors = db.session.scalars(
        db.select(User).order_by(User.id)
    ).all()

    tags = db.session.scalars(
        db.select(Tag).order_by(Tag.id)
    ).all()

    form.author_id.choices = [
        (author.id, author.username)
        for author in authors
    ]

    form.tags.choices = [
        (tag.id, tag.name)
        for tag in tags
    ]


def get_selected_tags(form):
    return db.session.scalars(
        db.select(Tag).where(
            Tag.id.in_(form.tags.data or [])
        )
    ).all()


@post_bp.route("/")
@post_bp.route("")
def all_posts():
    stmt = (
        db.select(Post)
        .options(
            joinedload(Post.user),
            selectinload(Post.tags)
        )
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
    set_form_choices(form)

    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            posted=form.posted.data,
            is_active=form.is_active.data,
            user_id=form.author_id.data,
        )

        post.tags = get_selected_tags(form)

        db.session.add(post)
        db.session.commit()

        flash("Пост успішно додано!", "success")

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
    set_form_choices(form)

    if request.method == "GET":
        form.author_id.data = post.user_id
        form.tags.data = [
            tag.id for tag in post.tags
        ]

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        post.posted = form.posted.data
        post.is_active = form.is_active.data
        post.user_id = form.author_id.data

        post.tags = get_selected_tags(form)

        db.session.commit()

        flash("Пост успішно оновлено!", "success")

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

        flash("Пост успішно видалено!", "success")

        return redirect(
            url_for("posts.all_posts")
        )

    return render_template(
        "posts/delete_confirm.html",
        post=post,
        form=form,
        title="Видалити пост",
    )
