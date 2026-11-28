
from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
)

from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    Optional,
)

from app import db
from app.users.models import User


def validate_password_size(form, field):
    if len(field.data.encode("utf-8")) > 72:
        raise ValidationError(
            "Пароль не повинен перевищувати 72 байти."
        )


class RegistrationForm(FlaskForm):
    username = StringField(
        "Ім'я користувача",
        validators=[
            DataRequired(),
            Length(min=2, max=20),
        ],
    )

    email = StringField(
        "Електронна пошта",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120),
        ],
    )

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(),
            Length(min=6, max=72),
            validate_password_size,
        ],
    )

    confirm_password = PasswordField(
        "Підтвердження пароля",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="Паролі не збігаються.",
            ),
        ],
    )

    submit = SubmitField("Зареєструватися")

    def validate_username(self, username):
        user = db.session.scalar(
            db.select(User).where(
                User.username == username.data.strip()
            )
        )

        if user:
            raise ValidationError(
                "Це ім'я користувача вже зайняте."
            )

    def validate_email(self, email):
        user = db.session.scalar(
            db.select(User).where(
                User.email == email.data.strip().lower()
            )
        )

        if user:
            raise ValidationError(
                "Ця електронна пошта вже використовується."
            )


class LoginForm(FlaskForm):
    email = StringField(
        "Електронна пошта",
        validators=[
            DataRequired(),
            Email(),
        ],
    )

    password = PasswordField(
        "Пароль",
        validators=[DataRequired()],
    )

    remember = BooleanField("Запам'ятати мене")

    submit = SubmitField("Увійти")


class ProfileForm(FlaskForm):
    full_name = StringField(
        "Повне ім'я",
        validators=[Optional(), Length(max=100)]
    )

    bio = TextAreaField(
        "Про себе",
        validators=[Optional(), Length(max=1000)],
        render_kw={"rows": 4}
    )

    submit = SubmitField("Зберегти профіль")
