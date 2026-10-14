from flask import render_template, abort
from app.products import products_bp

# Масив товарів із завдання
products = [
    {
        "id": 1,
        "name": "Laptop",
        "price": 1200,
        "content": "Потужний ноутбук з процесором Intel Core i7, 16 ГБ оперативної пам'яті та SSD на 512 ГБ."
    },
    {
        "id": 2,
        "name": "Phone",
        "price": 800,
        "content": "Смартфон із 6.5-дюймовим OLED-дисплеєм, подвійною камерою та акумулятором на 5000 мА·год."
    },
    {
        "id": 3,
        "name": "PC",
        "price": 1800,
        "content": "Настільний комп'ютер для ігор або роботи з графікою: RTX 4070, 32 ГБ RAM, 1 ТБ SSD."
    }
]

# Маршрут для списку всіх товарів
@products_bp.route('/products')
def product_list():
    return render_template('products/products.html', products=products, title='Список товарів')

# Маршрут для детальної інформації про товар за його id
@products_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product is None:
        abort(404)
    return render_template('products/detail_product.html', product=product, title=product['name'])