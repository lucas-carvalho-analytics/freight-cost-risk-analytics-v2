import type { ReactNode } from 'react'

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(251,191,36,0.16),_transparent_26%),radial-gradient(circle_at_bottom_right,_rgba(14,165,233,0.2),_transparent_30%)]" />
      <div className="relative mx-auto grid min-h-screen max-w-6xl items-center gap-8 px-6 py-10 lg:grid-cols-[1.15fr_0.85fr] lg:px-10">
        <section className="hidden rounded-[2rem] border border-white/10 bg-white/5 p-10 text-white shadow-2xl shadow-black/20 backdrop-blur lg:block">
          <span className="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.22em] text-slate-200">
            Freight Cost Risk Analytics
          </span>
          <h1 className="mt-8 max-w-xl text-5xl font-semibold tracking-tight">
            Painel corporativo para custo, risco e operação logística.
          </h1>
          <p className="mt-6 max-w-lg text-base leading-7 text-slate-300">
            Este MVP conecta diretamente aos indicadores já expostos no backend e mantém o
            acesso protegido por JWT para dar base ao dashboard da próxima fase.
          </p>
          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
              <p className="text-sm text-slate-300">Autenticação</p>
              <p className="mt-2 text-lg font-semibold">JWT real</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
              <p className="text-sm text-slate-300">KPIs</p>
              <p className="mt-2 text-lg font-semibold">Frete e risco</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
              <p className="text-sm text-slate-300">Estrutura</p>
              <p className="mt-2 text-lg font-semibold">Pronta para crescer</p>
            </div>
          </div>
        </section>
        <div>{children}</div>
      </div>
    </div>
  )
}
