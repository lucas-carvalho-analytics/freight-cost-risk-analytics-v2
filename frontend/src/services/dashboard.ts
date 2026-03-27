import { api } from './api'
import type {
  CarrierCostResponse,
  DashboardAnalytics,
  DashboardKpis,
  DestinationRiskResponse,
  KpiTotalResponse,
  OccurrenceRateResponse,
} from '../types/dashboard'
import type { DashboardFilters, FilterOptions } from '../types/filters'

function buildFilterParams(filters: DashboardFilters): URLSearchParams {
  const params = new URLSearchParams()

  if (filters.dataInicio) {
    params.set('data_inicio', filters.dataInicio)
  }
  if (filters.dataFim) {
    params.set('data_fim', filters.dataFim)
  }
  if (filters.origem) {
    params.set('origem', filters.origem)
  }
  if (filters.destino) {
    params.set('destino', filters.destino)
  }
  if (filters.transportadora) {
    params.set('transportadora', filters.transportadora)
  }
  if (filters.tipoVeiculo) {
    params.set('tipo_veiculo', filters.tipoVeiculo)
  }

  return params
}

export function createEmptyFilters(): DashboardFilters {
  return {
    dataInicio: '',
    dataFim: '',
    origem: '',
    destino: '',
    transportadora: '',
    tipoVeiculo: '',
  }
}

async function fetchDashboardKpis(filters: DashboardFilters): Promise<DashboardKpis> {
  const params = buildFilterParams(filters)
  const [freightTotalResponse, adValoremTotalResponse, occurrenceRateResponse] =
    await Promise.all([
      api.get<KpiTotalResponse>('/kpis/frete-total', { params }),
      api.get<KpiTotalResponse>('/kpis/advalorem-total', { params }),
      api.get<OccurrenceRateResponse>('/kpis/taxa-ocorrencias', { params }),
    ])

  return {
    freightTotal: freightTotalResponse.data,
    adValoremTotal: adValoremTotalResponse.data,
    occurrenceRate: occurrenceRateResponse.data,
  }
}

export async function fetchDashboardAnalytics(
  filters: DashboardFilters,
): Promise<DashboardAnalytics> {
  const params = buildFilterParams(filters)
  const [kpis, carrierCostResponse, destinationRiskResponse] = await Promise.all([
    fetchDashboardKpis(filters),
    api.get<CarrierCostResponse>('/kpis/custo-por-transportadora', { params }),
    api.get<DestinationRiskResponse>('/kpis/custo-risco-destino', { params }),
  ])

  return {
    kpis,
    carrierCost: carrierCostResponse.data.items,
    destinationRisk: destinationRiskResponse.data.items,
  }
}

export async function fetchFilterOptions(
  filters: DashboardFilters,
): Promise<FilterOptions> {
  const params = buildFilterParams(filters)
  const [origensResponse, destinosResponse, transportadorasResponse, tiposVeiculoResponse] =
    await Promise.all([
      api.get<{ items: string[] }>('/filtros/origens', { params }),
      api.get<{ items: string[] }>('/filtros/destinos', { params }),
      api.get<{ items: string[] }>('/filtros/transportadoras', { params }),
      api.get<{ items: string[] }>('/filtros/tipos-veiculo', { params }),
    ])

  return {
    origens: origensResponse.data.items,
    destinos: destinosResponse.data.items,
    transportadoras: transportadorasResponse.data.items,
    tiposVeiculo: tiposVeiculoResponse.data.items,
  }
}
