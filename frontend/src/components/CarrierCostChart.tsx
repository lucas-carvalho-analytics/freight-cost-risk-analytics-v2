import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { CarrierCostItem } from '../types/dashboard'

interface CarrierCostChartProps {
  data: CarrierCostItem[]
}

export function CarrierCostChart({ data }: CarrierCostChartProps) {
  return (
    <section className="min-w-0 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5">
      <div>
        <p className="text-sm font-medium text-slate-500">Gráfico 1</p>
        <h2 className="mt-2 text-xl font-semibold text-slate-950">
          Custo médio por transportadora
        </h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Leitura direta do endpoint agrupado para comparar a média de frete entre as
          transportadoras filtradas.
        </p>
      </div>

      <div className="mt-6 h-80 min-w-0">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 12, left: -20, bottom: 0 }}>
            <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />
            <XAxis
              axisLine={false}
              dataKey="transportadora"
              tickLine={false}
              tick={{ fill: '#475569' }}
            />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#475569' }} />
            <Tooltip
              contentStyle={{
                borderRadius: '16px',
                borderColor: '#cbd5e1',
                boxShadow: '0 16px 40px rgba(15, 23, 42, 0.12)',
              }}
            />
            <Bar dataKey="custo_medio_frete" fill="#0369a1" radius={[10, 10, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
