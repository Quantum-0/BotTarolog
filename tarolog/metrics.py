import datetime
import logging

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine("sqlite:////metrics/metrics.db")


class Base(DeclarativeBase):
    pass


class Metrics(Base):
    __tablename__ = "metrics"

    username = Column(String, primary_key=True)
    interactions_count = Column(Integer, nullable=False, default=0)  # default = 0
    first_action = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)  # default=datetime.datetime.utcnow
    last_action = Column(DateTime, nullable=False)


Base.metadata.create_all(bind=engine)


def update_metrics(username: str):
    with Session(autoflush=False, bind=engine) as db:
        user: Metrics | None = db.get(Metrics, username)
        if user is None:
            user = Metrics(username=username, first_action=datetime.datetime.utcnow(), interactions_count=0)
            logging.info("New user: %s", username)
        user.last_action = datetime.datetime.utcnow()
        user.interactions_count += 1
        db.add(user)
        db.commit()
