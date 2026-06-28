from datetime import timedelta

from app.core.security import create_access_token
from app.models.user import User
from app.core.security import get_password_hash


def test_public_endpoints_do_not_require_token(unauthenticated_client):
    assert unauthenticated_client.get("/").status_code == 200
    assert unauthenticated_client.get("/health").status_code == 200

    register = unauthenticated_client.post("/api/v1/users/", json={
        "email": "public@example.com",
        "password": "PublicPass123!",
    })
    assert register.status_code == 200

    login = unauthenticated_client.post("/api/v1/users/login", json={
        "email": "public@example.com",
        "password": "PublicPass123!",
    })
    assert login.status_code == 200
    assert login.json()["data"]["token_type"] == "bearer"


def test_protected_business_endpoint_requires_bearer_token(unauthenticated_client):
    response = unauthenticated_client.get("/api/v1/projects/")

    assert response.status_code == 401
    assert response.json()["detail"] == "认证凭据无效或已过期"


def test_protected_business_endpoint_rejects_raw_token(unauthenticated_client, auth_headers):
    raw_token = auth_headers["Authorization"].removeprefix("Bearer ")
    response = unauthenticated_client.get("/api/v1/projects/", headers={"Authorization": raw_token})

    assert response.status_code == 401


def test_protected_business_endpoint_rejects_invalid_token(unauthenticated_client):
    response = unauthenticated_client.get("/api/v1/projects/", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401


def test_protected_business_endpoint_rejects_expired_token(unauthenticated_client, create_user_via_api):
    created = create_user_via_api(email="expired@example.com", password="ExpiredPass123!")
    user_id = created.json()["data"]["id"]
    token = create_access_token(subject=str(user_id), expires_delta=timedelta(seconds=-1))

    response = unauthenticated_client.get("/api/v1/projects/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_protected_business_endpoint_accepts_valid_token(unauthenticated_client, auth_headers):
    response = unauthenticated_client.get("/api/v1/projects/", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["code"] == 0


def test_admin_endpoint_rejects_normal_user(unauthenticated_client, auth_headers):
    response = unauthenticated_client.get("/api/v1/users/", headers=auth_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "需要管理员权限"


def test_admin_endpoint_accepts_admin_user(unauthenticated_client, db):
    admin = User(
        email="admin-auth@example.com",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="认证管理员",
        is_active=True,
        is_superuser=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    login = unauthenticated_client.post("/api/v1/users/login", json={
        "email": "admin-auth@example.com",
        "password": "AdminPass123!",
    })
    token = login.json()["data"]["access_token"]

    response = unauthenticated_client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["code"] == 0