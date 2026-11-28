
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    current_app,
)

from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from sqlalchemy.orm import joinedload, selectinload

from app import db
from app.posts import post_bp
from app.posts.models import Post, Tag, Comment, Like
from app.posts.forms import PostForm, CommentForm
from app.users.models import User
from app.notifications import notify_like, notify_comment

from app.posts.utils import (
    save_image,
    delete_image,
    render_markdown,
)


@post_bp.app_template_filter("markdown")
def markdown_filter(content):
    return render_markdown(content)


def cleanup_image(filename):
    try:
        delete_image(filename)
    except OSError:
        current_app.logger.exception(
            "Image cleanup failed"
        )


def set_form_choices(form):
    tags = db.session.scalars(
        db.select(Tag).order_by(Tag.id)
    ).all()

    form.tags.choices = [
        (tag.id, tag.name) for tag in tags
    ]


def get_selected_tags(form):
    return db.session.scalars(
        db.select(Tag).where(
            Tag.id.in_(form.tags.data or [])
        )
    ).all()


def can_manage(user_id):
    return (
        current_user.is_authenticated
        and (
            current_user.id == user_id
            or current_user.is_admin
        )
    )


def get_visible_post(id):
    post = db.get_or_404(Post, id)

    if not post.is_active and not can_manage(post.user_id):
        abort(404)

    return post


@post_bp.route("/")
@post_bp.route("")
def all_posts():
    return render_feed(personal=False)


def render_feed(personal=False):
    q = request.args.get("q", "").strip()[:150]
    page = request.args.get("page", 1, type=int)

    stmt = (
        db.select(Post)
        .options(
            joinedload(Post.user),
            selectinload(Post.tags),
            selectinload(Post.likes),
            selectinload(Post.comments)
        )
        .where(Post.is_active.is_(True))
    )

    if personal:
        following_ids = [
            user.id for user in current_user.following
        ]

        following_ids.append(current_user.id)

        stmt = stmt.where(
            Post.user_id.in_(following_ids)
        )

    if q:
        stmt = stmt.where(
            db.or_(
                Post.title.icontains(
                    q, autoescape=True
                ),
                Post.content.icontains(
                    q, autoescape=True
                ),
                Post.user.has(
                    db.or_(
                        User.username.icontains(
                            q, autoescape=True
                        ),
                        User.full_name.icontains(
                            q, autoescape=True
                        )
                    )
                ),
                Post.tags.any(
                    Tag.name.icontains(
                        q, autoescape=True
                    )
                )
            )
        )

    stmt = stmt.order_by(
        Post.posted.desc(),
        Post.id.desc()
    )

    pagination = db.paginate(
        stmt,
        page=max(1, page),
        per_page=6,
        error_out=False
    )

    return render_template(
        "posts/all_posts.html",
        posts=pagination.items,
        pagination=pagination,
        q=q,
        personal=personal,
        title="Моя стрічка" if personal else "Публікації"
    )


@post_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    set_form_choices(form)

    if form.validate_on_submit():

        try:
            image_name = save_image(form.image.data)

        except ValueError as error:
            form.image.errors.append(str(error))

        else:
            post = Post(
                title=form.title.data,
                content=form.content.data,
                category=form.category.data,
                posted=form.posted.data,
                is_active=form.is_active.data,
                user_id=current_user.id,
                image=image_name
            )

            post.tags = get_selected_tags(form)

            try:
                db.session.add(post)
                db.session.commit()

            except Exception:
                db.session.rollback()
                cleanup_image(image_name)
                raise

            flash(
                "Публікацію успішно створено!",
                "success"
            )

            return redirect(
                url_for("posts.detail_post", id=post.id)
            )

    return render_template(
        "posts/add_post.html",
        form=form,
        title="Нова публікація",
        heading="Створення публікації"
    )


@post_bp.route("/<int:id>")
def detail_post(id):
    post = get_visible_post(id)

    liked = False

    if current_user.is_authenticated:
        liked = db.session.get(
            Like, (current_user.id, post.id)
        ) is not None

    comments = db.session.scalars(
        db.select(Comment)
        .options(joinedload(Comment.user))
        .where(Comment.post_id == post.id)
        .order_by(Comment.created_at.desc())
    ).all()

    return render_template(
        "posts/detail_post.html",
        post=post,
        comments=comments,
        comment_form=CommentForm(),
        action_form=FlaskForm(),
        liked=liked,
        title=post.title
    )


