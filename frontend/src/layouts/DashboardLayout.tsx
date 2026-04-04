import type { ReactNode } from 'react'
import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { ChangePasswordModal } from '../components/ChangePasswordModal'

export function DashboardLayout({ children }: { children: ReactNode }) {
  const { logout, user } = useAuth()
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false)

  return (
    <div className="min-h-screen bg-transparent">
      <header className="border-b border-slate-200/80 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-4 lg:px-10">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-700">
              Freight Cost Risk Analytics
            </p>
            <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
              Dashboard executivo
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-right sm:block">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Sessão</p>
              <p className="mt-1 text-sm font-medium text-slate-700">{user?.full_name}</p>
            </div>
            <button
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-50"
              onClick={() => setIsPasswordModalOpen(true)}
              type="button"
            >
              Alterar senha
            </button>
            <button
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-50"
              onClick={logout}
              type="button"
            >
              Sair
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-8 lg:px-10">{children}</main>
      
      <ChangePasswordModal 
        isOpen={isPasswordModalOpen} 
        onClose={() => setIsPasswordModalOpen(false)} 
      />
    </div>
  )
}
