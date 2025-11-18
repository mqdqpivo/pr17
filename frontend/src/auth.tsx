import React, { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export type Role = "guest" | "user" | "manager" | "admin";

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  roles: { id: number; name: Role; level: number }[];
}

interface AuthContextValue {
  token: string | null;
  user: UserProfile | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (data: {
    username: string;
    email: string;
    password: string;
    confirm_password: string;
  }) => Promise<void>;
  logout: () => void;
  hasRole: (minLevel: number) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const API_BASE_URL = "http://localhost:8000";

axios.defaults.baseURL = API_BASE_URL;

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`
    };
  }
  return config;
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem("token")
  );
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const res = await axios.get<UserProfile>("/auth/me");
        setUser(res.data);
      } catch {
        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [token]);

  const login = async (username: string, password: string) => {
    const res = await axios.post<{ access_token: string }>("/auth/login", {
      username,
      password
    });
    const accessToken = res.data.access_token;
    localStorage.setItem("token", accessToken);
    setToken(accessToken);
    const profile = await axios.get<UserProfile>("/auth/me");
    setUser(profile.data);
    navigate("/dashboard");
  };

  const register = async (data: {
    username: string;
    email: string;
    password: string;
    confirm_password: string;
  }) => {
    const res = await axios.post<{ access_token: string }>("/auth/register", data);
    const accessToken = res.data.access_token;
    localStorage.setItem("token", accessToken);
    setToken(accessToken);
    const profile = await axios.get<UserProfile>("/auth/me");
    setUser(profile.data);
    navigate("/dashboard");
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    navigate("/login");
  };

  const hasRole = (minLevel: number): boolean => {
    if (!user) return false;
    const levels = user.roles.map((r) => r.level);
    return levels.length ? Math.max(...levels) >= minLevel : false;
  };

  return (
    <AuthContext.Provider
      value={{ token, user, loading, login, register, logout, hasRole }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};


