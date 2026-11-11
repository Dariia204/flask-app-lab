
import uuid
from datetime import datetime
from pathlib import Path

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
    current_app,
)

from flask_wtf import FlaskForm
from tinydb import TinyDB, Query
from werkzeug.utils import secure_filename

from app.products import products_bp
from forms import ProductForm


# Шляхи до даних і зображень
APP_DIR = Path(__file__).resolve().parents[1]

DATA_FILE = APP_DIR / "data" / "products.json"

UPLOAD_DIR = (
    Path(__file__).resolve().parent
    / "static"
    / "uploads"
)

DATA_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# Ініціалізація TinyDB
db = TinyDB(DATA_FILE, encoding="utf-8")
products_table = db.table("products")

Product = Query()


# Допоміжні функції
def get_product(product_id):
    product = products_table.get(
        Product.id == product_id
    )

    if product is None:
        abort(404)

    return product


def get_next_id():
    products = products_table.all()

    return max(
        (
            int(product.get("id", 0))
            for product in products
        ),
        default=0,
    ) + 1


def get_current_datetime():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def save_image(upload):
    if upload is None:
        return None

    if not getattr(upload, "filename", ""):
        return None

    original_name = secure_filename(
        upload.filename
    )

    if not original_name:
        return None

    extension = Path(original_name).suffix.lower()

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
    }

    if extension not in allowed_extensions:
        raise ValueError(
            "Недозволений формат зображення."
        )

    filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    destination = UPLOAD_DIR / filename

    upload.save(destination)

    # Зберігаємо відносний шлях у TinyDB
    return f"uploads/{filename}"


def get_image_url(image_path):
    if not image_path:
        return None

    # Підтримка онлайн-зображень
    if image_path.startswith(
        ("http://", "https://")
    ):
        return image_path

    # Підтримка старих і нових шляхів
    filename = image_path

    if filename.startswith("uploads/"):
        filename = filename[len("uploads/"):]

    local_file = UPLOAD_DIR / filename

    if not local_file.is_file():
        return None

    return url_for(
        "products.static",
        filename=f"uploads/{filename}",
    )


# Каталог товарів
@products_bp.route("/products")
@products_bp.route("/product")
def product_list():
    products = products_table.all()

    for product in products:
        product["image_url"] = get_image_url(
            product.get("image", "")
        )

    return render_template(
        "products/products.html",
        products=products,
        title="Каталог товарів",
    )


# Додавання товару
@products_bp.route(
    "/products/add",
    methods=["GET", "POST"],
)
@products_bp.route(
    "/product/add",
    methods=["GET", "POST"],
)
def add_product():
    form = ProductForm()

    if form.validate_on_submit():
        try:
            image_path = save_image(
                form.image.data
            )

            product_data = {
                "id": get_next_id(),
                "name": form.name.data,
                "content": form.content.data,
                "price": float(form.price.data),
                "category": form.category.data,
                "quantity": form.quantity.data,
                "image": image_path or "",
                "created_at": get_current_datetime(),
            }

            products_table.insert(
                product_data
            )

            flash(
                "Товар успішно додано!",
                "success",
            )

            return redirect(
                url_for("products.product_list")
            )

        except Exception:
            current_app.logger.exception(
                "Помилка додавання товару"
            )

            flash(
                "Не вдалося додати товар.",
                "danger",
            )

    elif request.method == "POST":
        flash(
            "Перевірте поля форми.",
            "danger",
        )

    return render_template(
        "products/add_product.html",
        form=form,
        title="Додати товар",
    )


# Перегляд одного товару
@products_bp.route(
    "/products/<int:id>"
)
@products_bp.route(
    "/product/<int:id>"
)
def detail_product(id):
    product = get_product(id)

    product["image_url"] = get_image_url(
        product.get("image", "")
    )

    delete_form = FlaskForm()

    return render_template(
        "products/detail_product.html",
        product=product,
        delete_form=delete_form,
        title=product["name"],
    )


# Редагування товару
@products_bp.route(
    "/products/<int:id>/edit",
    methods=["GET", "POST"],
)
@products_bp.route(
    "/product/<int:id>/edit",
    methods=["GET", "POST"],
)
def edit_product(id):
    product = get_product(id)

    form = ProductForm()

    if request.method == "GET":
        form.process(data=product)

    if form.validate_on_submit():
        try:
            new_image = save_image(
                form.image.data
            )

            image_path = (
                new_image
                or product.get("image", "")
            )

            updated_data = {
                "name": form.name.data,
                "content": form.content.data,
                "price": float(form.price.data),
                "category": form.category.data,
                "quantity": form.quantity.data,
                "image": image_path,
            }

            # id і created_at не змінюємо
            products_table.update(
                updated_data,
                Product.id == id,
            )

            flash(
                "Товар успішно оновлено!",
                "success",
            )

            return redirect(
                url_for(
                    "products.detail_product",
                    id=id,
                )
            )

        except Exception:
            current_app.logger.exception(
                "Помилка редагування товару"
            )

            flash(
                "Не вдалося оновити товар.",
                "danger",
            )

    elif request.method == "POST":
        flash(
            "Перевірте поля форми.",
            "danger",
        )

    product["image_url"] = get_image_url(
        product.get("image", "")
    )

    return render_template(
        "products/edit_product.html",
        form=form,
        product=product,
        title="Редагувати товар",
    )


# Видалення товару
@products_bp.route(
    "/products/<int:id>/delete",
    methods=["POST"],
)
@products_bp.route(
    "/product/<int:id>/delete",
    methods=["POST"],
)
def delete_product(id):
    delete_form = FlaskForm()

    if not delete_form.validate_on_submit():
        abort(400)

    get_product(id)

    products_table.remove(
        Product.id == id
    )

    flash(
        "Товар успішно видалено!",
        "info",
    )

    return redirect(
        url_for("products.product_list")
    )
