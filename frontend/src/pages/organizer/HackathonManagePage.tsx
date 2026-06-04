import { Save } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";

import { api } from "../../api/client";
import type { Hackathon, HackathonStatus } from "../../api/types";

const statuses: HackathonStatus[] = ["draft", "registration", "in_progress", "judging", "finished"];

export function HackathonManagePage() {
  const [hackathons, setHackathons] = useState<Hackathon[]>([]);
  const [selected, setSelected] = useState<Hackathon | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    const { data } = await api.get<Hackathon[]>("/hackathons/");
    setHackathons(data);
    const first = data[0] ?? null;
    setSelected(first);
    setTitle(first?.title ?? "");
    setDescription(first?.description ?? "");
  }

  async function save(event: FormEvent) {
    event.preventDefault();
    try {
      if (selected) {
        const { data } = await api.put<Hackathon>(`/hackathons/${selected.id}`, { title, description });
        setSelected(data);
      } else {
        const { data } = await api.post<Hackathon>("/hackathons/", { title, description, status: "draft" });
        setSelected(data);
      }
      toast.success("Хакатон сохранен");
      await load();
    } catch {
      toast.error("Не удалось сохранить хакатон");
    }
  }

  async function changeStatus(status: HackathonStatus) {
    if (!selected) {
      return;
    }
    try {
      const { data } = await api.put<Hackathon>(`/hackathons/${selected.id}/status`, { status });
      setSelected(data);
      toast.success("Статус обновлен");
    } catch {
      toast.error("Не удалось обновить статус");
    }
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_360px]">
      <section className="rounded-xl border border-hs-border bg-hs-card p-5">
        <h1 className="font-display text-2xl font-bold">Управление хакатоном</h1>
        <form className="mt-5 grid gap-4" onSubmit={save}>
          <label className="field">
            <span>Название</span>
            <input className="plain-input" onChange={(event) => setTitle(event.target.value)} value={title} />
          </label>
          <label className="field">
            <span>Описание</span>
            <textarea className="plain-textarea min-h-36" onChange={(event) => setDescription(event.target.value)} value={description} />
          </label>
          <button className="btn-primary" type="submit">
            <Save className="size-4" />
            Сохранить
          </button>
        </form>
      </section>

      <aside className="space-y-5">
        <div className="rounded-xl border border-hs-border bg-hs-card p-5">
          <h2 className="font-display text-lg font-bold">Фаза</h2>
          <div className="mt-4 grid gap-2">
            {statuses.map((status) => (
              <button className={`task-row ${selected?.status === status ? "task-row-active" : ""}`} key={status} onClick={() => void changeStatus(status)} type="button">
                <span>{status}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-hs-border bg-hs-card p-5">
          <h2 className="font-display text-lg font-bold">Хакатоны</h2>
          <div className="mt-4 grid gap-2">
            {hackathons.map((hackathon) => (
              <button className="task-row" key={hackathon.id} onClick={() => { setSelected(hackathon); setTitle(hackathon.title); setDescription(hackathon.description ?? ""); }} type="button">
                <span>{hackathon.title}</span>
                <small>{hackathon.status}</small>
              </button>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
