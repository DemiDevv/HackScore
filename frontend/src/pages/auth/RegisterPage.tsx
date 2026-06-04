import { Lock, Mail, UserRound } from "lucide-react";
import { FormEvent, useState } from "react";
import toast from "react-hot-toast";
import { Link, Navigate, useNavigate } from "react-router-dom";

import type { UserRole } from "../../api/types";
import { defaultRouteForRole } from "../../components/layout/ProtectedRoute";
import { useAuthStore } from "../../store/authStore";

const roles: Array<{ value: UserRole; label: string; description: string }> = [
  { value: "participant", label: "Участник", description: "Загружает решение и решает задачи" },
  { value: "jury", label: "Жюри", description: "Проверяет команды и ставит оценки" },
  { value: "organizer", label: "Организатор", description: "Настраивает хакатон и критерии" },
];

export function RegisterPage() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, register, user } = useAuthStore();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordRepeat, setPasswordRepeat] = useState("");
  const [role, setRole] = useState<UserRole>("participant");

  if (isAuthenticated && user) {
    return <Navigate replace to={defaultRouteForRole(user.role)} />;
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (password !== passwordRepeat) {
      toast.error("Пароли не совпадают");
      return;
    }
    try {
      await register({ email, password, full_name: fullName, role });
      const nextUser = useAuthStore.getState().user;
      if (nextUser) {
        navigate(defaultRouteForRole(nextUser.role));
      }
    } catch {
      toast.error("Не удалось зарегистрироваться");
    }
  }

  return (
    <main className="grid min-h-screen bg-hs-bg text-hs-t1 lg:grid-cols-[1.2fr_0.95fr]">
      <section className="auth-visual hidden items-center justify-center p-10 lg:flex">
        <div className="max-w-xl">
          <h1 className="font-display text-6xl font-bold text-gradient">HackScore</h1>
          <p className="mt-5 max-w-lg text-lg leading-8 text-hs-t2">Создайте роль и войдите в рабочий контур хакатона.</p>
        </div>
      </section>
      <section className="flex items-center justify-center bg-hs-card px-5 py-10">
        <form className="auth-card" onSubmit={handleSubmit}>
          <div>
            <h1 className="font-display text-2xl font-bold">Создать аккаунт</h1>
            <p className="mt-2 text-sm text-hs-t2">Роль определит доступные разделы приложения.</p>
          </div>

          <label className="field">
            <span>Полное имя</span>
            <div className="input-shell">
              <UserRound className="size-4 text-hs-t3" />
              <input onChange={(event) => setFullName(event.target.value)} value={fullName} />
            </div>
          </label>

          <label className="field">
            <span>Email</span>
            <div className="input-shell">
              <Mail className="size-4 text-hs-t3" />
              <input onChange={(event) => setEmail(event.target.value)} type="email" value={email} />
            </div>
          </label>

          <div className="grid gap-3 sm:grid-cols-2">
            <label className="field">
              <span>Пароль</span>
              <div className="input-shell">
                <Lock className="size-4 text-hs-t3" />
                <input onChange={(event) => setPassword(event.target.value)} type="password" value={password} />
              </div>
            </label>
            <label className="field">
              <span>Повтор</span>
              <div className="input-shell">
                <Lock className="size-4 text-hs-t3" />
                <input onChange={(event) => setPasswordRepeat(event.target.value)} type="password" value={passwordRepeat} />
              </div>
            </label>
          </div>

          <div className="grid gap-2 sm:grid-cols-3">
            {roles.map((item) => (
              <button className={`role-card ${role === item.value ? "role-card-active" : ""}`} key={item.value} onClick={() => setRole(item.value)} type="button">
                <span>{item.label}</span>
                <small>{item.description}</small>
              </button>
            ))}
          </div>

          <button className="btn-primary w-full" disabled={isLoading} type="submit">
            {isLoading ? "Создание..." : "Зарегистрироваться"}
          </button>

          <p className="text-center text-sm text-hs-t2">
            Уже есть аккаунт?{" "}
            <Link className="font-semibold text-hs-accent-light" to="/login">
              Войти
            </Link>
          </p>
        </form>
      </section>
    </main>
  );
}
