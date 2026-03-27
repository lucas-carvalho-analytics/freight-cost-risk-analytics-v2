interface MetricCardProps {
  title: string
  value: string
  description: string
}

export function MetricCard({ title, value, description }: MetricCardProps) {
  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-950/5">
      <p className="text-sm font-medium text-slate-500">{title}</p>
      <p className="mt-4 text-3xl font-semibold tracking-tight text-slate-950">{value}</p>
      <p className="mt-2 text-sm text-slate-600">{description}</p>
    </article>
  )
}
