
import os
import io

import pytest

os.environ["TEST_DATABASE_URI"] = "sqlite:///:memory:"

from app import app, db
from app.users.models import User
from app.posts.models import Post, Comment, Like
from app.posts.utils import render_markdown, save_image
from app.notifications import notify_follow


@pytest.fixture
def client(monkeypatch):

    monkeypatch.setitem(app.config, "TESTING", True)
    monkeypatch.setitem(app.config, "WTF_CSRF_ENABLED", False)
    monkeypatch.setitem(app.config, "MAIL_ENABLED", False)

    with app.app_context():

        assert db.engine.url.database == ":memory:"

        db.create_all()

        alice = User(
            username="Alice",
            email="alice@example.com",
            is_admin=False
        )
        alice.set_password("Password123")

        bob = User(
            username="Bob",
            email="bob@example.com",
            is_admin=False
        )
        bob.set_password("Password123")

        admin = User(
            username="Admin",
            email="admin@example.com",
            is_admin=True
        )
        admin.set_password("Password123")

        db.session.add_all([alice, bob, admin])
        db.session.commit()

        post = Post(
            title="Python Test Post",
            content="Test publication content",
            category="tech",
            user_id=bob.id,
            is_active=True
        )

        db.session.add(post)
        db.session.commit()

        with app.test_client() as test_client:
            yield test_client

        db.session.remove()
        db.drop_all()


def login(client, user_id=1):

    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True


def post_data(title="New Test Post"):

    return {
        "title": title,
        "content": "New publication content",
        "category": "tech",
        "posted": "2026-11-28T12:00",
        "is_active": "y"
    }


# 1. Public feed

def test_public_feed(client):
    response = client.get("/post/")
    assert response.status_code == 200
    assert b"Python Test Post" in response.data


# 2. Post details

def test_post_details(client):
    response = client.get("/post/1")
    assert response.status_code == 200
    assert b"Test publication content" in response.data


# 3. Authentication required

def test_create_requires_login(client):
    response = client.get("/post/create")
    assert response.status_code == 302


# 4. Create post

def test_create_post(client):
    login(client)

    response = client.post(
        "/post/create",
        data=post_data()
    )

    assert response.status_code == 302

    post = db.session.scalar(
        db.select(Post).where(
            Post.title == "New Test Post"
        )
    )

    assert post is not None
    assert post.user_id == 1


# 5. Update post

def test_update_post(client):
    login(client, 2)

    response = client.post(
        "/post/1/update",
        data=post_data("Updated Post")
    )

    assert response.status_code == 302
    assert db.session.get(Post, 1).title == "Updated Post"


# 6. Delete post

def test_delete_post(client):
    login(client, 2)

    response = client.post("/post/1/delete")

    assert response.status_code == 302
    assert db.session.get(Post, 1) is None


# 7. Post ownership

def test_cannot_edit_other_post(client):
    login(client, 1)

    response = client.get("/post/1/update")

    assert response.status_code == 403


# 8. Add comment

def test_add_comment(client):
    login(client)

    response = client.post(
        "/post/1/comment",
        data={"content": "Test comment"}
    )

    assert response.status_code == 302

    comment = db.session.scalar(
        db.select(Comment)
    )

    assert comment.content == "Test comment"
    assert comment.user_id == 1


# 9. Edit comment

def test_edit_comment(client):
    login(client)

    client.post(
        "/post/1/comment",
        data={"content": "Old comment"}
    )

    response = client.post(
        "/post/comment/1/edit",
        data={"content": "Updated comment"}
    )

    assert response.status_code == 302
    assert db.session.get(Comment, 1).content == "Updated comment"


# 10. Delete comment

def test_delete_comment(client):
    login(client)

    client.post(
        "/post/1/comment",
        data={"content": "Delete me"}
    )

    response = client.post(
        "/post/comment/1/delete"
    )

    assert response.status_code == 302
    assert db.session.get(Comment, 1) is None


# 11. Comment ownership

def test_comment_permissions(client):
    login(client, 1)

    response = client.post(
        "/post/1/comment",
        data={"content": "Private action"}
    )

    assert response.status_code == 302

    comment = db.session.get(Comment, 1)

    assert comment is not None
    assert comment.user_id == 1

    # Використовуємо окремий контекст
    # та клієнт для другого користувача.
    with app.app_context():
        with app.test_client() as second_client:

            login(second_client, 2)

            response = second_client.post(
                "/post/comment/1/delete"
            )

            assert response.status_code == 403

        assert db.session.get(Comment, 1) is not None


# 12. Like and unlike

