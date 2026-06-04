import { Save } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { Link, useParams } from "react-router-dom";

import { api } from "../../api/client";
import type { CheckType, Criterion, Hackathon, ReviewDetail } from "../../api/types";

const tabs: CheckType[] = ["code", "documentation", "presentation", "screencast"];

export function ReviewDetailPage() {
  const { submissionId } = useParams();
  const [detail, setDetail] = useState<ReviewDetail | null>(null);
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [activeTab, setActiveTab] = useState<CheckType>("code");
  const [scores, setScores] = useState<Record<string, { score: number; comment: string }>>({});

  useEffect(() => {
    void load();
  }, [submissionId]);

  async function load() {
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
  }

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
