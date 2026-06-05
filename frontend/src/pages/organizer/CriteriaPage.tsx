import { Plus, Trash2 } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";

import { api } from "../../api/client";
import type { Criterion, Hackathon } from "../../api/types";

export function CriteriaPage() {
  const [hackathon, setHackathon] = useState<Hackathon | null>(null);
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [name, setName] = useState("");
  const [weight, setWeight] = useState(0.1);
  const [isAuto, setIsAuto] = useState(false);

  useEffect(() => {
    void load();
  }, []);

  const totalWeight = useMemo(() => criteria.reduce((sum, criterion) => sum + criterion.weight, 0), [criteria]);

  async function load() {
    try {
      const { data: hackathons } = await api.get<Hackathon[]>("/hackathons/");
      const current = hackathons[0] ?? null;
      setHackathon(current);
      if (current) {
        const { data } = await api.get<Criterion[]>(`/hackathons/${current.id}/criteria/`);
        setCriteria(data);
      }
    } catch {
      toast.error("Не удалось загрузить критерии");
    }
  }

  async function create(event: FormEvent) {
    event.preventDefault();
    if (!hackathon) {
      return;
    }
    try {
      await api.post(`/hackathons/${hackathon.id}/criteria/`, { name, weight, is_auto: isAuto, max_score: 10 });
      setName("");
      toast.success("Критерий добавлен");
      await load();
    } catch {
      toast.error("Не удалось добавить критерий");
    }
  }

  async function remove(id: string) {
    if (!hackathon) {
      return;
    }
    try {
      await api.delete(`/hackathons/${hackathon.id}/criteria/${id}`);
      await load();
    } catch {
      toast.error("Не удалось удалить критерий");
    }
  }

  async function loadPreset() {
    if (!hackathon) {
      return;
    }
    const preset = [
      ["Полнота MVP", 0.2, true],
      ["Архитектура и качество кода", 0.1, true],
      ["UX/UI", 0.1, false],
      ["Документация", 0.07, true],
    ] as const;
    try {
      for (const [presetName, presetWeight, presetAuto] of preset) {
        if (!criteria.some((criterion) => criterion.name === presetName)) {
          await api.post(`/hackathons/${hackathon.id}/criteria/`, { name: presetName, weight: presetWeight, is_auto: presetAuto, max_score: 10 });
        }
      }
      await load();
    } catch {
      toast.error("Не удалось загрузить шаблон");
    }
  }

  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-hs-border bg-hs-card p-5">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h1 className="font-display text-2xl font-bold">Критерии оценки</h1>
            <p className="mt-2 text-sm text-hs-t2">Сумма весов: {(totalWeight * 100).toFixed(1)}%</p>
          </div>
          <button className="btn-secondary" onClick={() => void loadPreset()} type="button">Загрузить стандартные</button>
        </div>
        <div className="mt-4 h-2 overflow-hidden rounded-full bg-hs-bg">
          <div className="h-full bg-hs-gradient" style={{ width: `${Math.min(totalWeight, 1) * 100}%` }} />
        </div>
      </div>

      <form className="rounded-xl border border-hs-border bg-hs-card p-4" onSubmit={create}>
        <div className="grid gap-3 md:grid-cols-[1fr_160px_130px_auto]">
          <input className="plain-input" onChange={(event) => setName(event.target.value)} placeholder="Название критерия" value={name} />
          <input className="plain-input" max={1} min={0} onChange={(event) => setWeight(Number(event.target.value))} step={0.01} type="number" value={weight} />
          <label className="flex items-center gap-2 text-sm text-hs-t2"><input checked={isAuto} onChange={(event) => setIsAuto(event.target.checked)} type="checkbox" /> Авто</label>
          <button className="btn-primary" type="submit"><Plus className="size-4" />Добавить</button>
        </div>
      </form>

      <div className="grid gap-3">
        {criteria.map((criterion) => (
          <div className="rounded-xl border border-hs-border bg-hs-card p-4" key={criterion.id}>
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="font-display font-bold">{criterion.name}</div>
                <div className="mt-1 text-sm text-hs-t2">{criterion.is_auto ? "Авто" : "Эксперт"} · вес {(criterion.weight * 100).toFixed(1)}%</div>
              </div>
              <button className="icon-button" onClick={() => void remove(criterion.id)} type="button"><Trash2 className="size-4" /></button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
