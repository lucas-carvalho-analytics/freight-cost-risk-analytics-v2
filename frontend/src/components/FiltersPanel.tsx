import type { ChangeEvent } from 'react'
import type { DashboardFilters, FilterOptions } from '../types/filters'

interface FiltersPanelProps {
  filters: DashboardFilters
  options: FilterOptions | null
  isLoading: boolean
  errorMessage: string | null
  onFieldChange: (field: keyof DashboardFilters, value: string) => void
  onRetry: () => void
}

interface FilterFieldProps {
  label: string
  name: keyof DashboardFilters
  options: string[]
  value: string
  disabled?: boolean
  onFieldChange: (field: keyof DashboardFilters, value: string) => void
}

function FilterField({
  label,
  name,
  options,
  value,
  disabled = false,
  onFieldChange,
}: FilterFieldProps) {
  function handleChange(event: ChangeEvent<HTMLSelectElement>) {
    onFieldChange(name, event.target.value)
  }

  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-slate-700">{label}</span>
      <select
        className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        disabled={disabled}
        onChange={handleChange}
        value={value}
      >
        <option value="">Todos</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  )
}

export function FiltersPanel({
  filters,
  options,
  isLoading,
  errorMessage,
  onFieldChange,
  onRetry,
}: FiltersPanelProps) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">Filtros operacionais</p>
          <h2 className="mt-2 text-xl font-semibold text-slate-950">
            Refine os indicadores do dashboard
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Os filtros usam a API real e atualizam KPIs, opções relacionadas e gráficos no
            mesmo fluxo.
          </p>
        </div>
        {isLoading ? (
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
            Atualizando filtros...
          </span>
        ) : null}
      </div>

      {errorMessage ? (
        <div className="mt-5 flex flex-col gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900 sm:flex-row sm:items-center sm:justify-between">
          <span>{errorMessage}</span>
          <button
            className="rounded-xl border border-amber-300 bg-white px-3 py-2 text-sm font-medium text-amber-800 transition hover:bg-amber-100"
            onClick={onRetry}
            type="button"
          >
            Recarregar filtros
          </button>
        </div>
      ) : null}

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Data inicial</span>
          <input
            className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100"
            onChange={(event) => onFieldChange('dataInicio', event.target.value)}
            type="date"
            value={filters.dataInicio}
          />
        </label>

        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Data final</span>
          <input
            className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100"
            onChange={(event) => onFieldChange('dataFim', event.target.value)}
            type="date"
            value={filters.dataFim}
          />
        </label>

        <FilterField
          disabled={isLoading || !options}
          label="Origem"
          name="origem"
          onFieldChange={onFieldChange}
          options={options?.origens ?? []}
          value={filters.origem}
        />

        <FilterField
          disabled={isLoading || !options}
          label="Destino"
          name="destino"
          onFieldChange={onFieldChange}
          options={options?.destinos ?? []}
          value={filters.destino}
        />

        <FilterField
          disabled={isLoading || !options}
          label="Transportadora"
          name="transportadora"
          onFieldChange={onFieldChange}
          options={options?.transportadoras ?? []}
          value={filters.transportadora}
        />

        <FilterField
          disabled={isLoading || !options}
          label="Tipo de veículo"
          name="tipoVeiculo"
          onFieldChange={onFieldChange}
          options={options?.tiposVeiculo ?? []}
          value={filters.tipoVeiculo}
        />
      </div>
    </section>
  )
}
