import { CheckCircle2, FileArchive, FileText, PlayCircle, Presentation, RefreshCw, Send, UploadCloud, type LucideIcon } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import toast from "react-hot-toast";

import { api } from "../../api/client";
import type { CheckResult, CheckType, Hackathon, Submission, Team } from "../../api/types";
import { useAuthStore } from "../../store/authStore";

const checkLabels: Record<CheckType, string> = {
  code: "Код",
  documentation: "Документация",
  presentation: "Презентация",
  screencast: "Скринкаст",
};

export function SubmissionPage() {
  const user = useAuthStore((state) => state.user);
  const [team, setTeam] = useState<Team | null>(null);
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [repoUrl, setRepoUrl] = useState("");
  const [screencastUrl, setScreencastUrl] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void bootstrap();
  }, []);

  useEffect(() => {
    if (!submission || submission.status !== "checking") {
      return;
    }
    const timer = window.setInterval(() => {
      void reloadSubmission(submission.id);
    }, 5000);
    return () => window.clearInterval(timer);
  }, [submission]);

  const progress = useMemo(() => {
    if (!submission) {
      return 0;
    }
    return [submission.repo_url || submission.repo_archive, submission.doc_file, submission.presentation, submission.screencast_file || submission.screencast_url, submission.submitted_at].filter(Boolean).length;
  }, [submission]);

  async function bootstrap() {
    try {
      const { data: hackathons } = await api.get<Hackathon[]>("/hackathons/");
      for (const hackathon of hackathons) {
        const { data: teams } = await api.get<Team[]>(`/hackathons/${hackathon.id}/teams/`);
        const myTeam = teams.find((item) => item.members.some((member) => member.user_id === user?.id));
        if (myTeam) {
          setTeam(myTeam);
          await loadOrCreateSubmission(myTeam);
          return;
        }
      }
    } catch {
      toast.error("Не удалось подготовить загрузку решения");
    }
  }

  async function loadOrCreateSubmission(nextTeam: Team) {
    try {
      const { data } = await api.get<Submission>(`/submissions/team/${nextTeam.id}`);
      setSubmission(data);
      setRepoUrl(data.repo_url ?? "");
      setScreencastUrl(data.screencast_url ?? "");
    } catch {
      const { data } = await api.post<Submission>("/submissions/", {
        team_id: nextTeam.id,
        hackathon_id: nextTeam.hackathon_id,
      });
      setSubmission(data);
    }
  }

  async function reloadSubmission(id: string) {
    const { data } = await api.get<Submission>(`/submissions/${id}`);
    setSubmission(data);
  }

  async function saveRepo(event: FormEvent) {
    event.preventDefault();
    if (!submission || !repoUrl.trim()) {
      return;
    }
    setBusy(true);
    try {
      const form = new FormData();
      form.append("repo_url", repoUrl);
      const { data } = await api.put<Submission>(`/submissions/${submission.id}/repo`, form);
      setSubmission(data);
      toast.success("Репозиторий сохранен");
    } catch {
      toast.error("Не удалось сохранить репозиторий");
    } finally {
      setBusy(false);
    }
  }

  async function upload(path: "documentation" | "presentation" | "screencast", file: File) {
    if (!submission) {
      return;
    }
    setBusy(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const { data } = await api.put<Submission>(`/submissions/${submission.id}/${path}`, form);
      setSubmission(data);
      toast.success("Файл загружен");
    } catch {
      toast.error("Не удалось загрузить файл");
    } finally {
      setBusy(false);
    }
  }

  async function saveScreencastUrl() {
    if (!submission || !screencastUrl.trim()) {
      return;
    }
    setBusy(true);
    try {
      const form = new FormData();
      form.append("screencast_url", screencastUrl);
      const { data } = await api.put<Submission>(`/submissions/${submission.id}/screencast`, form);
      setSubmission(data);
      toast.success("Ссылка сохранена");
    } catch {
      toast.error("Не удалось сохранить ссылку");
    } finally {
      setBusy(false);
    }
  }

  async function submit() {
    if (!submission) {
      return;
    }
    setBusy(true);
    try {
      const { data } = await api.post<Submission>(`/submissions/${submission.id}/submit`);
      setSubmission(data);
      toast.success("Отправлено на проверку");
    } catch {
      toast.error("Не удалось отправить решение");
    } finally {
      setBusy(false);
    }
  }

  if (!team || !submission) {
    return (
      <div className="rounded-xl border border-hs-border bg-hs-card p-6">
        <h1 className="font-display text-2xl font-bold">Загрузка решения</h1>
        <p className="mt-2 text-sm text-hs-t2">Создайте команду, чтобы загрузить решение.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="font-display text-2xl font-bold">Загрузка решения</h1>
          <p className="mt-2 text-sm text-hs-t2">{team.name} · статус {submission.status}</p>
        </div>
        <button className="btn-primary" disabled={busy} onClick={() => void submit()} type="button">
          <Send className="size-4" />
          Отправить на проверку
        </button>
      </div>

      <div className="rounded-xl border border-hs-border bg-hs-card p-4">
        <div className="mb-3 flex justify-between text-xs text-hs-t2">
          <span>Репозиторий</span>
          <span>Документация</span>
          <span>Презентация</span>
          <span>Скринкаст</span>
          <span>Отправка</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-hs-bg">
          <div className="h-full bg-hs-gradient transition-all" style={{ width: `${(progress / 5) * 100}%` }} />
        </div>
      </div>

      <div className="grid gap-4">
        <ArtifactCard icon={FileArchive} title="Репозиторий кода" done={Boolean(submission.repo_url || submission.repo_archive)}>
          <form className="grid gap-3 md:grid-cols-[1fr_auto]" onSubmit={saveRepo}>
            <input className="plain-input" onChange={(event) => setRepoUrl(event.target.value)} placeholder="https://github.com/team/project" value={repoUrl} />
            <button className="btn-secondary" disabled={busy} type="submit">Сохранить</button>
          </form>
        </ArtifactCard>

        <ArtifactCard icon={FileText} title="Документация" done={Boolean(submission.doc_file)}>
          <FileUpload accept=".pdf,.docx,.md" current={submission.doc_file} onFile={(file) => void upload("documentation", file)} />
        </ArtifactCard>

        <ArtifactCard icon={Presentation} title="Презентация" done={Boolean(submission.presentation)}>
          <FileUpload accept=".pptx,.pdf" current={submission.presentation} onFile={(file) => void upload("presentation", file)} />
        </ArtifactCard>

        <ArtifactCard icon={PlayCircle} title="Скринкаст" done={Boolean(submission.screencast_file || submission.screencast_url)}>
          <div className="grid gap-3">
            <FileUpload accept=".mp4,.webm,.mov" current={submission.screencast_file} onFile={(file) => void upload("screencast", file)} />
            <div className="grid gap-3 md:grid-cols-[1fr_auto]">
              <input className="plain-input" onChange={(event) => setScreencastUrl(event.target.value)} placeholder="https://youtube.com/..." value={screencastUrl} />
              <button className="btn-secondary" disabled={busy} onClick={() => void saveScreencastUrl()} type="button">Сохранить ссылку</button>
            </div>
          </div>
        </ArtifactCard>
      </div>

      <Results checks={submission.check_results} onReload={() => void reloadSubmission(submission.id)} />
    </div>
  );
}

