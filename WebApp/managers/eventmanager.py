from flask_sqlalchemy import SQLAlchemy
from WebApp.models.event import Event
from typing import Optional
from WebApp import db
from WebApp.models.category import Category

class EventManager:
    def __init__(self, db: SQLAlchemy):
        self.__db = db

    def list_events(self, page: int = 1, per_page: int = 10, category_id: Optional[int] = None, q: Optional[str] = None):

        query = self.__db.session.query(Event).order_by(Event.created_at.desc())
        if category_id:
            query = query.join(Event.categories).filter(Category.id == category_id)
        if q:
            qlike = f"%{q}%"
            query = query.outerjoin(Event.categories).filter(
                (Event.title.ilike(qlike)) | (Event.description.ilike(qlike)) | (Category.name.ilike(qlike))
            ).distinct()
        total = query.count()
        pages = (total + per_page - 1) // per_page if per_page else 1
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return {"items": items, "total": total, "page": page, "per_page": per_page, "pages": pages}

    def top_events(self, limit: int = 5, min_reservations: int = 5):
      
        from WebApp.models.reservation import Reservation
        from sqlalchemy import func

        q = self.__db.session.query(
            Event,
            func.count(Reservation.id).label('res_count')
        ).outerjoin(Reservation, Reservation.event_id == Event.id)
        q = q.group_by(Event.id).having(func.count(Reservation.id) >= min_reservations).order_by(func.count(Reservation.id).desc()).limit(limit)
        return q.all()

    def get_event(self, id: int):
        from sqlalchemy.orm import joinedload
        return self.__db.session.query(Event).options(joinedload(Event.categories)).filter(Event.id == id).one_or_none()

    def add_event(self, title: str, description: str):
        event = Event(title=title, description=description)
        self.__db.session.add(event)
        self.__db.session.commit()
        return event