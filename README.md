## Веб‑приложение с регистрацией, входом и разграничением прав доступа (RBAC)

Проект состоит из **backend** на FastAPI и **frontend** на React (SPA) с JWT‑аутентификацией и ролями:

- **Роли**: `guest` (0), `user` (1), `manager` (2), `admin` (3).
- Регистрация, вход по логину/паролю, выдача JWT.
- Разные разделы интерфейса в зависимости от роли.
- Админ‑панель: управление пользователями и просмотр аудита действий.

### 1. Стек технологий

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, JWT (python-jose), bcrypt (passlib).
- **Frontend**: React + TypeScript + Vite, React Router, Axios.
- **БД**: PostgreSQL, таблицы `users`, `roles`, `user_roles`, `audit_logs`.

---

### 2. Запуск backend

1. Установите Python 3.10+ и PostgreSQL.
2. Создайте БД и пользователя (из `backend/db_init.sql`):

```sql
CREATE DATABASE rbac_db;
CREATE USER rbac_user WITH PASSWORD 'rbac_password';
GRANT ALL PRIVILEGES ON DATABASE rbac_db TO rbac_user;
```

3. В терминале:

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

4. При первом старте:
   - создаются таблицы,
   - создаются роли `guest`, `user`, `manager`, `admin`,
   - создаётся администратор: логин `admin`, пароль `Admin12345`.

Документация Swagger будет доступна по адресу `http://localhost:8000/docs`.

---

### 3. Запуск frontend (SPA)

```bash
cd frontend
npm install
npm run dev
```

Приложение будет на `http://localhost:5173`.

---

### 4. Основные маршруты frontend

- `/login` — страница входа.
- `/register` — регистрация.
- `/dashboard` — панель (вид зависит от роли).
- `/profile` — личный кабинет.
- `/settings` — настройки профиля.
- `/admin/users` — список пользователей и назначение ролей (**admin**).
- `/admin/logs` — страница аудита действий (**admin**).

Все защищённые маршруты реализованы через компонент `PrivateRoute`, который:

- проверяет наличие JWT‑токена,
- при необходимости проверяет минимальный уровень роли (например, admin = 3),
- перенаправляет на `/login` или `/dashboard` при отсутствии прав.

---

### 5. REST API (кратко)

Базовый URL: `http://localhost:8000`

- **POST** `/auth/register`  
  Тело:

  ```json
  {
    "username": "user1",
    "email": "user1@example.com",
    "password": "Password123",
    "confirm_password": "Password123"
  }
  ```

  Ответ: `{"access_token": "...", "token_type": "bearer"}` — сразу выполняется вход.

- **POST** `/auth/login`  
  Тело:

  ```json
  { "username": "user1", "password": "Password123" }
  ```

  Ответ: `{"access_token": "...", "token_type": "bearer"}`.

- **GET** `/auth/me` — профиль текущего пользователя.  
  Заголовок: `Authorization: Bearer <JWT>`.

- **GET** `/users/` — список пользователей (только `admin`, уровень 3).
- **POST** `/users/` — создание пользователя администратором:

  ```json
  {
    "username": "manager1",
    "email": "manager1@example.com",
    "password": "Password123",
    "roles": ["manager"]
  }
  ```

- **PUT** `/users/{user_id}/roles` — назначение ролей пользователю (admin).

- **GET** `/admin/roles` — список ролей (admin).
- **GET** `/admin/logs` — аудит действий (admin).

Во всех защищённых запросах используется заголовок `Authorization: Bearer <token>`.

---

### 6. Роли и уровни доступа

- **guest (0)** — только регистрация и просмотр общедоступной информации (фронтенд по умолчанию).
- **user (1)** — доступ к личному профилю, общим страницам, `/dashboard`, `/profile`, `/settings`.
- **manager (2)** — доступ к административным разделам (например, в будущем рабочим панелям менеджера).
- **admin (3)** — полный доступ:
  - управление пользователями (`/users/`),
  - назначение ролей (`/users/{id}/roles`),
  - просмотр логов (`/admin/logs`).

Проверка уровня доступа реализована на сервере через зависимость `role_required(min_level)` в `backend/deps.py`.

---

### 7. Безопасность

- Пароли хранятся только в хэшированном виде (`bcrypt` через `passlib`).
- JWT‑токены подписываются секретным ключом, срок жизни задаётся в `config.py`
  (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- JWT передаётся в заголовке `Authorization: Bearer <token>` (нет cookies → минимальный риск CSRF).
- SQL‑инъекции предотвращаются использованием ORM (SQLAlchemy).
- XSS‑атаки снижаются за счёт React (данные не вставляются как HTML).
- Простые защиты от brute force можно расширить (например, добавить счётчик неудачных попыток и блокировку).


