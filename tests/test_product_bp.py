
import unittest

from app import app


class ProductBpTestCase(unittest.TestCase):

    def setUp(self):
        """Налаштування тестового клієнта."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_product_list_page(self):
        """Перевірка сторінки каталогу товарів."""
        response = self.client.get("/products")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Каталог товарів".encode("utf-8"),
            response.data
        )

    def test_product_detail_page(self):
        """Перевірка сторінки деталей товару."""
        response = self.client.get("/products/1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Ціна:".encode("utf-8"),
            response.data
        )

    def test_product_not_found(self):
        """Перевірка неіснуючого товару."""
        response = self.client.get("/products/999")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
