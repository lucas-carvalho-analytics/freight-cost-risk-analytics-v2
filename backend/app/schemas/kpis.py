from pydantic import BaseModel


class KpiTotalResponse(BaseModel):
    metric: str
    value: float
    shipment_count: int


class OccurrenceRateResponse(BaseModel):
    total_shipments: int
    shipments_com_ocorrencia: int
    taxa_ocorrencias_pct: float


class CarrierCostItem(BaseModel):
    transportadora: str
    custo_medio_frete: float
    quantidade_shipments: int


class CarrierCostResponse(BaseModel):
    items: list[CarrierCostItem]


class DestinationRiskItem(BaseModel):
    destino: str
    custo_medio: float
    taxa_ocorrencia_pct: float
    score_risco: float
    quantidade_shipments: int


class DestinationRiskResponse(BaseModel):
    items: list[DestinationRiskItem]


class FilterValuesResponse(BaseModel):
    items: list[str]
