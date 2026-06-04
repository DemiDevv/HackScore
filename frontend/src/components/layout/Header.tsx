import { Bell, LogOut, Menu, Trophy } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useAuthStore } from "../../store/authStore";

type HeaderProps = {
  onToggleSidebar: () => void;
};

const roleLabels = {
  participant: "Участник",
  jury: "Жюри",
  organizer: "Организатор",
};

export function Header({ onToggleSidebar }: HeaderProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="sticky top-0 z-30 border-b border-white/5 bg-hs-card/75 backdrop-blur-2xl">
      <div className="flex h-[60px] items-center justify-between px-4 lg:px-6">
        <div className="flex items-center gap-3">
          <button className="icon-button lg:hidden" onClick={onToggleSidebar} type="button">
            <Menu className="size-5" />
          </button>
          <div className="grid size-9 place-items-center rounded-lg bg-hs-gradient shadow-hs-glow">
            <Trophy className="size-5" />
          </div>
          <span className="font-display text-lg font-bold text-gradient">HackScore</span>
        </div>

        <div className="flex items-center gap-3">
          <button className="icon-button hidden sm:grid" type="button">
            <Bell className="size-5" />
          </button>
          <div className="hidden text-right sm:block">
            <div className="text-sm font-semibold">{user?.full_name}</div>
            <div className="text-xs text-hs-t2">{user ? roleLabels[user.role] : ""}</div>
          </div>
          <button className="icon-button" onClick={handleLogout} type="button">
            <LogOut className="size-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
