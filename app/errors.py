
from flask import render_template
from app import app


ERRORS = {
    400: (
        "Некоректний запит",
        "Перевірте введені дані та спробуйте ще раз."
    ),
    403: (
        "Доступ заборонено",
        "У вас недостатньо прав для виконання цієї дії."
    ),
    404: (
        "Сторінку не знайдено",
        "Можливо, сторінку видалено або змінено її адресу."
    ),
    413: (
        "Файл завеликий",
        "Максимальний розмір запиту становить 5 МБ."
    ),
    500: (
        "Помилка сервера",
        "Виникла внутрішня помилка. Спробуйте пізніше."
    )
}


def handle_error(error):
    code = error.code
    title, message = ERRORS[code]

    return render_template(
        "errors/error.html",
        code=code,
        title=title,
        message=message
    ), code


for code in ERRORS:
    app.register_error_handler(code, handle_error)
