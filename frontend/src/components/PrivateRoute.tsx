import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth";

interface Props {
  children: React.ReactElement;
  minLevel?: number;
}

export const PrivateRoute: React.FC<Props> = ({ children, minLevel = 1 }) => {
  const { token, loading, hasRole } = useAuth();

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (!hasRole(minLevel)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};


