from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_shipment_filters
from app.auth.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.shipment import Shipment
from app.models.user import User
from app.schemas.kpis import (
    CarrierCostResponse,
    DestinationRiskResponse,
    KpiTotalResponse,
    OccurrenceRateResponse,
)
from app.services.shipment_analytics import (
    ShipmentFilterParams,
    fetch_cost_by_carrier,
    fetch_occurrence_rate,
    fetch_risk_by_destination,
    fetch_total_sum,
)


router = APIRouter(prefix="/kpis")


def register_kpi_access(
    db: Session,
    user_id: int,
    endpoint: str,
) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            action="kpi_access_success",
            endpoint=endpoint,
        )
    )
    db.commit()


@router.get("/frete-total", response_model=KpiTotalResponse)
def get_frete_total(
    filters: ShipmentFilterParams = Depends(get_shipment_filters),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> KpiTotalResponse:
    value, shipment_count = fetch_total_sum(db, Shipment.frete_peso, filters)
    register_kpi_access(db, current_user.id, "/api/v1/kpis/frete-total")
    return KpiTotalResponse(
        metric="frete_total",
        value=value,
        shipment_count=shipment_count,
    )


@router.get("/advalorem-total", response_model=KpiTotalResponse)
def get_advalorem_total(
    filters: ShipmentFilterParams = Depends(get_shipment_filters),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> KpiTotalResponse:
    value, shipment_count = fetch_total_sum(db, Shipment.ad_valorem, filters)
    register_kpi_access(db, current_user.id, "/api/v1/kpis/advalorem-total")
    return KpiTotalResponse(
        metric="advalorem_total",
        value=value,
        shipment_count=shipment_count,
    )


@router.get("/taxa-ocorrencias", response_model=OccurrenceRateResponse)
def get_taxa_ocorrencias(
    filters: ShipmentFilterParams = Depends(get_shipment_filters),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> OccurrenceRateResponse:
    total_shipments, shipments_com_ocorrencia, taxa_ocorrencias_pct = (
        fetch_occurrence_rate(db, filters)
    )
    register_kpi_access(db, current_user.id, "/api/v1/kpis/taxa-ocorrencias")
    return OccurrenceRateResponse(
        total_shipments=total_shipments,
        shipments_com_ocorrencia=shipments_com_ocorrencia,
        taxa_ocorrencias_pct=taxa_ocorrencias_pct,
    )


@router.get("/custo-por-transportadora", response_model=CarrierCostResponse)
def get_custo_por_transportadora(
    filters: ShipmentFilterParams = Depends(get_shipment_filters),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> CarrierCostResponse:
    items = fetch_cost_by_carrier(db, filters)
    register_kpi_access(
        db,
        current_user.id,
        "/api/v1/kpis/custo-por-transportadora",
    )
    return CarrierCostResponse(items=items)


@router.get("/custo-risco-destino", response_model=DestinationRiskResponse)
def get_custo_risco_destino(
    filters: ShipmentFilterParams = Depends(get_shipment_filters),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> DestinationRiskResponse:
    items = fetch_risk_by_destination(db, filters)
    register_kpi_access(db, current_user.id, "/api/v1/kpis/custo-risco-destino")
    return DestinationRiskResponse(items=items)
