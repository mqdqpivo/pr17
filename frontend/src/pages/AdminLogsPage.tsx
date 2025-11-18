import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../auth";

interface Log {
  id: number;
  user_id: number | null;
  action: string;
  details?: string | null;
  created_at: string;
}

const AdminLogsPage: React.FC = () => {
  const { hasRole } = useAuth();
  const [logs, setLogs] = useState<Log[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await axios.get<Log[]>("/admin/logs");
        setLogs(res.data);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Ошибка загрузки логов");
      }
    };
    fetchLogs();
  }, []);

  if (!hasRole(3)) {
    return <div>Недостаточно прав</div>;
  }

  return (
    <div className="page">
      <h1>Аудит действий</h1>
      {error && <div className="error">{error}</div>}
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>ID пользователя</th>
            <th>Действие</th>
            <th>Подробности</th>
            <th>Время</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>{log.id}</td>
              <td>{log.user_id ?? "-"}</td>
              <td>{log.action}</td>
              <td>{log.details ?? "-"}</td>
              <td>{new Date(log.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminLogsPage;


