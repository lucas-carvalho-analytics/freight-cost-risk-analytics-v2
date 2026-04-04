import { useState, type FormEvent } from 'react'
import { useLocation } from 'react-router-dom'
import { AuthLayout } from '../layouts/AuthLayout'
import { getApiErrorMessage } from '../services/auth'
import { useAuth } from '../hooks/useAuth'

export function LoginPage() {
  const location = useLocation()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const sessionExpired = (location.state as { reason?: string } | null)?.reason === 'expired'

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsSubmitting(true)
    setErrorMessage(null)

    try {
      await login({ email, password })
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(error, 'Não foi possível entrar agora. Revise suas credenciais.'),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout>
      <section className="rounded-[2rem] border border-slate-200 bg-white p-8 shadow-2xl shadow-slate-950/10 sm:p-10">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-sky-700">
            Acesso seguro
          </p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
            Entrar no dashboard
          </h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Use um usuário ativo do backend para acessar os indicadores protegidos.
          </p>
        </div>

        {sessionExpired ? (
          <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            Sua sessão expirou ou ficou inválida. Faça login novamente.
          </div>
        ) : null}

        {errorMessage ? (
          <div className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {errorMessage}
          </div>
        ) : null}

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700">Login</span>
            <input
              autoComplete="username"
              className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-slate-950 outline-none transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100"
              onChange={(event) => setEmail(event.target.value)}
              placeholder="Seu usuário ou e-mail"
              required
              type="text"
              value={email}
            />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm font-medium text-slate-700">Senha</span>
            <input
              autoComplete="current-password"
              className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-slate-950 outline-none transition focus:border-sky-500 focus:ring-4 focus:ring-sky-100"
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Sua senha"
              required
              type="password"
              value={password}
            />
          </label>

          <button
            className="w-full rounded-2xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </section>
    </AuthLayout>
  )
}
