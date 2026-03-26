from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.shipment import Shipment


@dataclass(slots=True)
class ShipmentFilterParams:
    data_inicio: date | None = None
    data_fim: date | None = None
    origem: str | None = None
    destino: str | None = None
    transportadora: str | None = None
    tipo_veiculo: str | None = None
    ocorrencia: str | None = None


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_occurrence(value: str | None) -> str | None:
    normalized = _normalize_text(value)
    if normalized is None:
        return None
    normalized_key = normalized.casefold()
    if normalized_key == "ok":
        return "OK"
    if normalized_key == "atraso":
        return "Atraso"
    if normalized_key == "sinistro":
        return "Sinistro"
    return normalized


def build_filter_params(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    origem: str | None = None,
    destino: str | None = None,
    transportadora: str | None = None,
    tipo_veiculo: str | None = None,
    ocorrencia: str | None = None,
) -> ShipmentFilterParams:
    return ShipmentFilterParams(
        data_inicio=data_inicio,
        data_fim=data_fim,
        origem=_normalize_text(origem),
        destino=_normalize_text(destino),
        transportadora=_normalize_text(transportadora),
        tipo_veiculo=_normalize_text(tipo_veiculo),
        ocorrencia=_normalize_occurrence(ocorrencia),
    )


def apply_shipment_filters(statement, filters: ShipmentFilterParams):
    conditions = []

    if filters.data_inicio is not None:
        conditions.append(Shipment.data_embarque >= filters.data_inicio)
    if filters.data_fim is not None:
        conditions.append(Shipment.data_embarque <= filters.data_fim)
    if filters.origem is not None:
        conditions.append(Shipment.origem == filters.origem)
    if filters.destino is not None:
        conditions.append(Shipment.destino == filters.destino)
    if filters.transportadora is not None:
        conditions.append(Shipment.transportadora == filters.transportadora)
    if filters.tipo_veiculo is not None:
        conditions.append(Shipment.tipo_veiculo == filters.tipo_veiculo)
    if filters.ocorrencia is not None:
        conditions.append(Shipment.ocorrencia == filters.ocorrencia)

    if conditions:
        statement = statement.where(*conditions)

    return statement


def without_filter(
    filters: ShipmentFilterParams,
    field_name: str,
) -> ShipmentFilterParams:
    return replace(filters, **{field_name: None})


def decimal_to_float(value: Decimal | float | int | None) -> float:
    if value is None:
        return 0.0
    return round(float(value), 2)


def fetch_total_sum(
    db: Session,
    column,
    filters: ShipmentFilterParams,
) -> tuple[float, int]:
    statement = select(
        func.coalesce(func.sum(column), 0),
        func.count(Shipment.id),
    )
    statement = apply_shipment_filters(statement, filters)
    total_value, shipment_count = db.execute(statement).one()
    return decimal_to_float(total_value), int(shipment_count or 0)


def fetch_occurrence_rate(
    db: Session,
    filters: ShipmentFilterParams,
) -> tuple[int, int, float]:
    statement = select(
        func.count(Shipment.id),
        func.coalesce(
            func.sum(case((Shipment.tem_ocorrencia.is_(True), 1), else_=0)),
            0,
        ),
    )
    statement = apply_shipment_filters(statement, filters)
    total_shipments, shipments_com_ocorrencia = db.execute(statement).one()

    total_shipments = int(total_shipments or 0)
    shipments_com_ocorrencia = int(shipments_com_ocorrencia or 0)
    taxa_ocorrencias_pct = 0.0
    if total_shipments:
        taxa_ocorrencias_pct = round(
            (shipments_com_ocorrencia / total_shipments) * 100,
            2,
        )

    return total_shipments, shipments_com_ocorrencia, taxa_ocorrencias_pct


def fetch_cost_by_carrier(
    db: Session,
    filters: ShipmentFilterParams,
) -> list[dict[str, float | int | str]]:
    statement = select(
        Shipment.transportadora,
        func.avg(Shipment.frete_peso),
        func.count(Shipment.id),
    ).group_by(Shipment.transportadora).order_by(Shipment.transportadora)
    statement = apply_shipment_filters(statement, filters)

    rows = db.execute(statement).all()
    return [
        {
            "transportadora": row[0],
            "custo_medio_frete": decimal_to_float(row[1]),
            "quantidade_shipments": int(row[2]),
        }
        for row in rows
    ]


def fetch_risk_by_destination(
    db: Session,
    filters: ShipmentFilterParams,
) -> list[dict[str, float | int | str]]:
    statement = select(
        Shipment.destino,
        func.avg(Shipment.frete_peso),
        func.avg(case((Shipment.tem_ocorrencia.is_(True), 1.0), else_=0.0)),
        func.count(Shipment.id),
    ).group_by(Shipment.destino).order_by(Shipment.destino)
    statement = apply_shipment_filters(statement, filters)

    rows = db.execute(statement).all()
    if not rows:
        return []

    average_costs = [decimal_to_float(row[1]) for row in rows]
    occurrence_rates = [float(row[2] or 0.0) for row in rows]
    max_average_cost = max(average_costs, default=0.0)
    max_occurrence_rate = max(occurrence_rates, default=0.0)

    items: list[dict[str, float | int | str]] = []
    for row, average_cost, occurrence_rate in zip(rows, average_costs, occurrence_rates):
        normalized_cost = average_cost / max_average_cost if max_average_cost else 0.0
        normalized_occurrence_rate = (
            occurrence_rate / max_occurrence_rate if max_occurrence_rate else 0.0
        )
        score_risco = round(
            (normalized_cost * 0.4) + (normalized_occurrence_rate * 0.6),
            4,
        )

        items.append(
            {
                "destino": row[0],
                "custo_medio": average_cost,
                "taxa_ocorrencia_pct": round(occurrence_rate * 100, 2),
                "score_risco": score_risco,
                "quantidade_shipments": int(row[3]),
            }
        )

    return items


def fetch_distinct_values(
    db: Session,
    column,
    filters: ShipmentFilterParams,
) -> list[str]:
    statement = select(column).distinct().order_by(column)
    statement = apply_shipment_filters(statement, filters)

    return [
        value
        for value in db.scalars(statement).all()
        if value is not None and str(value).strip()
    ]
