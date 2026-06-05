import { Eye, EyeOff, Lock, Mail, Trophy } from "lucide-react";
import { FormEvent, useState } from "react";
import type { ReactNode } from "react";
import toast from "react-hot-toast";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { defaultRouteForRole } from "../../components/layout/ProtectedRoute";
import { useAuthStore } from "../../store/authStore";

export function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, login, user } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  if (isAuthenticated && user) {
    return <Navigate replace to={defaultRouteForRole(user.role)} />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    try {
      await login(email, password);
      const nextUser = useAuthStore.getState().user;
      if (nextUser) {
        navigate(defaultRouteForRole(nextUser.role));
      }
    } catch {
      toast.error("Не удалось войти");
    }
  }

  return (
    <AuthShell>
      <form className="auth-card" onSubmit={handleSubmit}>
        <div>
          <h1 className="font-display text-2xl font-bold">Вход в систему</h1>
          <p className="mt-2 text-sm text-hs-t2">Введите свои учетные данные для входа.</p>
        </div>

        <label className="field">
          <span>Email</span>
          <div className="input-shell">
            <Mail className="size-4 text-hs-t3" />
            <input autoComplete="email" onChange={(event) => setEmail(event.target.value)} type="email" value={email} />
          </div>
        </label>

        <label className="field">
          <span>Пароль</span>
          <div className="input-shell">
            <Lock className="size-4 text-hs-t3" />
            <input autoComplete="current-password" onChange={(event) => setPassword(event.target.value)} type={showPassword ? "text" : "password"} value={password} />
            <button className="text-hs-t3 hover:text-hs-t1 transition-colors" onClick={() => setShowPassword(!showPassword)} tabIndex={-1} type="button">
              {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
            </button>
          </div>
        </label>

        <button className="btn-primary w-full" disabled={isLoading} type="submit">
          {isLoading ? "Вход..." : "Войти"}
        </button>

        <p className="text-center text-sm text-hs-t2">
          Нет аккаунта?{" "}
          <Link className="font-semibold text-hs-accent-light" to="/register">
            Зарегистрироваться
          </Link>
        </p>
      </form>
    </AuthShell>
  );
}

function AuthShell({ children }: { children: ReactNode }) {
  return (
    <main className="grid min-h-screen bg-hs-bg text-hs-t1 lg:grid-cols-[1.35fr_0.9fr]">
      <section className="auth-visual hidden items-center justify-center p-10 lg:flex">
        <div className="max-w-xl">
          <div className="mb-8 grid size-14 place-items-center rounded-xl bg-hs-gradient shadow-hs-glow">
            <Trophy className="size-7" />
          </div>
          <h1 className="font-display text-6xl font-bold text-gradient">HackScore</h1>
          <p className="mt-5 max-w-lg text-lg leading-8 text-hs-t2">Автоматическая оценка решений, экспертные баллы и лидерборды хакатона в одном интерфейсе.</p>
        </div>
      </section>
      <section className="flex items-center justify-center bg-hs-card px-5 py-10">{children}</section>
    </main>
  );
}
