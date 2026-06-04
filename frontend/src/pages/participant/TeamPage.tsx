import { Crown, Mail, Plus, Trash2, Users } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";

import { api } from "../../api/client";
import type { Hackathon, Team } from "../../api/types";
import { useAuthStore } from "../../store/authStore";

export function TeamPage() {
  const user = useAuthStore((state) => state.user);
  const [team, setTeam] = useState<Team | null>(null);
  const [email, setEmail] = useState("");

  useEffect(() => {
    void loadTeam();
  }, []);

  async function loadTeam() {
    try {
      const { data: hackathons } = await api.get<Hackathon[]>("/hackathons/");
      for (const hackathon of hackathons) {
        const { data: teams } = await api.get<Team[]>(`/hackathons/${hackathon.id}/teams/`);
        const myTeam = teams.find((item) => item.members.some((member) => member.user_id === user?.id));
        if (myTeam) {
          setTeam(myTeam);
          return;
        }
      }
      setTeam(null);
    } catch {
      toast.error("Не удалось загрузить команду");
    }
  }

  async function invite(event: FormEvent) {
    event.preventDefault();
    if (!team || !email.trim()) {
      return;
    }
    try {
      const { data } = await api.post<Team>(`/hackathons/${team.hackathon_id}/teams/${team.id}/members`, { email });
      setTeam(data);
      setEmail("");
      toast.success("Участник добавлен");
    } catch {
      toast.error("Не удалось добавить участника");
    }
  }

  async function remove(userId: string) {
    if (!team) {
      return;
    }
    try {
      const { data } = await api.delete<Team>(`/hackathons/${team.hackathon_id}/teams/${team.id}/members/${userId}`);
      setTeam(data);
    } catch {
      toast.error("Не удалось удалить участника");
    }
  }

  if (!team) {
    return (
      <div className="rounded-xl border border-hs-border bg-hs-card p-6">
        <h1 className="font-display text-2xl font-bold">Моя команда</h1>
        <p className="mt-2 text-sm text-hs-t2">Команда пока не найдена. Создайте ее на странице хакатонов.</p>
      </div>
    );
  }

  const isCaptain = team.members.some((member) => member.user_id === user?.id && member.is_captain);

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_360px]">
      <section className="rounded-xl border border-hs-border bg-hs-card p-5">
        <div className="flex items-center gap-3">
          <div className="grid size-10 place-items-center rounded-lg bg-hs-cyan-15 text-hs-cyan">
            <Users className="size-5" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold">{team.name}</h1>
            <p className="text-sm text-hs-t2">Участников: {team.members.length}</p>
          </div>
        </div>

        <div className="mt-6 divide-y divide-hs-border rounded-lg border border-hs-border">
          {team.members.map((member) => (
            <div className="flex items-center justify-between gap-3 p-4" key={member.id}>
              <div>
                <div className="flex items-center gap-2 font-semibold">
                  {member.full_name}
                  {member.is_captain ? <Crown className="size-4 text-hs-cyan" /> : null}
                </div>
                <div className="mt-1 text-sm text-hs-t2">{member.email}</div>
              </div>
              {isCaptain && !member.is_captain ? (
                <button className="icon-button" onClick={() => void remove(member.user_id)} type="button">
                  <Trash2 className="size-4" />
                </button>
              ) : null}
            </div>
          ))}
        </div>
      </section>

      <aside className="rounded-xl border border-hs-border bg-hs-card p-5">
        <h2 className="font-display text-lg font-bold">Пригласить участника</h2>
        <form className="mt-4 grid gap-3" onSubmit={invite}>
          <div className="input-shell">
            <Mail className="size-4 text-hs-t3" />
            <input disabled={!isCaptain} onChange={(event) => setEmail(event.target.value)} placeholder="email участника" value={email} />
          </div>
          <button className="btn-primary" disabled={!isCaptain} type="submit">
            <Plus className="size-4" />
            Добавить
          </button>
        </form>
      </aside>
    </div>
  );
}
