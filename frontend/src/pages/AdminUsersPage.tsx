import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../auth";

interface Role {
  id: number;
  name: string;
  level: number;
}

interface User {
  id: number;
  username: string;
  email: string;
  roles: Role[];
}

const AdminUsersPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [usersRes, rolesRes] = await Promise.all([
          axios.get<User[]>("/users/"),
          axios.get<Role[]>("/admin/roles")
        ]);
        setUsers(usersRes.data);
        setRoles(rolesRes.data);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Ошибка загрузки данных");
      }
    };
    fetchData();
  }, []);

  const handleChangeRoles = async (userId: number, roleName: string) => {
    try {
      const user = users.find((u) => u.id === userId);
      if (!user) return;
      const hasRoleAlready = user.roles.some((r) => r.name === roleName);
      const newRoles = hasRoleAlready
        ? user.roles.filter((r) => r.name !== roleName)
        : [...user.roles, roles.find((r) => r.name === roleName)!];
      const res = await axios.put<User>(`/users/${userId}/roles`, {
        roles: newRoles.map((r) => r.name)
      });
      setUsers((prev) => prev.map((u) => (u.id === userId ? res.data : u)));
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Ошибка изменения ролей");
    }
  };

  if (!hasRole(3)) {
    return <div>Недостаточно прав</div>;
  }

  return (
    <div className="page">
      <h1>Пользователи</h1>
      {error && <div className="error">{error}</div>}
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Логин</th>
            <th>Email</th>
            <th>Роли</th>
            <th>Назначение ролей</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.username}</td>
              <td>{u.email}</td>
              <td>{u.roles.map((r) => r.name).join(", ")}</td>
              <td>
                {roles.map((r) => (
                  <label key={r.id} className="role-badge">
                    <input
                      type="checkbox"
                      checked={u.roles.some((ur) => ur.name === r.name)}
                      onChange={() => handleChangeRoles(u.id, r.name)}
                    />
                    {r.name}
                  </label>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminUsersPage;


