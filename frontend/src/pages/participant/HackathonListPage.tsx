import { ArrowRight, Plus, Trophy } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Link } from "react-router-dom";

import { api } from "../../api/client";
import type { Hackathon, Team } from "../../api/types";

export function HackathonListPage() {
  const [hackathons, setHackathons] = useState<Hackathon[]>([]);
  const [teams, setTeams] = useState<Record<string, Team[]>>({});
  const [teamName, setTeamName] = useState("");
  const [selectedHackathon, setSelectedHackathon] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    setLoading(true);
    try {
      const { data } = await api.get<Hackathon[]>("/hackathons/");
      setHackathons(data);
      const teamsByHackathon: Record<string, Team[]> = {};
      await Promise.all(
        data.map(async (hackathon) => {
          const response = await api.get<Team[]>(`/hackathons/${hackathon.id}/teams/`);
          teamsByHackathon[hackathon.id] = response.data;
        }),
      );
      setTeams(teamsByHackathon);
      setSelectedHackathon(data[0]?.id ?? null);
    } catch {
      toast.error("Не удалось загрузить хакатоны");
    } finally {
      setLoading(false);
    }
  }

  async function createTeam(event: FormEvent) {
    event.preventDefault();
    if (!selectedHackathon || !teamName.trim()) {
      return;
    }
    try {
      await api.post(`/hackathons/${selectedHackathon}/teams/`, { name: teamName });
      setTeamName("");
      toast.success("Команда создана");
      await load();
    } catch {
      toast.error("Не удалось создать команду");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <h1 className="font-display text-2xl font-bold">Мои хакатоны</h1>
          <p className="mt-2 text-sm text-hs-t2">Доступные соревнования и ваши команды.</p>
        </div>
      </div>

      <form className="rounded-xl border border-hs-border bg-hs-card p-4" onSubmit={createTeam}>
        <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
          <select className="select" onChange={(event) => setSelectedHackathon(event.target.value)} value={selectedHackathon ?? ""}>
            {hackathons.map((hackathon) => (
              <option key={hackathon.id} value={hackathon.id}>
                {hackathon.title}
              </option>
            ))}
          </select>
          <input className="plain-input" onChange={(event) => setTeamName(event.target.value)} placeholder="Название команды" value={teamName} />
          <button className="btn-primary" type="submit">
            <Plus className="size-4" />
            Создать команду
          </button>
        </div>
      </form>

      {loading ? <div className="rounded-xl border border-hs-border bg-hs-card p-6 text-hs-t2">Загрузка...</div> : null}

      <div className="grid gap-4 lg:grid-cols-2">
        {hackathons.map((hackathon) => {
          const hackathonTeams = teams[hackathon.id] ?? [];
          const members = hackathonTeams.reduce((sum, team) => sum + team.members.length, 0);
          return (
            <article className="rounded-xl border border-hs-border bg-hs-card p-5 shadow-hs-panel" key={hackathon.id}>
              <div className="flex items-start gap-3">
                <div className="grid size-10 place-items-center rounded-lg bg-hs-accent-15 text-hs-accent-light">
                  <Trophy className="size-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <h2 className="font-display text-lg font-bold">{hackathon.title}</h2>
                  <p className="mt-2 line-clamp-2 text-sm text-hs-t2">{hackathon.description}</p>
                </div>
              </div>
              <div className="mt-5 grid gap-3 text-sm text-hs-t2 sm:grid-cols-3">
                <div>Статус: <span className="badge">{hackathon.status}</span></div>
                <div>Команд: {hackathonTeams.length}</div>
                <div>Участников: {members}</div>
              </div>
              <Link className="btn-secondary mt-5" to="/participant/submission">
                Перейти
                <ArrowRight className="size-4" />
              </Link>
            </article>
          );
        })}
      </div>
    </div>
  );
}
