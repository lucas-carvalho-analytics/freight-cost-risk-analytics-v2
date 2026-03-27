import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { DestinationRiskItem } from '../types/dashboard'

interface DestinationRiskChartProps {
  data: DestinationRiskItem[]
}

export function DestinationRiskChart({ data }: DestinationRiskChartProps) {
  const topDestinations = [...data]
    .sort((left, right) => right.score_risco - left.score_risco)
    .slice(0, 5)

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5">
      <div>
        <p className="text-sm font-medium text-slate-500">Gráfico 2</p>
        <h2 className="mt-2 text-xl font-semibold text-slate-950">
          Score de risco por destino
        </h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Destinos ordenados pelo score heurístico já calculado pela API, destacando os
          pontos que merecem maior atenção operacional.
        </p>
      </div>

      <div className="mt-6 h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={topDestinations} layout="vertical" margin={{ top: 8, right: 20, left: 30, bottom: 0 }}>
            <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" horizontal={false} />
            <XAxis
              axisLine={false}
              dataKey="score_risco"
              tickLine={false}
              tick={{ fill: '#475569' }}
              type="number"
            />
            <YAxis
              axisLine={false}
              dataKey="destino"
              tickLine={false}
              tick={{ fill: '#475569', fontSize: 12 }}
              type="category"
              width={160}
            />
            <Tooltip
              contentStyle={{
                borderRadius: '16px',
                borderColor: '#cbd5e1',
                boxShadow: '0 16px 40px rgba(15, 23, 42, 0.12)',
              }}
            />
            <Bar dataKey="score_risco" fill="#0f172a" radius={[0, 10, 10, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