def test_toggle_like(client):
    login(client)

    response = client.post("/post/1/like")

    assert response.status_code == 302
    assert db.session.get(Like, (1, 1)) is not None

    client.post("/post/1/like")

    assert db.session.get(Like, (1, 1)) is None


# 13. Follow and unfollow

def test_toggle_follow(client):
    login(client)

    response = client.post("/user/2/follow")

    assert response.status_code == 302

    alice = db.session.get(User, 1)
    bob = db.session.get(User, 2)

    assert bob in alice.following

    client.post("/user/2/follow")

    assert bob not in alice.following


# 14. Self-follow protection

def test_cannot_follow_self(client):
    login(client)

    response = client.post("/user/1/follow")

    assert response.status_code == 400


# 15. Personal feed

def test_personal_feed(client):
    login(client)

    response = client.get("/post/feed")

    assert b"Python Test Post" not in response.data

    client.post("/user/2/follow")

    response = client.get("/post/feed")

    assert response.status_code == 200
    assert b"Python Test Post" in response.data


# 16. Post search

def test_post_search(client):
    response = client.get("/post/?q=Python")

    assert response.status_code == 200
    assert b"Python Test Post" in response.data

    response = client.get("/post/?q=UnknownXYZ")

    assert b"Python Test Post" not in response.data


# 17. User search

def test_user_search(client):
    login(client)

    response = client.get("/users?q=Bob")

    assert response.status_code == 200
    assert b"Bob" in response.data


# 18. Profile editing

def test_edit_profile(client):
    login(client)

    response = client.post(
        "/account/edit",
        data={
            "full_name": "Alice Example",
            "bio": "Software developer"
        }
    )

    assert response.status_code == 302

    user = db.session.get(User, 1)

    assert user.full_name == "Alice Example"
    assert user.bio == "Software developer"


# 19. Pagination

def test_pagination(client):

    for number in range(8):
        db.session.add(
            Post(
                title=f"Pagination Post {number}",
                content="Pagination test content",
                category="tech",
                user_id=2,
                is_active=True
            )
        )

    db.session.commit()

    response = client.get("/post/?page=2")

    assert response.status_code == 200
    assert b"Pagination Post" in response.data


# 20. Admin access

def test_admin_access(client):
    login(client, 3)

    response = client.get("/management/")

    assert response.status_code == 200


# 21. Admin access protection

def test_admin_forbidden(client):
    login(client, 1)

    response = client.get("/management/")

    assert response.status_code == 403


# 22. Admin moderation

def test_admin_hide_post(client):
    login(client, 3)

    response = client.post(
        "/management/posts/1/status"
    )

    assert response.status_code == 302
    assert db.session.get(Post, 1).is_active is False


# 23. Hidden post protection

def test_hidden_post(client):
    post = db.session.get(Post, 1)
    post.is_active = False

    db.session.commit()

    response = client.get("/post/1")

    assert response.status_code == 404


# 24. CSRF protection

def test_csrf_protection(client, monkeypatch):
    login(client)

    monkeypatch.setitem(
        app.config,
        "WTF_CSRF_ENABLED",
        True
    )

    response = client.post("/post/1/like")

    assert response.status_code == 400
    assert db.session.get(Like, (1, 1)) is None


# 25. Markdown formatting

def test_markdown_formatting(client):
    result = render_markdown("**Bold text**")

    assert "<strong>Bold text</strong>" in result


# 26. XSS protection

def test_xss_protection(client):
    result = render_markdown(
        '<script>alert("XSS")</script>'
    )

    assert "<script>" not in result


# 27. Invalid image

def test_invalid_image(client):
    from werkzeug.datastructures import FileStorage

    file = FileStorage(
        stream=io.BytesIO(b"Not a real image"),
        filename="fake.jpg",
        content_type="image/jpeg"
    )

    with pytest.raises(ValueError):
        save_image(file)


# 28. Email notification

def test_email_notification(client, monkeypatch):

    messages = []

    def fake_send(recipient, subject, body):
        messages.append((recipient, subject, body))
        return True

    monkeypatch.setattr(
        "app.notifications.send_notification",
        fake_send
    )

    alice = db.session.get(User, 1)
    bob = db.session.get(User, 2)

    assert notify_follow(bob, alice) is True

    assert len(messages) == 1
    assert messages[0][0] == bob.email
    assert "Alice" in messages[0][2]


# 29. Custom error page

def test_custom_404(client):
    response = client.get("/nonexistent-page")

    assert response.status_code == 404
    assert b"SocialSpace" in response.data


# 30. Password hashing

def test_password_hashing(client):
    user = db.session.get(User, 1)

    assert user.password != "Password123"
    assert user.check_password("Password123")
    assert not user.check_password("WrongPassword")
