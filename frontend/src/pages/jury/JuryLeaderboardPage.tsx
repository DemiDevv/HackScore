import { Medal } from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";

import { api } from "../../api/client";
import type { Hackathon, LeaderboardRow } from "../../api/types";

export function JuryLeaderboardPage() {
  const [rows, setRows] = useState<LeaderboardRow[]>([]);

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    try {
      const { data: hackathons } = await api.get<Hackathon[]>("/hackathons/");
      const hackathon = hackathons[0];
      if (!hackathon) {
        return;
      }
      const { data } = await api.get<LeaderboardRow[]>(`/scoring/hackathons/${hackathon.id}/leaderboard`);
      setRows(data);
    } catch {
      toast.error("Не удалось загрузить лидерборд");
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="font-display text-2xl font-bold">Лидерборд</h1>
        <p className="mt-2 text-sm text-hs-t2">Итоговые баллы команд.</p>
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
