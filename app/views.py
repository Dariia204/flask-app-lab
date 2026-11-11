
import logging
from pathlib import Path

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from forms import ContactForm


main_bp = Blueprint("main", __name__)

LOG_FILE = Path(__file__).resolve().parent.parent / "app.log"

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


@main_bp.route("/")
def homepage():
    return render_template(
        "homepage.html",
        title="Головна",
        agent=request.user_agent.string,
    )


@main_bp.route("/resume")
def resume():
    return render_template(
        "resume.html",
        title="Резюме",
    )


@main_bp.route("/contact", methods=["GET", "POST"])
@main_bp.route("/contacts", methods=["GET", "POST"])
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

        return redirect(url_for("main.contact"))

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
