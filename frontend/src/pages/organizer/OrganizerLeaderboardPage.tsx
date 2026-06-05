import { Download, Medal } from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";

import { api } from "../../api/client";
import type { Hackathon, LeaderboardRow } from "../../api/types";

export function OrganizerLeaderboardPage() {
  const [hackathon, setHackathon] = useState<Hackathon | null>(null);
  const [rows, setRows] = useState<LeaderboardRow[]>([]);

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    try {
      const { data: hackathons } = await api.get<Hackathon[]>("/hackathons/");
      const current = hackathons[0] ?? null;
      setHackathon(current);
      if (current) {
        const { data } = await api.get<LeaderboardRow[]>(`/scoring/hackathons/${current.id}/leaderboard`);
        setRows(data);
      }
    } catch {
      toast.error("Не удалось загрузить лидерборд");
    }
  }

  async function exportCsv() {
    if (!hackathon) {
      return;
    }
    try {
      const response = await api.get(`/scoring/hackathons/${hackathon.id}/leaderboard/export`, { responseType: "blob" });
      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a");
      link.href = url;
      link.download = "leaderboard.csv";
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Не удалось экспортировать CSV");
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold">Лидерборд</h1>
          <p className="mt-2 text-sm text-hs-t2">Финальные результаты и экспорт CSV.</p>
        </div>
        <button className="btn-primary" onClick={() => void exportCsv()} type="button"><Download className="size-4" />Экспорт</button>
      </div>
      <div className="rounded-xl border border-hs-border bg-hs-card p-5">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead><tr><th>Место</th><th>Команда</th><th>Авто</th><th>Экспертные</th><th>Итого</th></tr></thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.team_id}>
                  <td><Medal className="inline size-4 text-hs-accent-light" /> {row.rank}</td>
                  <td>{row.team_name}</td>
                  <td>{Object.entries(row.auto_scores).map(([name, score]) => `${name}: ${score ?? "-"}`).join(" · ")}</td>
                  <td>{row.expert_scores.map((score) => `${score.criterion}: ${score.avg_score ?? "-"}`).join(" · ")}</td>
                  <td className="font-bold">{row.total_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
