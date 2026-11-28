
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    make_response,
)

from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required,
)

from sqlalchemy.exc import IntegrityError

from app import db
from app.users import users_bp
from app.users.models import User
from app.users.forms import RegistrationForm, LoginForm


@users_bp.route("/hi/<string:name>")
def greetings(name):
    name_upper = name.upper()
    age = request.args.get("age", None, type=int)

    return render_template(
        "users/hi.html",
        name=name_upper,
        age=age,
        title="Greeting Page",
    )


@users_bp.route("/admin")
def admin():
    return redirect(
        url_for(
            "users.greetings",
            name="administrator",
            age=45,
            _external=True,
        )
    )


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
        )

        user.set_password(form.password.data)

        db.session.add(user)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            flash(
                "Користувач із такими даними вже існує.",
                "danger",
            )

            return render_template(
                "users/register.html",
                form=form,
                title="Реєстрація",
            )

        flash(
            "Обліковий запис успішно створено!",
            "success",
        )

        return redirect(url_for("users.login"))

    return render_template(
        "users/register.html",
        form=form,
        title="Реєстрація",
    )


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            db.select(User).where(
                User.email == form.email.data.lower()
            )
        )

        if user and user.check_password(form.password.data):
            session.clear()

            login_user(
                user,
                remember=form.remember.data
            )

            flash(
                "Ви успішно увійшли в систему!",
                "success",
            )

            return redirect(url_for("users.account"))

        flash(
            "Неправильна електронна пошта або пароль.",
            "danger",
        )

    return render_template(
        "users/login.html",
        form=form,
        title="Вхід",
    )


@users_bp.route("/account")
@login_required
def account():
    return render_template(
        "users/account.html",
        user=current_user,
        title="Обліковий запис",
    )


@users_bp.route("/users")
@login_required
def all_users():
    q = request.args.get("q", "").strip()[:150]
    page = request.args.get("page", 1, type=int)

    stmt = db.select(User)

    if q:
        stmt = stmt.where(
            db.or_(
                User.username.icontains(q, autoescape=True),
                User.full_name.icontains(q, autoescape=True)
            )
        )

    stmt = stmt.order_by(User.id)

    pagination = db.paginate(
        stmt,
        page=max(1, page),
        per_page=6,
        error_out=False
    )

    return render_template(
        "users/all_users.html",
        users=pagination.items,
        count=pagination.total,
        pagination=pagination,
        q=q,
        title="ористувачі"
    )

@users_bp.route("/profile")
@login_required
def profile():
    return render_template(
        "users/profile.html",
        title="Профіль",
        user=current_user.username,
        cookies=request.cookies,
        theme=request.cookies.get("theme", "light"),
    )


@users_bp.route("/logout")
@login_required
def logout():
    logout_user()

    flash(
        "Ви вийшли із системи.",
        "info",
    )

    return redirect(url_for("users.login"))


@users_bp.route("/cookie/add", methods=["POST"])
@login_required
def add_cookie():
    key = request.form.get("key")
    value = request.form.get("value")
    max_age = request.form.get("max_age", type=int)

    response = make_response(
        redirect(url_for("users.profile"))
    )

    if key and value and key not in (
        "session", "remember_token"
    ):
        response.set_cookie(
            key,
            value,
            max_age=max_age,
        )

        flash(
            f"Кукі '{key}' успішно додано!",
            "success",
        )

    return response


@users_bp.route("/cookie/delete", methods=["POST"])
@login_required
def delete_cookie():
    key = request.form.get("key")

    response = make_response(
        redirect(url_for("users.profile"))
    )

    if key and key not in (
        "session", "remember_token"
    ):
        response.delete_cookie(key)

        flash(
            f"Кукі '{key}' видалено!",
            "info",
        )

    return response


@users_bp.route("/cookie/delete_all", methods=["POST"])
@login_required
def delete_all_cookies():
    response = make_response(
        redirect(url_for("users.profile"))
    )

    for key in request.cookies:
        if key not in ("session", "remember_token"):
            response.delete_cookie(key)

    flash("Усі користувацькі кукі видалено!", "info")

    return response


@users_bp.route("/theme/<string:theme_name>")
@login_required
def change_theme(theme_name):
    response = make_response(
        redirect(url_for("users.profile"))
    )

    if theme_name in ("light", "dark"):
        response.set_cookie(
            "theme",
            theme_name,
            max_age=30 * 24 * 60 * 60,
        )

        flash(
            f"Тему змінено на {theme_name}!",
            "success",
        )

    return response


from flask import abort
from flask_wtf import FlaskForm
from app.users.forms import ProfileForm
from app.posts.models import Post


@users_bp.route("/account/edit", methods=["GET", "POST"])
@login_required
def edit_account():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.full_name = (form.full_name.data or "").strip()
        current_user.bio = (form.bio.data or "").strip()

        db.session.commit()

        flash("рофіль успішно оновлено!", "success")

        return redirect(url_for("users.account"))

    return render_template(
        "users/edit_account.html",
        form=form,
        title="едагування профілю"
    )


@users_bp.route("/user/<int:user_id>")
@login_required
def public_profile(user_id):
    user = db.get_or_404(User, user_id)

    stmt = db.select(Post).where(
        Post.user_id == user.id
    )

    if current_user.id != user.id and not current_user.is_admin:
        stmt = stmt.where(Post.is_active.is_(True))

    posts = db.session.scalars(
        stmt.order_by(Post.posted.desc())
    ).all()

    return render_template(
        "users/public_profile.html",
        user=user,
        posts=posts,
        action_form=FlaskForm(),
        title=user.username
    )


@users_bp.route("/user/<int:user_id>/follow", methods=["POST"])
@login_required
def toggle_follow(user_id):
    user = db.get_or_404(User, user_id)

    if not FlaskForm().validate_on_submit():
        abort(400)

    if user.id == current_user.id:
        abort(400)

    if user in current_user.following:
        current_user.following.remove(user)
        flash("и відписалися від користувача.", "info")
    else:
        current_user.following.append(user)
        flash("и підписалися на користувача!", "success")

    db.session.commit()

    return redirect(
        url_for("users.public_profile", user_id=user.id)
    )


@users_bp.route("/user/<int:user_id>/followers")
@login_required
def followers_list(user_id):
    user = db.get_or_404(User, user_id)

    return render_template(
        "users/connections.html",
        user=user,
        users=user.followers,
        heading="ідписники",
        title="ідписники"
    )


@users_bp.route("/user/<int:user_id>/following")
@login_required
def following_list(user_id):
    user = db.get_or_404(User, user_id)

    return render_template(
        "users/connections.html",
        user=user,
        users=user.following,
        heading="ідписки",
        title="ідписки"
    )

