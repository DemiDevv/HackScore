import { useState } from "react";
import { Outlet } from "react-router-dom";

import { useAuthStore } from "../../store/authStore";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-hs-bg text-hs-t1">
      <Header onToggleSidebar={() => setSidebarOpen((value) => !value)} />
      <Sidebar onClose={() => setSidebarOpen(false)} open={sidebarOpen} role={user.role} />
      <main className="min-h-[calc(100vh-60px)] px-4 py-6 lg:ml-[240px] lg:px-7">
        <div className="mx-auto max-w-6xl animate-fade-in">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
