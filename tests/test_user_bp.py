import unittest
from app import app


class FlaskAppTestCase(unittest.TestCase):

 def setUp(self):
    """Налаштування тестового клієнта перед кожним тестом."""
    app.config['TESTING'] = True
    self.client = app.test_client()

def test_greetings_page(self):
    """Тест маршруту /hi/<name>."""
    response = self.client.get('/hi/John?age=30')
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'JOHN', response.data)
    self.assertIn(b'30', response.data)

def test_admin_page(self):
    """Тест маршруту /admin із перенаправленням."""
    response = self.client.get('/admin', follow_redirects=True)
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'ADMINISTRATOR', response.data)
    self.assertIn(b'45', response.data)


if __name__ == '__main__':
 unittest.main()