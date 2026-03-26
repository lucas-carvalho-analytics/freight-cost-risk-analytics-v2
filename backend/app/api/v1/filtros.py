from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_shipment_filters
from app.auth.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.shipment import Shipment
from app.models.user import User
from app.schemas.kpis import FilterValuesResponse
from app.services.shipment_analytics import (
    ShipmentFilterParams,
    fetch_distinct_values,
    without_filter,
)


router = APIRouter(prefix="/filtros")


@router.get("/origens", response_model=FilterValuesResponse)
def get_origens(
    filters: ShipmentFilterParams = Depends(get_shipment_filters),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> FilterValuesResponse:
    _ = current_user
    return FilterValuesResponse(
        items=fetch_distinct_values(
            db,
            Shipment.origem,
            without_filter(filters, "origem"),
        )
    )


@router.get("/destinos", response_model=FilterValuesResponse)
def get_destinos(
    filters: ShipmentFilterParams = Depends(get_shipment_filters),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> FilterValuesResponse:
    _ = current_user
    return FilterValuesResponse(
        items=fetch_distinct_values(
            db,
            Shipment.destino,
            without_filter(filters, "destino"),
        )
    )


@router.get("/transportadoras", response_model=FilterValuesResponse)
def get_transportadoras(
    filters: ShipmentFilterParams = Depends(get_shipment_filters),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> FilterValuesResponse:
    _ = current_user
    return FilterValuesResponse(
        items=fetch_distinct_values(
            db,
            Shipment.transportadora,
            without_filter(filters, "transportadora"),
        )
    )


@router.get("/tipos-veiculo", response_model=FilterValuesResponse)
def get_tipos_veiculo(
    filters: ShipmentFilterParams = Depends(get_shipment_filters),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> FilterValuesResponse:
    _ = current_user
    return FilterValuesResponse(
        items=fetch_distinct_values(
            db,
            Shipment.tipo_veiculo,
            without_filter(filters, "tipo_veiculo"),
        )
    )
