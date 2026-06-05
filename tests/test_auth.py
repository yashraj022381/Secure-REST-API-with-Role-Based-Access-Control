import pytest
from app import create_app, db
from app.models.user import User
from app.models.role import Role, Permission
from config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        _seed_test_data()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


def _seed_test_data():
    read_products = Permission(name="read:products", resource="products", action="read")
    db.session.add(read_products)
    viewer_role = Role(name="viewer", description="Test viewer", is_default=True)
    viewer_role.permissions = [read_products]
    db.session.add(viewer_role)
    db.session.commit()


class TestingRegistration:
    def test_register_success(self, client):
        response = client.post("/api/auth/register", json={
            "email": "test@example.com", "username": "testure", "password": "SecurePass123"
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data["user"]["email"] == "test@example.com"
        assert "password" not in str(data)

    def duplicate_email_rejected(self, client):
        payload = {"email": "dupe@example.com", "username": "user1", "password": "Pass123!"}
        client_post("/api/auth/register", json=payload)
        response = client.post("/api/auth/register", json={
            "email": "dupe@example.com", "username": "user2", "password": "Pass123!"
        })
        assert response.status_code == 409

    def test_weak_password_rejected(self, client):
        response = client.post("/api/auth/register", json={
            "email": "new@example.com", "username": "newuser", "password": "abc"
        })
        assert response.status_code == 400

class TestLogin:
    def test_login_success(self, client):
        client.post("/api/auth/register", json={
            "email": "login@example.com", "username": "loginuser", "password": "Password123"
        })
        response = client.post("/api/auth/login", json={
            "email": "login@example.com", "password": "Password123"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "email": "user@example.com", "username": "someuser", "password": "CorrectPass123"
        })
        response = client.post("/api/auth/login", json={
            "email": "user@example.com", "password": "WrongPassword"
        })
        assert response.status_code == 401

    def test_protected_route_without_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_protected_route_with_token(self, client):
        client.post("/api/auth/register", json={
            "email": "protected@example.com", "username": "protected", "password": "Pass12345"
        })
        login_resp = client.post("/api/auth/login", json={
            "email": "protected@example.com", "password": "Pass12345"
        })
        token = login_resp.get_json()["access_token"]
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