@post_bp.route("/<int:id>/update", methods=["GET", "POST"])
@login_required
def update_post(id):
    post = db.get_or_404(Post, id)

    if not can_manage(post.user_id):
        abort(403)

    form = PostForm(data={
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "posted": post.posted,
        "is_active": post.is_active,
        "tags": [tag.id for tag in post.tags]
    })

    set_form_choices(form)

    if form.validate_on_submit():

        old_image = post.image

        try:
            new_image = save_image(form.image.data)

        except ValueError as error:
            form.image.errors.append(str(error))

        else:
            post.title = form.title.data
            post.content = form.content.data
            post.category = form.category.data
            post.posted = form.posted.data
            post.is_active = form.is_active.data
            post.tags = get_selected_tags(form)

            if new_image:
                post.image = new_image

            elif form.remove_image.data:
                post.image = None

            try:
                db.session.commit()

            except Exception:
                db.session.rollback()
                cleanup_image(new_image)
                raise

            if old_image != post.image:
                cleanup_image(old_image)

            flash("Публікацію оновлено!", "success")

            return redirect(
                url_for("posts.detail_post", id=post.id)
            )

    return render_template(
        "posts/add_post.html",
        form=form,
        post=post,
        title="Редагування",
        heading="Редагування публікації"
    )


@post_bp.route("/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete_post(id):
    post = db.get_or_404(Post, id)

    if not can_manage(post.user_id):
        abort(403)

    form = FlaskForm()

    if form.validate_on_submit():

        image_name = post.image

        db.session.delete(post)
        db.session.commit()

        cleanup_image(image_name)

        flash("Публікацію видалено!", "success")

        return redirect(
            url_for("posts.all_posts")
        )

    return render_template(
        "posts/delete_confirm.html",
        post=post,
        form=form,
        title="Видалення публікації"
    )


@post_bp.route("/<int:id>/like", methods=["POST"])
@login_required
def toggle_like(id):
    post = get_visible_post(id)

    if not FlaskForm().validate_on_submit():
        abort(400)

    like = db.session.get(
        Like, (current_user.id, post.id)
    )

    if like:
        db.session.delete(like)

    else:
        db.session.add(
            Like(
                user_id=current_user.id,
                post_id=post.id
            )
        )

    db.session.commit()

    if like is None:
        notify_like(post, current_user)

    return redirect(
        url_for("posts.detail_post", id=post.id)
    )


@post_bp.route("/<int:id>/comment", methods=["POST"])
@login_required
def add_comment(id):
    post = get_visible_post(id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data.strip(),
            user_id=current_user.id,
            post_id=post.id
        )

        db.session.add(comment)
        db.session.commit()

        notify_comment(post, current_user, comment)

        flash("Коментар додано!", "success")

    else:
        flash("Перевірте текст коментаря.", "danger")

    return redirect(
        url_for("posts.detail_post", id=post.id)
    )


@post_bp.route(
    "/comment/<int:id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_comment(id):
    comment = db.get_or_404(Comment, id)

    if not can_manage(comment.user_id):
        abort(403)

    get_visible_post(comment.post_id)

    form = CommentForm(obj=comment)

    if form.validate_on_submit():
        comment.content = form.content.data.strip()

        db.session.commit()

        flash("Коментар оновлено!", "success")

        return redirect(
            url_for(
                "posts.detail_post",
                id=comment.post_id
            )
        )

    return render_template(
        "posts/edit_comment.html",
        form=form,
        comment=comment,
        title="Редагування коментаря"
    )


@post_bp.route(
    "/comment/<int:id>/delete",
    methods=["POST"]
)
@login_required
def delete_comment(id):
    comment = db.get_or_404(Comment, id)

    if not can_manage(comment.user_id):
        abort(403)

    get_visible_post(comment.post_id)

    if not FlaskForm().validate_on_submit():
        abort(400)

    post_id = comment.post_id

    db.session.delete(comment)
    db.session.commit()

    flash("Коментар видалено!", "success")

    return redirect(
        url_for("posts.detail_post", id=post_id)
    )


@post_bp.route("/feed")
@login_required
def personal_feed():
    return render_feed(personal=True)
