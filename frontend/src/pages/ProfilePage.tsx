import React from "react";
import { useAuth } from "../auth";

const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <div>Нет данных профиля</div>;
  }

  return (
    <div className="page">
      <h1>Профиль</h1>
      <div className="card">
        <p>
          <strong>Логин:</strong> {user.username}
        </p>
        <p>
          <strong>Email:</strong> {user.email}
        </p>
        <p>
          <strong>Роли:</strong>{" "}
          {user.roles.map((r) => r.name).join(", ") || "нет ролей"}
        </p>
      </div>
    </div>
  );
};

export default ProfilePage;


