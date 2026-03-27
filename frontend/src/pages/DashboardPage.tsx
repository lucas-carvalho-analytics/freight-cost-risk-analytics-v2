import type { ReactNode } from 'react'
import { useState } from 'react'
import { CarrierCostChart } from '../components/CarrierCostChart'
import { DestinationRiskChart } from '../components/DestinationRiskChart'
import { FiltersPanel } from '../components/FiltersPanel'
import { DashboardLayout } from '../layouts/DashboardLayout'
import { MetricCard } from '../components/MetricCard'
import { PageState } from '../components/PageState'
import { useDashboardAnalytics } from '../hooks/useDashboardAnalytics'
import { useDashboardFilters } from '../hooks/useDashboardFilters'
import { createEmptyFilters } from '../services/dashboard'
import type { DashboardFilters } from '../types/filters'

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
  }).format(value)
}

function formatPercentage(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

export function DashboardPage() {
  const [filters, setFilters] = useState<DashboardFilters>(createEmptyFilters())
  const {
    data: analytics,
    errorMessage: analyticsErrorMessage,
    isLoading: analyticsIsLoading,
    refetch: refetchAnalytics,
  } = useDashboardAnalytics(filters)
  const {
    data: filterOptions,
    errorMessage: filterErrorMessage,
    isLoading: filterIsLoading,
    refetch: refetchFilters,
  } = useDashboardFilters(filters)

  function handleFilterChange(field: keyof DashboardFilters, value: string) {
    setFilters((currentFilters) => ({
      ...currentFilters,
      [field]: value,
    }))
  }

  function clearFilters() {
    setFilters(createEmptyFilters())
  }

  let analyticsContent: ReactNode

  if (analyticsIsLoading) {
    analyticsContent = (
      <PageState
        title="Carregando dashboard"
        description="Estamos consultando os indicadores e gráficos reais da operação."
      />
    )
  } else if (analyticsErrorMessage || !analytics) {
    analyticsContent = (
      <PageState
        actionLabel="Tentar novamente"
        description={analyticsErrorMessage ?? 'Não foi possível carregar os dados do dashboard.'}
        onAction={() => void refetchAnalytics()}
        title="Falha ao carregar indicadores"
      />
    )
  } else if (analytics.kpis.freightTotal.shipment_count === 0) {
    analyticsContent = (
      <PageState
        actionLabel="Limpar filtros"
        description="Nenhum embarque foi encontrado com a combinação atual de filtros."
        onAction={clearFilters}
        title="Sem dados para exibir"
      />
    )
  } else {
    analyticsContent = (
      <div className="space-y-6">
        <section className="grid gap-4 lg:grid-cols-3">
          <MetricCard
            description={`${analytics.kpis.freightTotal.shipment_count} embarques considerados`}
            title="Frete total"
            value={formatCurrency(analytics.kpis.freightTotal.value)}
          />
          <MetricCard
            description={`${analytics.kpis.adValoremTotal.shipment_count} embarques considerados`}
            title="Ad valorem total"
            value={formatCurrency(analytics.kpis.adValoremTotal.value)}
          />
          <MetricCard
            description={`${analytics.kpis.occurrenceRate.shipments_com_ocorrencia} embarques com ocorrência`}
            title="Taxa de ocorrências"
            value={`${formatPercentage(analytics.kpis.occurrenceRate.taxa_ocorrencias_pct)}%`}
          />
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <CarrierCostChart data={analytics.carrierCost} />
          <DestinationRiskChart data={analytics.destinationRisk} />
        </section>
      </div>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <FiltersPanel
          errorMessage={filterErrorMessage}
          filters={filters}
          isLoading={filterIsLoading}
          onFieldChange={handleFilterChange}
          onRetry={() => void refetchFilters()}
          options={filterOptions}
        />

        <div className="flex justify-end">
          <button
            className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-50"
            onClick={clearFilters}
            type="button"
          >
            Limpar filtros
          </button>
        </div>

        {analyticsContent}
      </div>
    </DashboardLayout>
  )
}
