from attrs import define
from sqlalchemy import Column, Integer, String, or_
from sqlalchemy.orm import relationship, Session
from .database import Base

class Flower(Base):
    __tablename__ = 'flowers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    count = Column(Integer)
    cost = Column(Integer)
    purchased = relationship('Purchase', back_populates='flower')
    
@define
class FlowerCreate:
    name: str
    count: int
    cost: int
    
@define
class FlowerEdit:
    name: str
    count: int
    cost: int
    
class FlowersRepository:
    def save(self, db: Session,  flower: FlowerCreate)->Flower:
        db_flower = Flower(name=flower.name, count=flower.count, cost=flower.cost)
        db.add(db_flower)
        db.commit()
        db.refresh(db_flower)
        return db_flower    
    def get_all(self, db: Session, skip: int=0, limit:int=10):
        return db.query(Flower).offset(skip).limit(limit).all()
    def get_by_ids(self,db: Session, id_list: list)->list:
        filter_condition = [Flower.id == id for id in id_list]
        return db.query(Flower).filter(or_(*filter_condition)).all()
    def delete(self, db: Session,flower_id: int):
        flower = db.query(Flower).filter(flower_id==Flower.id).first()
        db.delete(flower)
        db.commit()
    def update(self, flower_id: int, input: FlowerEdit, db: Session):
        flower_db = db.query(Flower).filter(flower_id==Flower.id).first()
        if flower_db:
            flower_db.name = input.name
            flower_db.count = input.count
            flower_db.cost = input.cost
            db.commit()
            db.refresh(flower_db)
        return flower_db
            
        