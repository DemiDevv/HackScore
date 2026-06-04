import { Code2, Play, RefreshCw } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";

import { api } from "../../api/client";
import type { AlgoLanguage, AlgoSubmission, AlgoTask, Hackathon } from "../../api/types";

const starterCode: Record<AlgoLanguage, string> = {
  python: "import sys\n\nprint(sys.stdin.read().strip())\n",
  cpp: "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  return 0;\n}\n",
  java: "import java.io.*;\n\npublic class Solution {\n  public static void main(String[] args) throws Exception {\n  }\n}\n",
};

export function AlgoTasksPage() {
  const [tasks, setTasks] = useState<AlgoTask[]>([]);
  const [selected, setSelected] = useState<AlgoTask | null>(null);
  const [attempts, setAttempts] = useState<AlgoSubmission[]>([]);
  const [language, setLanguage] = useState<AlgoLanguage>("python");
  const [sourceCode, setSourceCode] = useState(starterCode.python);

  useEffect(() => {
    void loadTasks();
  }, []);

  useEffect(() => {
    if (selected) {
      void loadAttempts(selected.id);
    }
  }, [selected]);

  async function loadTasks() {
    try {
      const { data: hackathons } = await api.get<Hackathon[]>("/hackathons/");
      const hackathon = hackathons[0];
      if (!hackathon) {
        return;
      }
      const { data } = await api.get<AlgoTask[]>(`/algo/tasks?hackathon_id=${hackathon.id}`);
      setTasks(data);
      setSelected(data[0] ?? null);
    } catch {
      toast.error("Не удалось загрузить задачи");
    }
  }

  async function loadAttempts(taskId: string) {
    try {
      const { data } = await api.get<AlgoSubmission[]>(`/algo/tasks/${taskId}/submissions`);
      setAttempts(data);
    } catch {
      setAttempts([]);
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!selected) {
      return;
    }
    try {
      await api.post(`/algo/tasks/${selected.id}/submit`, { language, source_code: sourceCode });
      toast.success("Решение отправлено");
      await loadAttempts(selected.id);
    } catch {
      toast.error("Не удалось отправить решение");
    }
  }

  function changeLanguage(next: AlgoLanguage) {
    setLanguage(next);
    setSourceCode(starterCode[next]);
  }

  return (
    <div className="grid gap-5 lg:grid-cols-[330px_1fr]">
      <aside className="rounded-xl border border-hs-border bg-hs-card p-4">
        <h1 className="font-display text-xl font-bold">Алго-задачи</h1>
        <div className="mt-4 grid gap-2">
          {tasks.map((task) => (
            <button className={`task-row ${selected?.id === task.id ? "task-row-active" : ""}`} key={task.id} onClick={() => setSelected(task)} type="button">
              <span>{task.title}</span>
              <small>{task.time_limit_ms} ms · {task.memory_limit_mb} MB</small>
            </button>
          ))}
        </div>
      </aside>

      <section className="space-y-5">
        {selected ? (
          <>
            <div className="rounded-xl border border-hs-border bg-hs-card p-5">
              <div className="flex items-start gap-3">
                <div className="grid size-10 place-items-center rounded-lg bg-hs-cyan-15 text-hs-cyan">
                  <Code2 className="size-5" />
                </div>
                <div>
                  <h2 className="font-display text-2xl font-bold">{selected.title}</h2>
                  <p className="mt-2 whitespace-pre-line text-sm leading-6 text-hs-t2">{selected.description}</p>
                </div>
              </div>
              <div className="mt-5 grid gap-3 md:grid-cols-2">
                {selected.tests.filter((test) => test.is_sample).map((test) => (
                  <div className="rounded-lg border border-hs-border bg-hs-bg p-3" key={test.id}>
                    <div className="mb-2 text-xs font-bold uppercase tracking-[0.08em] text-hs-t3">Пример</div>
                    <pre className="text-xs text-hs-t2">input: {test.input_data}output: {test.expected_output}</pre>
                  </div>
                ))}
              </div>
            </div>

            <form className="rounded-xl border border-hs-border bg-hs-card p-5" onSubmit={submit}>
              <div className="mb-3 flex items-center justify-between gap-3">
                <select className="select max-w-44" onChange={(event) => changeLanguage(event.target.value as AlgoLanguage)} value={language}>
                  <option value="python">Python</option>
                  <option value="cpp">C++</option>
                  <option value="java">Java</option>
                </select>
                <button className="btn-primary" type="submit">
                  <Play className="size-4" />
                  Отправить
                </button>
              </div>
              <textarea className="code-editor" onChange={(event) => setSourceCode(event.target.value)} value={sourceCode} />
            </form>

            <div className="rounded-xl border border-hs-border bg-hs-card p-5">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-display text-lg font-bold">Мои попытки</h2>
                <button className="btn-secondary" onClick={() => void loadAttempts(selected.id)} type="button">
                  <RefreshCw className="size-4" />
                  Обновить
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr><th>Время</th><th>Язык</th><th>Вердикт</th><th>Тесты</th><th>ms</th><th>KB</th></tr>
                  </thead>
                  <tbody>
                    {attempts.map((attempt) => (
                      <tr key={attempt.id}>
                        <td>{new Date(attempt.submitted_at).toLocaleString()}</td>
                        <td>{attempt.language}</td>
                        <td><span className="badge">{attempt.verdict}</span></td>
                        <td>{attempt.test_passed}/{attempt.test_total}</td>
                        <td>{attempt.execution_time ?? "-"}</td>
                        <td>{attempt.memory_used ?? "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="rounded-xl border border-hs-border bg-hs-card p-6 text-hs-t2">Задачи пока не созданы.</div>
        )}
      </section>
    </div>
  );
}
