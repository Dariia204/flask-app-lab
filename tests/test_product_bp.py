import unittest
from app import app


class ProductBpTestCase(unittest.TestCase):

  def setUp(self):
    """Налаштування тестового клієнта."""
    app.config['TESTING'] = True
    self.client = app.test_client()

  def test_product_list_page(self):
    """Тест відображення списку всіх товарів /products."""
    response = self.client.get('/products')
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'Laptop', response.data)
    self.assertIn(b'Phone', response.data)
    self.assertIn(b'PC', response.data)

  def test_product_detail_page(self):
    """Тест відображення детальної сторінки товару /products/1."""
    response = self.client.get('/products/1')
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'Laptop', response.data)
    self.assertIn(b'1200', response.data)

  def test_product_not_found(self):
    """Тест для неіснуючого товару (має бути 404)."""
    response = self.client.get('/products/999')
    self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
  unittest.main()