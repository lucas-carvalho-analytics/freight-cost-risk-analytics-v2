export interface DashboardFilters {
  dataInicio: string
  dataFim: string
  origem: string
  destino: string
  transportadora: string
  tipoVeiculo: string
}

export interface FilterOptions {
  origens: string[]
  destinos: string[]
  transportadoras: string[]
  tiposVeiculo: string[]
}