function ArtifactCard({ children, done, icon: Icon, title }: { children: ReactNode; done: boolean; icon: LucideIcon; title: string }) {
  return (
    <section className="rounded-xl border border-hs-border bg-hs-card p-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="grid size-10 place-items-center rounded-lg bg-hs-cyan-15 text-hs-cyan">
            <Icon className="size-5" />
          </div>
          <h2 className="font-display text-lg font-bold">{title}</h2>
        </div>
        {done ? <CheckCircle2 className="size-5 text-hs-green" /> : null}
      </div>
      {children}
    </section>
  );
}

function FileUpload({ accept, current, onFile }: { accept: string; current: string | null; onFile: (file: File) => void }) {
  return (
    <label className="grid min-h-28 cursor-pointer place-items-center rounded-lg border border-dashed border-hs-border bg-hs-bg p-4 text-center text-sm text-hs-t2">
      <input accept={accept} className="hidden" onChange={(event) => event.target.files?.[0] && onFile(event.target.files[0])} type="file" />
      <span className="grid justify-items-center gap-2">
        <UploadCloud className="size-6 text-hs-accent-light" />
        {current ? `Загружено: ${current.split("/").pop()}` : "Выберите файл или перетащите его сюда"}
      </span>
    </label>
  );
}

function Results({ checks, onReload }: { checks: CheckResult[]; onReload: () => void }) {
  if (checks.length === 0) {
    return null;
  }

  return (
    <section className="rounded-xl border border-hs-border bg-hs-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-lg font-bold">Результаты проверок</h2>
        <button className="btn-secondary" onClick={onReload} type="button">
          <RefreshCw className="size-4" />
          Обновить
        </button>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {checks.map((check) => (
          <details className="rounded-lg border border-hs-border bg-hs-bg p-4" key={check.id}>
            <summary className="cursor-pointer list-none">
              <div className="flex items-center justify-between">
                <span className="font-semibold">{checkLabels[check.check_type]}</span>
                <span className="badge">{check.score ?? "..."}/10 · {check.status}</span>
              </div>
            </summary>
            <pre className="mt-4 max-h-72 overflow-auto rounded-lg bg-black/30 p-3 text-xs text-hs-t2">{JSON.stringify(check.report, null, 2)}</pre>
          </details>
        ))}
      </div>
    </section>
  );
}
