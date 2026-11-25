
from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    IntegerField,
    SelectField,
    SubmitField,
)

from wtforms.validators import (
    DataRequired,
    InputRequired,
    Email,
    Length,
    NumberRange,
    ValidationError,
)


CATEGORIES = [
    ("техніка", "Техніка"),
    ("одяг", "Одяг"),
    ("книги", "Книги"),
    ("інше", "Інше"),
]


class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я",
        validators=[
            DataRequired(),
            Length(min=2, max=100),
        ],
    )

    email = StringField(
        "Електронна пошта",
        validators=[
            DataRequired(),
            Email(),
        ],
    )

    category = SelectField(
        "Тема звернення",
        choices=[
            ("general", "Загальне питання"),
            ("support", "Технічна підтримка"),
            ("feedback", "Відгук"),
        ],
        validators=[DataRequired()],
    )

    message = TextAreaField(
        "Повідомлення",
        validators=[
            DataRequired(),
            Length(min=10, max=2000),
        ],
        render_kw={
            "rows": 5,
            "cols": 40,
        },
    )

    submit = SubmitField("Надіслати")


class ProductForm(FlaskForm):
    name = StringField(
        "Назва товару",
        validators=[
            DataRequired(),
            Length(min=3, max=100),
        ],
    )

    content = TextAreaField(
        "Опис товару",
        validators=[DataRequired()],
        render_kw={
            "rows": 5,
            "cols": 40,
        },
    )

    price = DecimalField(
        "Ціна",
        places=2,
        validators=[
            InputRequired(),
            NumberRange(min=Decimal("0.01")),
        ],
        render_kw={
            "step": "0.01",
            "min": "0.01",
        },
    )

    category = SelectField(
        "Категорія",
        choices=CATEGORIES,
        validators=[DataRequired()],
    )

    quantity = IntegerField(
        "Кількість",
        validators=[
            InputRequired(),
            NumberRange(min=0),
        ],
        render_kw={"min": "0"},
    )

    image = FileField(
        "Зображення товару",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png"],
                "Дозволені лише JPG, JPEG та PNG",
            ),
        ],
    )

    submit = SubmitField("Зберегти")

    def validate_price(self, field):
        if field.data is not None:
            if field.data.as_tuple().exponent < -2:
                raise ValidationError(
                    "Ціна може мати не більше "
                    "двох знаків після коми."
                )
