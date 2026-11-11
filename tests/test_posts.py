
import pytest

from app import create_app, db
from app.posts.models import Post


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def create_test_post(
    title="Test Post",
    content="Test post content",
    category="tech",
    is_active=True,
):
    post = Post(
        title=title,
        content=content,
        category=category,
        is_active=is_active,
    )

    db.session.add(post)
    db.session.commit()

    return post


def test_create_post(client, app):
    response = client.post(
        "/post/create",
        data={
            "title": "New Post",
            "content": "This is a new post",
            "category": "news",
            "enabled": "y",
            "publish_date": "2026-11-11T12:00",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        post = db.session.scalar(
            db.select(Post).where(
                Post.title == "New Post"
            )
        )

        assert post is not None
        assert post.category == "news"
        assert post.author == "Anonymous"
        assert post.is_active is True


def test_get_all_posts(client, app):
    with app.app_context():
        create_test_post()

    response = client.get("/post")

    assert response.status_code == 200
    assert b"Test Post" in response.data


def test_get_post_details(client, app):
    with app.app_context():
        post = create_test_post()
        post_id = post.id

    response = client.get(
        f"/post/{post_id}"
    )

    assert response.status_code == 200
    assert b"Test post content" in response.data


def test_update_post(client, app):
    with app.app_context():
        post = create_test_post()
        post_id = post.id

    response = client.post(
        f"/post/{post_id}/update",
        data={
            "title": "Updated Post",
            "content": "Updated post content",
            "category": "publication",
            "enabled": "y",
            "publish_date": "2026-11-11T14:00",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        updated = db.session.get(Post, post_id)

        assert updated.title == "Updated Post"
        assert updated.content == "Updated post content"
        assert updated.category == "publication"


def test_delete_post(client, app):
    with app.app_context():
        post = create_test_post()
        post_id = post.id

    response = client.post(
        f"/post/{post_id}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        assert db.session.get(Post, post_id) is None


def test_delete_confirmation(client, app):
    with app.app_context():
        post = create_test_post()
        post_id = post.id

    response = client.get(
        f"/post/{post_id}/delete"
    )

    assert response.status_code == 200
    assert b"Test Post" in response.data

    with app.app_context():
        assert db.session.get(Post, post_id) is not None


def test_inactive_post_hidden(client, app):
    with app.app_context():
        create_test_post(
            title="Hidden Post",
            is_active=False,
        )

    response = client.get("/post")

    assert response.status_code == 200
    assert b"Hidden Post" not in response.data


def test_invalid_post_title(client, app):
    response = client.post(
        "/post/create",
        data={
            "title": "A",
            "content": "Valid content",
            "category": "tech",
            "enabled": "y",
            "publish_date": "2026-11-11T12:00",
        },
    )

    assert response.status_code == 200

    with app.app_context():
        posts = db.session.scalars(
            db.select(Post)
        ).all()

        assert len(posts) == 0


def test_post_not_found(client):
    response = client.get("/post/99999")

    assert response.status_code == 404


def test_create_post_form(client):
    response = client.get("/post/create")

    assert response.status_code == 200
    assert b'name="title"' in response.data
    assert b'name="content"' in response.data
