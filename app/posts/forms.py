
from datetime import datetime
from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    DateTimeLocalField,
    SelectField,
    SelectMultipleField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    Length,
    InputRequired,
)


class PostForm(FlaskForm):
    title = StringField(
        "Заголовок",
        validators=[DataRequired(), Length(min=3, max=150)]
    )

    content = TextAreaField(
        "Текст публікації",
        validators=[DataRequired(), Length(min=5, max=10000)],
        render_kw={"rows": 6}
    )

    is_active = BooleanField(
        "Активна публікація",
        default=True
    )

    posted = DateTimeLocalField(
        "Дата та час публікації",
        format="%Y-%m-%dT%H:%M",
        default=datetime.now,
        validators=[InputRequired()]
    )

    category = SelectField(
        "Категорія",
        choices=[
            ("news", "Новини"),
            ("publication", "Публікації"),
            ("tech", "Технології"),
            ("other", "Інше"),
        ],
        validators=[DataRequired()]
    )

    tags = SelectMultipleField(
        "Теги",
        coerce=int,
        render_kw={"size": 4}
    )

    submit = SubmitField("Зберегти")


class CommentForm(FlaskForm):
    content = TextAreaField(
        "Коментар",
        validators=[
            DataRequired(),
            Length(min=1, max=1000)
        ],
        render_kw={
            "rows": 3,
            "placeholder": "Напишіть коментар..."
        }
    )

    submit = SubmitField("Зберегти")
