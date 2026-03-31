def test_health_endpoint_returns_ok(client) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_endpoint_returns_ready_and_database_check(client) -> None:
    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "freight_cost_risk_analytics",
        "version": "0.1.0",
        "checks": {
            "database": "ok",
        },
    }


def test_health_endpoints_include_request_id_header(client) -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "req-health-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-health-123"
