import React from "react";
import { useAuth } from "../auth";

const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  const maxLevel =
    user?.roles && user.roles.length ? Math.max(...user.roles.map((r) => r.level)) : 0;

  const roleTitle =
    maxLevel === 3
      ? "Администратор"
      : maxLevel === 2
      ? "Менеджер"
      : maxLevel === 1
      ? "Пользователь"
      : "Гость";

  return (
    <div className="page">
      <h1>Панель управления</h1>
      <p>
        Вы вошли как <strong>{user?.username}</strong> ({roleTitle})
      </p>
      <ul>
        <li>Администратор видит административные разделы (пользователи, логи).</li>
        <li>Менеджер имеет доступ к административным разделам без изменения ролей.</li>
        <li>Пользователь видит только свой профиль и общие страницы.</li>
      </ul>
    </div>
  );
};

export default DashboardPage;


