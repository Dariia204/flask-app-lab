
from pathlib import Path
from uuid import uuid4
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

import markdown
import bleach

from markupsafe import Markup


UPLOAD_DIR = Path(__file__).resolve().parent / "static" / "uploads"

MAX_IMAGE_SIZE = 5 * 1024 * 1024

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def save_image(file):
    if not file or not file.filename:
        return None

    data = file.stream.read(MAX_IMAGE_SIZE + 1)

    if len(data) > MAX_IMAGE_SIZE:
        raise ValueError("Розмір зображення не повинен перевищувати 5 МБ.")

    try:
        with Image.open(BytesIO(data)) as image:

            if image.format not in ALLOWED_FORMATS:
                raise ValueError("Дозволені формати: JPG, PNG, WEBP.")

            if image.width * image.height > 20000000:
                raise ValueError("Зображення має завеликі розміри.")

            image.load()

            image = ImageOps.exif_transpose(image)
            image.thumbnail((1600, 1600))

            image = image.convert("RGB")

            UPLOAD_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

            filename = f"{uuid4().hex}.jpg"

            image.save(
                UPLOAD_DIR / filename,
                format="JPEG",
                quality=88
            )

            return filename

    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError
    ) as error:
        raise ValueError(
            "Не вдалося обробити зображення."
        ) from error


def delete_image(filename):
    if not filename:
        return

    path = UPLOAD_DIR / Path(filename).name

    if path.is_file():
        path.unlink()


def render_markdown(content):
    html = markdown.markdown(
        content or "",
        extensions=[
            "extra",
            "nl2br",
            "sane_lists"
        ]
    )

    allowed_tags = [
        "p", "br", "strong", "em",
        "h1", "h2", "h3", "h4",
        "h5", "h6",
        "ul", "ol", "li",
        "blockquote", "pre", "code",
        "a", "hr",
        "table", "thead", "tbody",
        "tr", "th", "td"
    ]

    cleaned_html = bleach.clean(
        html,
        tags=allowed_tags,
        attributes={
            "a": ["href", "title"]
        },
        protocols=["http", "https", "mailto"],
        strip=True
    )

    return Markup(cleaned_html)
