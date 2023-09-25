import datetime
import logging

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from tarolog.settings import settings

if settings.Database.ENGINE == "sqlite":
    engine = create_engine("sqlite:////metrics/metrics.db")
else:
    engine = create_engine(settings.Database.DSN)


class Base(DeclarativeBase):
    pass


class Metrics(Base):
    __tablename__ = settings.Database.METRICS_TABLE_NAME

    username = Column(String, primary_key=True)
    interactions_count = Column(Integer, nullable=False, default=0)
    first_action = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    last_action = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


class Projects(Base):
    __tablename__ = settings.Database.PROJECTS_TABLE_NAME

    project_name = Column(String, primary_key=True)
    request_count = Column(Integer, nullable=False, default=0)
    first_action = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    last_action = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


Base.metadata.create_all(bind=engine)


def update_metrics(username: str) -> None:
    with Session(autoflush=False, bind=engine) as db:
        user: Metrics | None = db.get(Metrics, username)
        if user is None:
            user = Metrics(username=username, first_action=datetime.datetime.utcnow(), interactions_count=0)
            logging.info("New user: %s", username)
        user.last_action = datetime.datetime.utcnow()
        user.interactions_count += 1
        db.add(user)
        db.commit()


def update_project(project_name: str) -> None:
    with Session(autoflush=False, bind=engine) as db:
        proj: Projects | None = db.get(Projects, project_name)
        if proj is None:
            proj = Projects(project_name=project_name, first_action=datetime.datetime.utcnow(), request_count=0)
            logging.info("Requested project: %s", project_name)
        proj.last_action = datetime.datetime.utcnow()
        proj.request_count += 1
        db.add(proj)
        db.commit()
