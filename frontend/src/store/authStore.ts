import { create } from "zustand";

import { api } from "../api/client";
import type { AuthResponse, User, UserRole } from "../api/types";

type AuthState = {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
};

type RegisterPayload = {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
};

function readStoredUser(): User | null {
  const raw = localStorage.getItem("hackscore_user");
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as User;
  } catch {
    localStorage.removeItem("hackscore_user");
    return null;
  }
}

function persistAuth(response: AuthResponse) {
  localStorage.setItem("hackscore_token", response.access_token);
  localStorage.setItem("hackscore_user", JSON.stringify(response.user));
}

export const useAuthStore = create<AuthState>((set) => {
  const token = localStorage.getItem("hackscore_token");
  const user = readStoredUser();

  return {
    user,
    token,
    isAuthenticated: Boolean(token && user),
    isLoading: false,

    async login(email, password) {
      set({ isLoading: true });
      try {
        const { data } = await api.post<AuthResponse>("/auth/login", { email, password });
        persistAuth(data);
        set({ token: data.access_token, user: data.user, isAuthenticated: true });
      } finally {
        set({ isLoading: false });
      }
    },

    async register(payload) {
      set({ isLoading: true });
      try {
        const { data } = await api.post<AuthResponse>("/auth/register", payload);
        persistAuth(data);
        set({ token: data.access_token, user: data.user, isAuthenticated: true });
      } finally {
        set({ isLoading: false });
      }
    },

    logout() {
      localStorage.removeItem("hackscore_token");
      localStorage.removeItem("hackscore_user");
      set({ token: null, user: null, isAuthenticated: false });
    },
  };
});
