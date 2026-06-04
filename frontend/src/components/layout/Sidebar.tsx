import {
  BarChart3,
  ClipboardCheck,
  Code2,
  FileUp,
  Gauge,
  ListChecks,
  Medal,
  Settings2,
  Trophy,
  Users,
  type LucideIcon,
} from "lucide-react";
import { NavLink } from "react-router-dom";

import type { UserRole } from "../../api/types";

type SidebarProps = {
  role: UserRole;
  open: boolean;
  onClose: () => void;
};

const nav = {
  participant: [
    { section: "Хакатон", items: [{ to: "/participant/hackathons", label: "Мои хакатоны", icon: Trophy }, { to: "/participant/team", label: "Моя команда", icon: Users }] },
    { section: "Решение", items: [{ to: "/participant/submission", label: "Загрузка решения", icon: FileUp }, { to: "/participant/results", label: "Результаты", icon: BarChart3 }] },
    { section: "Алгоритмы", items: [{ to: "/participant/algo", label: "Задачи", icon: Code2 }] },
  ],
  jury: [
    { section: "Оценка", items: [{ to: "/jury/reviews", label: "Решения команд", icon: ClipboardCheck }] },
    { section: "Результаты", items: [{ to: "/jury/leaderboard", label: "Лидерборд", icon: Medal }] },
  ],
  organizer: [
    { section: "Управление", items: [{ to: "/organizer/hackathon", label: "Хакатон", icon: Settings2 }, { to: "/organizer/criteria", label: "Критерии", icon: ListChecks }, { to: "/organizer/teams", label: "Команды", icon: Users }] },
    { section: "Алгоритмы", items: [{ to: "/organizer/algo", label: "Задачи", icon: Code2 }] },
    { section: "Итоги", items: [{ to: "/organizer/leaderboard", label: "Лидерборд", icon: Gauge }] },
  ],
} satisfies Record<UserRole, Array<{ section: string; items: Array<{ to: string; label: string; icon: LucideIcon }> }>>;

export function Sidebar({ role, open, onClose }: SidebarProps) {
  return (
    <>
      <aside
        className={`fixed inset-y-[60px] left-0 z-20 w-[240px] border-r border-hs-border bg-hs-bg2 p-4 transition-transform lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <nav className="space-y-6">
          {nav[role].map((group) => (
            <div key={group.section}>
              <div className="mb-2 px-2 text-[10px] font-bold uppercase tracking-[0.08em] text-hs-t3">
                {group.section}
              </div>
              <div className="space-y-1">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink className="nav-link" key={item.to} onClick={onClose} to={item.to}>
                      <Icon className="size-4" />
                      {item.label}
                    </NavLink>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="absolute bottom-4 left-4 right-4 rounded-lg border border-hs-border bg-hs-card p-3">
          <div className="mb-2 text-xs font-semibold text-hs-t2">Статус хакатона</div>
          <div className="inline-flex items-center gap-2 rounded-full bg-hs-accent-15 px-3 py-1 text-xs font-medium text-hs-accent-light">
            <span className="size-2 rounded-full bg-hs-green" />
            В процессе
          </div>
        </div>
      </aside>
      {open ? <button aria-label="Закрыть меню" className="fixed inset-0 z-10 bg-black/50 lg:hidden" onClick={onClose} type="button" /> : null}
    </>
  );
}
