import { AlertTriangle, BrainCircuit, CheckCircle2, CircleHelp, Gauge, Save } from "lucide-react";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import toast from "react-hot-toast";
import { Link, useParams } from "react-router-dom";

import { api } from "../../api/client";
import type { AIReview, CheckType, Criterion, Hackathon, ReviewDetail } from "../../api/types";

const tabs: CheckType[] = ["code", "documentation", "presentation", "screencast"];

const verdictLabels: Record<string, string> = {
  strong_candidate: "сильный кандидат",
  promising: "перспективно",
  needs_manual_review: "ручная проверка",
  high_risk: "высокий риск",
};

const signalLabels: Record<string, string> = {
  code_quality: "Код",
  documentation_quality: "Документация",
  pitch_quality: "Питч",
  demo_readiness: "Готовность демо",
  risk_level: "Риск",
  completed_checks_ratio: "Проверки",
  artifact_coverage: "Артефакты",
};

export function ReviewDetailPage() {
  const { submissionId } = useParams();
  const [detail, setDetail] = useState<ReviewDetail | null>(null);
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [activeTab, setActiveTab] = useState<CheckType>("code");
  const [scores, setScores] = useState<Record<string, { score: number; comment: string }>>({});

  const load = useCallback(async () => {
    if (!submissionId) {
      return;
    }
    try {
      const { data } = await api.get<ReviewDetail>(`/scoring/submissions/${submissionId}/review`);
      setDetail(data);
      const { data: hackathons } = await api.get<Hackathon[]>("/hackathons/");
      const hackathon = hackathons[0];
      if (hackathon) {
        const criteriaResponse = await api.get<Criterion[]>(`/hackathons/${hackathon.id}/criteria/`);
        const expertCriteria = criteriaResponse.data.filter((criterion) => !criterion.is_auto);
        setCriteria(expertCriteria);
        const nextScores: Record<string, { score: number; comment: string }> = {};
        for (const criterion of expertCriteria) {
          const existing = data.my_scores.find((score) => score.criterion_id === criterion.id);
          nextScores[criterion.id] = { score: existing?.score ?? 0, comment: existing?.comment ?? "" };
        }
        setScores(nextScores);
      }
    } catch {
      toast.error("Не удалось загрузить оценку");
    }
  }, [submissionId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (!detail) {
      return;
    }
    try {
      await api.post(`/scoring/submissions/${detail.submission_id}/scores`, Object.entries(scores).map(([criterion_id, value]) => ({ criterion_id, ...value })));
      toast.success("Оценки сохранены");
      await load();
    } catch {
      toast.error("Не удалось сохранить оценки");
    }
  }

  const activeCheck = useMemo(() => detail?.checks.find((check) => check.check_type === activeTab), [activeTab, detail]);

  if (!detail) {
    return <div className="rounded-xl border border-hs-border bg-hs-card p-6 text-hs-t2">Загрузка...</div>;
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_380px]">
      <section className="space-y-5">
        <div>
          <Link className="text-sm text-hs-accent-light" to="/jury/reviews">Назад к списку</Link>
          <h1 className="mt-3 font-display text-2xl font-bold">{detail.team_name}</h1>
          <p className="mt-2 text-sm text-hs-t2">Авто-балл: {detail.auto_score ?? "-"} · моя оценка: {detail.my_score ?? "-"}</p>
        </div>

        <AIReviewPanel review={detail.ai_review} />

        <div className="rounded-xl border border-hs-border bg-hs-card p-5">
          <div className="mb-4 flex flex-wrap gap-2">
            {tabs.map((tab) => (
              <button className={`filter-pill ${activeTab === tab ? "filter-pill-active" : ""}`} key={tab} onClick={() => setActiveTab(tab)} type="button">
                {tab}
              </button>
            ))}
          </div>

          <div className="rounded-lg border border-hs-border bg-hs-bg p-4">
            <div className="mb-3 flex items-center justify-between">
              <span className="font-semibold">{activeTab}</span>
              <span className="badge">{activeCheck?.score ?? "..."}/10 · {activeCheck?.status ?? "missing"}</span>
            </div>
            <pre className="max-h-[520px] overflow-auto rounded-lg bg-black/30 p-4 text-xs leading-5 text-hs-t2">{JSON.stringify(activeCheck, null, 2)}</pre>
          </div>

          <div className="mt-4 grid gap-2 text-sm text-hs-t2">
            {detail.repo_url ? <a className="text-hs-accent-light" href={detail.repo_url} rel="noreferrer" target="_blank">Репозиторий</a> : null}
            {detail.screencast_url ? <a className="text-hs-accent-light" href={detail.screencast_url} rel="noreferrer" target="_blank">Скринкаст</a> : null}
            {detail.doc_file ? <span>Документация: {detail.doc_file}</span> : null}
            {detail.presentation ? <span>Презентация: {detail.presentation}</span> : null}
          </div>
        </div>
      </section>

      <aside className="h-max rounded-xl border border-hs-border bg-hs-card p-5 xl:sticky xl:top-20">
        <h2 className="font-display text-lg font-bold">Экспертная оценка</h2>
        <form className="mt-4 grid gap-4" onSubmit={save}>
          {criteria.map((criterion) => (
            <label className="grid gap-2" key={criterion.id}>
              <span className="text-sm font-semibold">{criterion.name}</span>
              <input
                className="plain-input"
                max={criterion.max_score}
                min={0}
                onChange={(event) => setScores((current) => ({ ...current, [criterion.id]: { ...current[criterion.id], score: Number(event.target.value) } }))}
                type="number"
                value={scores[criterion.id]?.score ?? 0}
              />
              <textarea
                className="plain-textarea"
                onChange={(event) => setScores((current) => ({ ...current, [criterion.id]: { ...current[criterion.id], comment: event.target.value } }))}
                placeholder="Комментарий"
                value={scores[criterion.id]?.comment ?? ""}
              />
            </label>
          ))}
          <button className="btn-primary" type="submit">
            <Save className="size-4" />
            Сохранить оценки
          </button>
        </form>
      </aside>
    </div>
  );
}

