import { Users } from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";

import { api } from "../../api/client";
import type { Hackathon, Submission, Team } from "../../api/types";

export function TeamsOverviewPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [submissions, setSubmissions] = useState<Record<string, Submission | null>>({});

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
      const { data } = await api.get<Team[]>(`/hackathons/${hackathon.id}/teams/`);
      setTeams(data);
      const byTeam: Record<string, Submission | null> = {};
      await Promise.all(data.map(async (team) => {
        try {
          const response = await api.get<Submission>(`/submissions/team/${team.id}`);
          byTeam[team.id] = response.data;
        } catch {
          byTeam[team.id] = null;
        }
      }));
      setSubmissions(byTeam);
    } catch {
      toast.error("Не удалось загрузить команды");
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="font-display text-2xl font-bold">Команды</h1>
        <p className="mt-2 text-sm text-hs-t2">Участники, submission и прогресс проверок.</p>
      </div>
      <div className="rounded-xl border border-hs-border bg-hs-card p-5">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead><tr><th>Команда</th><th>Участники</th><th>Submission</th><th>Артефакты</th><th>Проверки</th></tr></thead>
            <tbody>
              {teams.map((team) => {
                const submission = submissions[team.id];
                const artifacts = submission ? [submission.repo_url || submission.repo_archive, submission.doc_file, submission.presentation, submission.screencast_file || submission.screencast_url].filter(Boolean).length : 0;
                return (
                  <tr key={team.id}>
                    <td><Users className="mr-2 inline size-4 text-hs-cyan" />{team.name}</td>
                    <td>{team.members.length}</td>
                    <td><span className="badge">{submission?.status ?? "missing"}</span></td>
                    <td>{artifacts}/4</td>
                    <td>{submission?.check_results.length ?? 0}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
