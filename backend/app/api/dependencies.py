from datetime import date

from fastapi import Query

from app.services.shipment_analytics import ShipmentFilterParams, build_filter_params


def get_shipment_filters(
    data_inicio: date | None = Query(default=None),
    data_fim: date | None = Query(default=None),
    origem: str | None = Query(default=None),
    destino: str | None = Query(default=None),
    transportadora: str | None = Query(default=None),
    tipo_veiculo: str | None = Query(default=None),
    ocorrencia: str | None = Query(default=None),
) -> ShipmentFilterParams:
    return build_filter_params(
        data_inicio=data_inicio,
        data_fim=data_fim,
        origem=origem,
        destino=destino,
        transportadora=transportadora,
        tipo_veiculo=tipo_veiculo,
        ocorrencia=ocorrencia,
    )
