import { Navigate, Outlet } from "react-router-dom";

import type { UserRole } from "../../api/types";
import { useAuthStore } from "../../store/authStore";

type ProtectedRouteProps = {
  roles?: UserRole[];
};

export function ProtectedRoute({ roles }: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated || !user) {
    return <Navigate replace to="/login" />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate replace to={defaultRouteForRole(user.role)} />;
  }

  return <Outlet />;
}

export function defaultRouteForRole(role: UserRole) {
  if (role === "participant") {
    return "/participant/hackathons";
  }
  if (role === "jury") {
    return "/jury/reviews";
  }
  return "/organizer/hackathon";
}
