
import smtplib

from email.message import EmailMessage
from flask import current_app


def send_notification(recipient, subject, body):

    config = current_app.config

    if not config.get("MAIL_ENABLED"):
        return False

    try:
        message = EmailMessage()

        message["From"] = config["MAIL_DEFAULT_SENDER"]
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(body)

        with smtplib.SMTP(
            config["MAIL_SERVER"],
            config["MAIL_PORT"],
            timeout=5
        ) as server:

            if config["MAIL_USE_TLS"]:
                server.starttls()

            if config["MAIL_USERNAME"]:
                server.login(
                    config["MAIL_USERNAME"],
                    config["MAIL_PASSWORD"]
                )

            server.send_message(message)

        current_app.logger.info(
            "Email notification sent"
        )

        return True

    except (OSError, smtplib.SMTPException, ValueError):

        current_app.logger.exception(
            "Email notification failed"
        )

        return False


def notify_follow(recipient, actor):

    if recipient.id == actor.id:
        return False

    return send_notification(
        recipient.email,
        "SocialSpace — новий підписник",
        (
            f"Привіт, {recipient.username}!\n\n"
            f"Користувач {actor.username} підписався на вас.\n\n"
            "З повагою, команда SocialSpace."
        )
    )


def notify_like(post, actor):

    if post.user_id == actor.id:
        return False

    return send_notification(
        post.user.email,
        "SocialSpace — новий лайк",
        (
            f"Привіт, {post.user.username}!\n\n"
            f"Користувач {actor.username} вподобав "
            f"вашу публікацію «{post.title}».\n\n"
            "З повагою, команда SocialSpace."
        )
    )


def notify_comment(post, actor, comment):

    if post.user_id == actor.id:
        return False

    return send_notification(
        post.user.email,
        "SocialSpace — новий коментар",
        (
            f"Привіт, {post.user.username}!\n\n"
            f"Користувач {actor.username} прокоментував "
            f"вашу публікацію «{post.title}».\n\n"
            f"Коментар: {comment.content}\n\n"
            "З повагою, команда SocialSpace."
        )
    )
