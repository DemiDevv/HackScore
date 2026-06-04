import { Activity, ArrowRight, CheckCircle2, Code2, FileUp, Trophy } from "lucide-react";
import { Toaster } from "react-hot-toast";

const checks = [
  { icon: Code2, label: "Код", score: "8.4", status: "Структура, линтер, секреты" },
  { icon: FileUp, label: "Документы", score: "9.1", status: "Разделы, объем, схемы" },
  { icon: Activity, label: "Скринкаст", score: "7.8", status: "Метаданные и транскрипт" },
];

function App() {
  return (
    <main className="min-h-screen bg-hs-bg text-hs-t1">
      <div className="flex min-h-screen flex-col">
        <header className="sticky top-0 z-10 border-b border-white/5 bg-hs-card/75 backdrop-blur-2xl">
          <div className="mx-auto flex h-[60px] max-w-6xl items-center justify-between px-6">
            <div className="flex items-center gap-3">
              <div className="grid size-9 place-items-center rounded-lg bg-hs-gradient shadow-hs-glow">
                <Trophy className="size-5" />
              </div>
              <span className="font-display text-lg font-bold text-gradient">HackScore</span>
            </div>
            <div className="hidden items-center gap-2 text-sm text-hs-t2 sm:flex">
              <span className="rounded-full border border-hs-border bg-hs-card-hover px-3 py-1">
                API /api/health
              </span>
              <span className="size-2 rounded-full bg-hs-green shadow-[0_0_12px_rgba(16,185,129,0.6)]" />
            </div>
          </div>
        </header>

        <section className="mx-auto grid w-full max-w-6xl flex-1 gap-8 px-6 py-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
          <div className="space-y-7 animate-fade-in">
            <div className="inline-flex items-center gap-2 rounded-full border border-hs-border bg-hs-card px-3 py-1 text-xs font-medium text-hs-t2">
              <CheckCircle2 className="size-4 text-hs-green" />
              Каркас проекта инициализирован
            </div>
            <div className="space-y-4">
              <h1 className="font-display text-4xl font-bold leading-tight sm:text-5xl">
                Автоматическая оценка решений для хакатонов
              </h1>
              <p className="max-w-2xl text-base leading-7 text-hs-t2">
                Базовый слой HackScore готов к развитию: FastAPI backend, React frontend,
                PostgreSQL, Redis, Celery и Docker Compose.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <a className="btn-primary" href="/api/health">
                Проверить API
                <ArrowRight className="size-4" />
              </a>
              <a className="btn-secondary" href="/api/docs">
                Swagger docs
              </a>
            </div>
          </div>

          <div className="rounded-xl border border-hs-border bg-hs-card p-5 shadow-hs-panel animate-fade-up">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h2 className="font-display text-lg font-bold">Проверки решения</h2>
                <p className="mt-1 text-sm text-hs-t2">Preview ключевого сценария участника</p>
              </div>
              <span className="rounded-full bg-hs-accent-15 px-3 py-1 text-xs font-medium text-hs-accent-light">
                checking
              </span>
            </div>

            <div className="space-y-3">
              {checks.map((item) => {
                const Icon = item.icon;
                return (
                  <div
                    className="flex items-center justify-between rounded-lg border border-hs-border bg-hs-bg p-4"
                    key={item.label}
                  >
                    <div className="flex items-center gap-3">
                      <div className="grid size-10 place-items-center rounded-lg bg-hs-cyan-15 text-hs-cyan">
                        <Icon className="size-5" />
                      </div>
                      <div>
                        <div className="font-display text-sm font-semibold">{item.label}</div>
                        <div className="mt-1 text-xs text-hs-t2">{item.status}</div>
                      </div>
                    </div>
                    <div className="font-display text-xl font-bold">{item.score}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      </div>
      <Toaster position="bottom-right" />
    </main>
  );
}

export default App;
