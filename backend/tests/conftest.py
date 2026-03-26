import os
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")

from app.auth.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Shipment, User


@pytest.fixture
def db_engine(tmp_path):
    database_path = tmp_path / "test_suite.db"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def session_local(db_engine):
    return sessionmaker(
        bind=db_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )


@pytest.fixture
def db_session(session_local) -> Session:
    session = session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(session_local) -> TestClient:
    def override_get_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    user = User(
        email="admin@example.com",
        full_name="Admin",
        password_hash=hash_password("Admin123!"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def access_token(test_user: User) -> str:
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def sample_shipments(db_session: Session) -> list[Shipment]:
    shipments = [
        Shipment(
            data_embarque=date(2024, 1, 10),
            origem="Suape",
            destino="Fábrica Recife/PE",
            valor_carga=Decimal("10000.00"),
            tipo_veiculo="Truck",
            transportadora="Belmont-Alpha",
            taxa_ad_valorem_pct=Decimal("1.00"),
            frete_peso=Decimal("100.00"),
            ocorrencia="OK",
            tem_ocorrencia=False,
            ad_valorem=Decimal("100.00"),
        ),
        Shipment(
            data_embarque=date(2024, 1, 11),
            origem="Suape",
            destino="Fábrica Caruaru/PE",
            valor_carga=Decimal("12000.00"),
            tipo_veiculo="Truck",
            transportadora="Belmont-Alpha",
            taxa_ad_valorem_pct=Decimal("1.00"),
            frete_peso=Decimal("200.00"),
            ocorrencia="Atraso",
            tem_ocorrencia=True,
            ad_valorem=Decimal("120.00"),
        ),
        Shipment(
            data_embarque=date(2024, 1, 12),
            origem="Jaboatão",
            destino="Fábrica João Pessoa/PB",
            valor_carga=Decimal("15000.00"),
            tipo_veiculo="Van",
            transportadora="Trans-X",
            taxa_ad_valorem_pct=Decimal("1.00"),
            frete_peso=Decimal("300.00"),
            ocorrencia="Sinistro",
            tem_ocorrencia=True,
            ad_valorem=Decimal("150.00"),
        ),
    ]
    db_session.add_all(shipments)
    db_session.commit()
    return shipments


@pytest.fixture
def internal_error_route():
    def raise_internal_error():
        raise RuntimeError("simulated internal error")

    route_path = "/api/v1/test/internal-error"
    app.router.add_api_route(route_path, raise_internal_error, methods=["GET"])

    try:
        yield route_path
    finally:
        app.router.routes = [
            route for route in app.router.routes if getattr(route, "path", None) != route_path
        ]
