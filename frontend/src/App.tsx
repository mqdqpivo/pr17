import React from "react";
import { Link, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import { PrivateRoute } from "./components/PrivateRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import ProfilePage from "./pages/ProfilePage";
import SettingsPage from "./pages/SettingsPage";
import AdminUsersPage from "./pages/AdminUsersPage";
import AdminLogsPage from "./pages/AdminLogsPage";

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout, hasRole } = useAuth();

  const maxLevel =
    user?.roles && user.roles.length ? Math.max(...user.roles.map((r) => r.level)) : 0;

  return (
    <div className="app">
      <header className="navbar">
        <div className="navbar-left">
          <span className="logo">RBAC Demo</span>
          <nav>
            {user && (
              <>
                <Link to="/dashboard">Главная</Link>
                <Link to="/profile">Профиль</Link>
                <Link to="/settings">Настройки</Link>
                {hasRole(2) && <Link to="/admin/users">Пользователи</Link>}
                {hasRole(3) && <Link to="/admin/logs">Логи</Link>}
              </>
            )}
          </nav>
        </div>
        <div className="navbar-right">
          {user ? (
            <>
              <span className="user-info">
                {user.username} (уровень {maxLevel})
              </span>
              <button onClick={logout}>Выход</button>
            </>
          ) : (
            <>
              <Link to="/login">Вход</Link>
              <Link to="/register">Регистрация</Link>
            </>
          )}
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
};

const AppRoutes: React.FC = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
    <Route
      path="/dashboard"
      element={
        <PrivateRoute>
          <DashboardPage />
        </PrivateRoute>
      }
    />
    <Route
      path="/profile"
      element={
        <PrivateRoute>
          <ProfilePage />
        </PrivateRoute>
      }
    />
    <Route
      path="/settings"
      element={
        <PrivateRoute>
          <SettingsPage />
        </PrivateRoute>
      }
    />
    <Route
      path="/admin/users"
      element={
        <PrivateRoute minLevel={3}>
          <AdminUsersPage />
        </PrivateRoute>
      }
    />
    <Route
      path="/admin/logs"
      element={
        <PrivateRoute minLevel={3}>
          <AdminLogsPage />
        </PrivateRoute>
      }
    />
    <Route
      path="/"
      element={
        <PrivateRoute>
          <DashboardPage />
        </PrivateRoute>
      }
    />
  </Routes>
);

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Layout>
        <AppRoutes />
      </Layout>
    </AuthProvider>
  );
};

export default App;


