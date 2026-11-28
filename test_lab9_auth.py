
import pytest

from app import app, db
from app.users.models import User


TEST_USER = {
    "username": "LabTest",
    "email": "labtest@example.com",
    "password": "TestPassword2026!",
    "confirm_password": "TestPassword2026!",
}


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        # Захист від випадкового видалення робочої БД
        assert db.engine.url.database == ":memory:"

        db.create_all()

        try:
            yield app.test_client()
        finally:
            db.session.remove()
            db.drop_all()


def register_user(client):
    return client.post(
        "/register",
        data=TEST_USER,
        follow_redirects=True,
    )


def login_test_user(client, password=None):
    return client.post(
        "/login",
        data={
            "email": TEST_USER["email"],
            "password": password or TEST_USER["password"],
        },
        follow_redirects=True,
    )


# 1. Завантаження сторінки реєстрації
def test_register_page(client):
    response = client.get("/register")

    assert response.status_code == 200
    assert "Реєстрація" in response.get_data(as_text=True)


# 2. Завантаження сторінки входу
def test_login_page(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert "Вхід" in response.get_data(as_text=True)


# 3. Збереження користувача в базі даних
def test_user_registration(client):
    response = register_user(client)

    assert response.status_code == 200

    user = db.session.scalar(
        db.select(User).where(
            User.email == TEST_USER["email"]
        )
    )

    assert user is not None
    assert user.username == TEST_USER["username"]


# 4. Перевірка хешування пароля
def test_password_hashing(client):
    register_user(client)

    user = db.session.scalar(
        db.select(User).where(
            User.email == TEST_USER["email"]
        )
    )

    assert user.password != TEST_USER["password"]
    assert user.password.startswith("$2b$")
    assert user.check_password(TEST_USER["password"])
    assert not user.check_password("WrongPassword")


# 5. Перевірка повторної реєстрації
def test_duplicate_registration(client):
    register_user(client)

    response = register_user(client)
    html = response.get_data(as_text=True)

    assert "вже зайняте" in html
    assert "вже використовується" in html

    users = db.session.scalars(
        db.select(User)
    ).all()

    assert len(users) == 1


# 6. Перевірка підтвердження пароля
def test_password_confirmation(client):
    data = TEST_USER.copy()
    data["confirm_password"] = "DifferentPassword"

    response = client.post(
        "/register",
        data=data,
        follow_redirects=True,
    )

    assert "Паролі не збігаються" in response.get_data(
        as_text=True
    )

    users = db.session.scalars(
        db.select(User)
    ).all()

    assert len(users) == 0


# 7. Успішний вхід
def test_successful_login(client):
    register_user(client)

    response = login_test_user(client)

    assert response.status_code == 200
    assert response.request.path == "/account"
    assert "LabTest" in response.get_data(as_text=True)

    with client.session_transaction() as session:
        assert "_user_id" in session


# 8. Вхід із неправильним паролем
def test_invalid_login(client):
    register_user(client)

    response = login_test_user(
        client,
        password="WrongPassword",
    )

    assert "Неправильна електронна пошта або пароль" in (
        response.get_data(as_text=True)
    )

    with client.session_transaction() as session:
        assert "_user_id" not in session


# 9. Захист сторінок від неавторизованих користувачів
def test_protected_pages(client):
    for path in ["/account", "/profile", "/users"]:
        response = client.get(path)

        assert response.status_code == 302
        assert "/login" in response.location


# 10. Доступ авторизованого користувача
def test_authenticated_access(client):
    register_user(client)
    login_test_user(client)

    response = client.get("/account")
    assert response.status_code == 200

    response = client.get("/users")
    assert response.status_code == 200


# 11. Перенаправлення авторизованого користувача
def test_authenticated_redirect(client):
    register_user(client)
    login_test_user(client)

    for path in ["/register", "/login"]:
        response = client.get(path)

        assert response.status_code == 302
        assert "/account" in response.location


# 12. Вихід із системи
def test_logout(client):
    register_user(client)
    login_test_user(client)

    response = client.get(
        "/logout",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert response.request.path == "/login"

    with client.session_transaction() as session:
        assert "_user_id" not in session

    response = client.get("/account")

    assert response.status_code == 302
    assert "/login" in response.location
