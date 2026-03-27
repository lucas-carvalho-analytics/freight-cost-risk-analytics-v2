import { useEffect, useState } from 'react'
import { getApiErrorMessage } from '../services/auth'
import { fetchFilterOptions } from '../services/dashboard'
import type { DashboardFilters, FilterOptions } from '../types/filters'

interface DashboardFilterOptionsState {
  data: FilterOptions | null
  isLoading: boolean
  errorMessage: string | null
  refetch: () => Promise<void>
}

export function useDashboardFilters(filters: DashboardFilters): DashboardFilterOptionsState {
  const [data, setData] = useState<FilterOptions | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  async function refetch(): Promise<void> {
    setIsLoading(true)
    setErrorMessage(null)

    try {
      const nextData = await fetchFilterOptions(filters)
      setData(nextData)
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(
          error,
          'Não foi possível carregar as opções de filtros.',
        ),
      )
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    async function loadOptions(): Promise<void> {
      setIsLoading(true)
      setErrorMessage(null)

      try {
        const nextData = await fetchFilterOptions(filters)
        setData(nextData)
      } catch (error) {
        setErrorMessage(
          getApiErrorMessage(
            error,
            'Não foi possível carregar as opções de filtros.',
          ),
        )
      } finally {
        setIsLoading(false)
      }
    }

    void loadOptions()
  }, [filters])

  return {
    data,
    isLoading,
    errorMessage,
    refetch,
  }
}
