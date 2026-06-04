import { ClipboardCheck, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { Link } from "react-router-dom";

import { api } from "../../api/client";
import type { Hackathon, ReviewSubmissionSummary } from "../../api/types";

export function ReviewListPage() {
  const [items, setItems] = useState<ReviewSubmissionSummary[]>([]);
  const [filter, setFilter] = useState<"all" | "mine" | "pending">("all");
  const [query, setQuery] = useState("");

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
      const { data } = await api.get<ReviewSubmissionSummary[]>(`/scoring/hackathons/${hackathon.id}/submissions`);
      setItems(data);
    } catch {
      toast.error("Не удалось загрузить решения");
    }
  }

  const filtered = useMemo(() => {
    return items.filter((item) => {
      if (filter === "mine" && item.my_score === null) {
        return false;
      }
      if (filter === "pending" && item.my_score !== null) {
        return false;
      }
      return item.team_name.toLowerCase().includes(query.toLowerCase());
    });
  }, [filter, items, query]);

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h1 className="font-display text-2xl font-bold">Решения команд</h1>
          <p className="mt-2 text-sm text-hs-t2">Автопроверки и экспертные оценки.</p>
        </div>
        <div className="input-shell max-w-sm">
          <Search className="size-4 text-hs-t3" />
          <input onChange={(event) => setQuery(event.target.value)} placeholder="Поиск команды" value={query} />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {(["all", "pending", "mine"] as const).map((value) => (
          <button className={`filter-pill ${filter === value ? "filter-pill-active" : ""}`} key={value} onClick={() => setFilter(value)} type="button">
            {value === "all" ? "Все" : value === "pending" ? "Ожидают оценки" : "Оценены мной"}
          </button>
        ))}
      </div>

      <div className="rounded-xl border border-hs-border bg-hs-card p-5">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr><th>Команда</th><th>Статус</th><th>Авто-балл</th><th>Моя оценка</th><th>Проверки</th><th /></tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.submission_id}>
                  <td>
                    <div className="flex items-center gap-2 font-semibold">
                      <ClipboardCheck className="size-4 text-hs-accent-light" />
                      {item.team_name}
                    </div>
                  </td>
                  <td><span className="badge">{item.status}</span></td>
                  <td>{item.auto_score ?? "-"}</td>
                  <td>{item.my_score ?? "-"}</td>
                  <td>{item.checks.length}</td>
                  <td>
                    <Link className="btn-secondary" to={`/jury/reviews/${item.submission_id}`}>
                      Оценить
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
