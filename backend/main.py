from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import admin, auth, models, users
from .config import settings
from .database import Base, engine, SessionLocal
from .security import get_password_hash


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    # Для учебного проекта разрешаем запросы с любого origin,
    # чтобы не мучиться с CORS при запуске на localhost.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(admin.router)

    @app.on_event("startup")
    def on_startup() -> None:
        # Создаем таблицы
        Base.metadata.create_all(bind=engine)

        # Инициализируем роли и администратора
        db = SessionLocal()
        try:
            from sqlalchemy import select

            role_names_levels = [
                ("guest", 0),
                ("user", 1),
                ("manager", 2),
                ("admin", 3),
            ]

            for name, level in role_names_levels:
                exists = db.scalars(
                    select(models.Role).where(models.Role.name == name)
                ).first()
                if not exists:
                    db.add(models.Role(name=name, level=level))
            db.commit()

            # создаем администратора, если его нет
            admin_username = "admin"
            admin_email = "admin@example.com"
            admin_password = "Admin12345"
            existing_admin = db.scalars(
                select(models.User).where(models.User.username == admin_username)
            ).first()
            if not existing_admin:
                existing_admin = models.User(
                    username=admin_username,
                    email=admin_email,
                    hashed_password=get_password_hash(admin_password),
                    is_active=True,
                )
                db.add(existing_admin)
                db.commit()
                db.refresh(existing_admin)
            else:
                # обновляем пароль администратора под новый алгоритм хэширования
                existing_admin.hashed_password = get_password_hash(admin_password)
                db.add(existing_admin)
                db.commit()
                db.refresh(existing_admin)

            admin_role = db.scalars(
                select(models.Role).where(models.Role.name == "admin")
            ).first()
            if admin_role and admin_role not in existing_admin.roles:
                existing_admin.roles.append(admin_role)
                db.add(existing_admin)
                db.commit()

        finally:
            db.close()

    return app


app = create_app()


