export interface KpiTotalResponse {
  metric: string
  value: number
  shipment_count: number
}

export interface OccurrenceRateResponse {
  total_shipments: number
  shipments_com_ocorrencia: number
  taxa_ocorrencias_pct: number
}

export interface DashboardKpis {
  freightTotal: KpiTotalResponse
  adValoremTotal: KpiTotalResponse
  occurrenceRate: OccurrenceRateResponse
}

export interface CarrierCostItem {
  transportadora: string
  custo_medio_frete: number
  quantidade_shipments: number
}

export interface CarrierCostResponse {
  items: CarrierCostItem[]
}

export interface DestinationRiskItem {
  destino: string
  custo_medio: number
  taxa_ocorrencia_pct: number
  score_risco: number
  quantidade_shipments: number
}

export interface DestinationRiskResponse {
  items: DestinationRiskItem[]
}

export interface DashboardAnalytics {
  kpis: DashboardKpis
  carrierCost: CarrierCostItem[]
  destinationRisk: DestinationRiskItem[]
}
