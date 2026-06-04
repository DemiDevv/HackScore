import { Plus } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";

import { api } from "../../api/client";
import type { AlgoTask, Hackathon } from "../../api/types";

export function AlgoManagePage() {
  const [hackathon, setHackathon] = useState<Hackathon | null>(null);
  const [tasks, setTasks] = useState<AlgoTask[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [inputData, setInputData] = useState("");
  const [expectedOutput, setExpectedOutput] = useState("");
  const [selectedTask, setSelectedTask] = useState<AlgoTask | null>(null);

  useEffect(() => {
    void load();
  }, []);

  async function load() {
    const { data: hackathons } = await api.get<Hackathon[]>("/hackathons/");
    const current = hackathons[0] ?? null;
    setHackathon(current);
    if (current) {
      const { data } = await api.get<AlgoTask[]>(`/algo/tasks?hackathon_id=${current.id}`);
      setTasks(data);
      setSelectedTask(data[0] ?? null);
    }
  }

  async function createTask(event: FormEvent) {
    event.preventDefault();
    if (!hackathon) {
      return;
    }
    try {
      await api.post("/algo/tasks", { hackathon_id: hackathon.id, title, description, time_limit_ms: 1000, memory_limit_mb: 256 });
      setTitle("");
      setDescription("");
      await load();
      toast.success("Задача создана");
    } catch {
      toast.error("Не удалось создать задачу");
    }
  }

  async function addTest(event: FormEvent) {
    event.preventDefault();
    if (!selectedTask) {
      return;
    }
    try {
      await api.post(`/algo/tasks/${selectedTask.id}/tests`, [{ input_data: inputData, expected_output: expectedOutput, is_sample: false }]);
      setInputData("");
      setExpectedOutput("");
      await load();
      toast.success("Тест добавлен");
    } catch {
      toast.error("Не удалось добавить тест");
    }
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[1fr_380px]">
      <section className="rounded-xl border border-hs-border bg-hs-card p-5">
        <h1 className="font-display text-2xl font-bold">Алго-задачи</h1>
        <form className="mt-5 grid gap-3" onSubmit={createTask}>
          <input className="plain-input" onChange={(event) => setTitle(event.target.value)} placeholder="Название" value={title} />
          <textarea className="plain-textarea min-h-40" onChange={(event) => setDescription(event.target.value)} placeholder="Условие Markdown" value={description} />
          <button className="btn-primary" type="submit"><Plus className="size-4" />Создать задачу</button>
        </form>

        <div className="mt-6 grid gap-2">
          {tasks.map((task) => (
            <button className={`task-row ${selectedTask?.id === task.id ? "task-row-active" : ""}`} key={task.id} onClick={() => setSelectedTask(task)} type="button">
              <span>{task.title}</span>
              <small>{task.tests.length} тестов · {task.time_limit_ms} ms</small>
            </button>
          ))}
        </div>
      </section>

      <aside className="rounded-xl border border-hs-border bg-hs-card p-5">
        <h2 className="font-display text-lg font-bold">Добавить тест</h2>
        <form className="mt-4 grid gap-3" onSubmit={addTest}>
          <textarea className="plain-textarea" onChange={(event) => setInputData(event.target.value)} placeholder="input" value={inputData} />
          <textarea className="plain-textarea" onChange={(event) => setExpectedOutput(event.target.value)} placeholder="expected output" value={expectedOutput} />
          <button className="btn-primary" disabled={!selectedTask} type="submit">Добавить</button>
        </form>
      </aside>
    </div>
  );
}
