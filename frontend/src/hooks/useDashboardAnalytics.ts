import { useEffect, useState } from 'react'
import { getApiErrorMessage } from '../services/auth'
import { fetchDashboardAnalytics } from '../services/dashboard'
import type { DashboardAnalytics } from '../types/dashboard'
import type { DashboardFilters } from '../types/filters'

interface DashboardAnalyticsState {
  data: DashboardAnalytics | null
  isLoading: boolean
  errorMessage: string | null
  refetch: () => Promise<void>
}

export function useDashboardAnalytics(filters: DashboardFilters): DashboardAnalyticsState {
  const [data, setData] = useState<DashboardAnalytics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  async function refetch(): Promise<void> {
    setIsLoading(true)
    setErrorMessage(null)

    try {
      const nextData = await fetchDashboardAnalytics(filters)
      setData(nextData)
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(
          error,
          'Não foi possível carregar os indicadores e gráficos.',
        ),
      )
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    async function loadAnalytics(): Promise<void> {
      setIsLoading(true)
      setErrorMessage(null)

      try {
        const nextData = await fetchDashboardAnalytics(filters)
        setData(nextData)
      } catch (error) {
        setErrorMessage(
          getApiErrorMessage(
            error,
            'Não foi possível carregar os indicadores e gráficos.',
          ),
        )
      } finally {
        setIsLoading(false)
      }
    }

    void loadAnalytics()
  }, [filters])

  return {
    data,
    isLoading,
    errorMessage,
    refetch,
  }
}
