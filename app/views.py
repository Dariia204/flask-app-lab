
import logging
from pathlib import Path

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from app import app
from forms import ContactForm


LOG_FILE = Path(app.root_path).parent / "app.log"

logger = logging.getLogger("contact_form")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
    )

    logger.addHandler(handler)


@app.route("/")
def homepage():
    return render_template(
        "homepage.html",
        title="Головна",
        agent=request.user_agent.string,
    )


@app.route("/resume")
def resume():
    return render_template(
        "resume.html",
        title="Резюме",
    )


@app.route("/contact", methods=["GET", "POST"])
@app.route("/contacts", methods=["GET", "POST"])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        try:
            logger.info(
                "Контактна форма: "
                "name=%s, email=%s, "
                "category=%s, message=%s",
                form.name.data,
                form.email.data,
                form.category.data,
                form.message.data.replace("\n", " "),
            )

            flash(
                "Повідомлення успішно записано!",
                "success",
            )

        except Exception:
            logger.exception(
                "Помилка запису контактної форми"
            )

            flash(
                "Не вдалося записати повідомлення.",
                "danger",
            )

        return redirect(url_for("contact"))

    if request.method == "POST":
        flash(
            "Форма містить помилки. "
            "Перевірте введені дані.",
            "danger",
        )

    return render_template(
        "contacts.html",
        form=form,
        title="Контакти",
    )
