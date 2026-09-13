from typing import TypeVar, Generic, Type, Optional, List
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db

T = TypeVar("T", bound=db.Model)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> Optional[T]:
        return self.model.query.get(id)

    def get_all(self) -> List[T]:
        return self.model.query.all()

    def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        self.db.session.commit()
        return instance

    def delete(self, instance: T) -> None:
        self.db.session.delete(instance)
        self.db.session.commit()

    def save(self, instance: T) -> T:
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def find_by(self, **kwargs) -> Optional[T]:
        return self.model.query.filter_by(**kwargs).first()

    def find_all_by(self, **kwargs) -> List[T]:
        return self.model.query.filter_by(**kwargs).all()
