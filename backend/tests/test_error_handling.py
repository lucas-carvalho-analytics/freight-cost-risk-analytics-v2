def test_validation_error_returns_standardized_response(client) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "invalid-email", "password": "Admin123!"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "validation_error"
    assert body["message"] == "Request validation failed."
    assert body["status_code"] == 422
    assert isinstance(body["details"], list)


def test_not_found_returns_standardized_response(client) -> None:
    response = client.get("/api/v1/rota-inexistente")

    assert response.status_code == 404
    assert response.json() == {
        "error": "http_error",
        "message": "Not Found",
        "status_code": 404,
    }


def test_internal_server_error_returns_standardized_response(
    client,
    internal_error_route,
) -> None:
    response = client.get(internal_error_route)

    assert response.status_code == 500
    assert response.json() == {
        "error": "internal_server_error",
        "message": "Internal server error.",
        "status_code": 500,
    }
