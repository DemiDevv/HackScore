import { BarChart3 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";

import { api } from "../../api/client";
import type { Hackathon, Submission, Team } from "../../api/types";
import { useAuthStore } from "../../store/authStore";

export function ResultsPage() {
  const user = useAuthStore((state) => state.user);
  const [submission, setSubmission] = useState<Submission | null>(null);

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    try {
      const { data: hackathons } = await api.get<Hackathon[]>("/hackathons/");
      for (const hackathon of hackathons) {
        const { data: teams } = await api.get<Team[]>(`/hackathons/${hackathon.id}/teams/`);
        const myTeam = teams.find((team) => team.members.some((member) => member.user_id === user?.id));
        if (myTeam) {
          const response = await api.get<Submission>(`/submissions/team/${myTeam.id}`);
          setSubmission(response.data);
          return;
        }
      }
    } catch {
      toast.error("Не удалось загрузить результаты");
    }
  }

  const total = useMemo(() => {
    const scores = submission?.check_results.map((check) => check.score).filter((score): score is number => score !== null) ?? [];
    return scores.length ? (scores.reduce((sum, score) => sum + score, 0) / scores.length).toFixed(2) : "-";
  }, [submission]);

  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-hs-border bg-hs-card p-6">
        <div className="flex items-center gap-4">
          <div className="grid size-14 place-items-center rounded-xl bg-hs-gradient shadow-hs-glow">
            <BarChart3 className="size-7" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold">Мои результаты</h1>
            <p className="mt-1 text-sm text-hs-t2">Средний автоматический балл</p>
          </div>
          <div className="ml-auto font-display text-4xl font-bold">{total}</div>
        </div>
      </div>

      <div className="rounded-xl border border-hs-border bg-hs-card p-5">
        <h2 className="font-display text-lg font-bold">Автопроверки</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr><th>Тип</th><th>Статус</th><th>Балл</th><th>Завершено</th></tr>
            </thead>
            <tbody>
              {submission?.check_results.map((check) => (
                <tr key={check.id}>
                  <td>{check.check_type}</td>
                  <td><span className="badge">{check.status}</span></td>
                  <td>{check.score ?? "-"}</td>
                  <td>{check.completed_at ? new Date(check.completed_at).toLocaleString() : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
