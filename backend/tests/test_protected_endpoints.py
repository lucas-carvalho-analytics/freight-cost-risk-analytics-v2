from sqlalchemy import select

from app.models.audit_log import AuditLog


def test_kpi_endpoint_with_valid_token_returns_aggregated_data(
    client,
    test_user,
    auth_headers,
    sample_shipments,
    db_session,
) -> None:
    response = client.get("/api/v1/kpis/frete-total", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["metric"] == "frete_total"
    assert body["value"] == 600.0
    assert body["shipment_count"] == 3

    audit_log = db_session.execute(
        select(AuditLog).where(AuditLog.action == "kpi_access_success")
    ).scalar_one()
    assert audit_log.endpoint == "/api/v1/kpis/frete-total"
    assert audit_log.user_id == test_user.id


def test_kpi_endpoint_without_token_returns_401(client, sample_shipments) -> None:
    response = client.get("/api/v1/kpis/frete-total")

    assert response.status_code == 401
    assert response.json() == {
        "error": "http_error",
        "message": "Not authenticated.",
        "status_code": 401,
    }


def test_filter_endpoint_with_valid_token_returns_filtered_options(
    client,
    auth_headers,
    sample_shipments,
) -> None:
    response = client.get(
        "/api/v1/filtros/destinos?origem=Suape&destino=Fábrica Recife/PE",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            "Fábrica Caruaru/PE",
            "Fábrica Recife/PE",
        ]
    }
