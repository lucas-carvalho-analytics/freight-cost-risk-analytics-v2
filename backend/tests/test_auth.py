from sqlalchemy import select

from app.models.audit_log import AuditLog


def test_login_with_valid_credentials_returns_access_token(client, test_user) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "Admin123!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 3600
    assert "access_token" in body


def test_login_with_invalid_credentials_returns_401(client, test_user) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials."


def test_auth_me_with_valid_token_returns_current_user(client, test_user, auth_headers) -> None:
    response = client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == test_user.email
    assert body["full_name"] == test_user.full_name
    assert body["is_active"] is True


def test_auth_me_without_token_returns_401(client) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated."


def test_auth_me_with_invalid_token_returns_401(client) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token."


def test_login_registers_audit_log(client, test_user, db_session) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "Admin123!"},
    )

    assert response.status_code == 200

    log = db_session.execute(
        select(AuditLog).where(AuditLog.action == "login_success")
    ).scalar_one()
    assert log.endpoint == "/api/v1/auth/login"
    assert log.user_id == test_user.id