function AIReviewPanel({ review }: { review: AIReview }) {
  const confidencePercent = Math.round(review.confidence * 100);

  return (
    <div className="rounded-xl border border-hs-border bg-hs-card p-5 shadow-hs-panel">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <BrainCircuit className="size-5 text-hs-cyan" />
            <h2 className="font-display text-lg font-bold">AI Review Model</h2>
            <span className="badge">{review.model_version}</span>
            <span className="badge">{verdictLabels[review.verdict] ?? review.verdict}</span>
          </div>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-hs-t2">{review.summary}</p>
        </div>

        <div className="grid min-w-[180px] grid-cols-2 gap-3">
          <div className="rounded-lg border border-hs-border bg-hs-bg p-3">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase text-hs-t3">
              <Gauge className="size-4" />
              AI-балл
            </div>
            <div className="mt-2 font-display text-2xl font-bold">{review.score.toFixed(1)}</div>
          </div>
          <div className="rounded-lg border border-hs-border bg-hs-bg p-3">
            <div className="text-xs font-semibold uppercase text-hs-t3">Уверенность</div>
            <div className="mt-2 font-display text-2xl font-bold">{confidencePercent}%</div>
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        <ReviewList icon={<CheckCircle2 className="size-4 text-hs-green" />} items={review.strengths} title="Сильные стороны" />
        <ReviewList icon={<AlertTriangle className="size-4 text-amber-300" />} items={review.risks} title="Риски" />
        <ReviewList icon={<CircleHelp className="size-4 text-hs-accent-light" />} items={review.jury_questions} title="Вопросы жюри" />
      </div>

      {review.missing_parts.length > 0 ? (
        <div className="mt-4 rounded-lg border border-amber-300/20 bg-amber-300/10 p-3 text-sm text-amber-100">
          Не хватает: {review.missing_parts.join(", ")}
        </div>
      ) : null}

      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {Object.entries(review.signals).map(([name, value]) => (
          <div className="rounded-lg border border-hs-border bg-hs-bg p-3" key={name}>
            <div className="flex items-center justify-between gap-3 text-xs text-hs-t2">
              <span>{signalLabels[name] ?? name}</span>
              <span>{Math.round(value * 100)}%</span>
            </div>
            <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-hs-gradient" style={{ width: `${Math.round(value * 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ReviewList({ icon, items, title }: { icon: ReactNode; items: string[]; title: string }) {
  return (
    <div className="rounded-lg border border-hs-border bg-hs-bg p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-bold">
        {icon}
        {title}
      </div>
      <ul className="grid gap-2 text-sm leading-5 text-hs-t2">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
