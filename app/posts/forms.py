
from datetime import datetime

from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    BooleanField,
    DateTimeLocalField,
    SelectField,
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
        validators=[
            DataRequired(),
            Length(min=3, max=150),
        ],
    )

    content = TextAreaField(
        "Текст поста",
        validators=[
            DataRequired(),
            Length(min=5),
        ],
        render_kw={"rows": 6},
    )

    enabled = BooleanField(
        "Активний пост",
        default=True,
    )

    publish_date = DateTimeLocalField(
        "Дата та час публікації",
        format="%Y-%m-%dT%H:%M",
        default=datetime.now,
        validators=[InputRequired()],
    )

    category = SelectField(
        "Категорія",
        choices=[
            ("news", "Новини"),
            ("publication", "Публікації"),
            ("tech", "Технології"),
            ("other", "Інше"),
        ],
        validators=[DataRequired()],
    )

    submit = SubmitField("Зберегти")
