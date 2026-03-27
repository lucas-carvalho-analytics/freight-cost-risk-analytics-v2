interface PageStateProps {
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
}

export function PageState({
  title,
  description,
  actionLabel,
  onAction,
}: PageStateProps) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm shadow-slate-950/5">
      <h2 className="text-xl font-semibold text-slate-950">{title}</h2>
      <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
      {actionLabel && onAction ? (
        <button
          className="mt-6 rounded-xl bg-slate-950 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-800"
          onClick={onAction}
          type="button"
        >
          {actionLabel}
        </button>
      ) : null}
    </div>
  )
}
