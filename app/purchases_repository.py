from attrs import define
from .database import Base
from sqlalchemy import Column, Integer, ForeignKey, or_
from sqlalchemy.orm import relationship, Session

@define
class PurchaseCreate:
    user_id: int
    flower_id: int
    
class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    flower_id = Column(Integer, ForeignKey('flowers.id'))
    flower = relationship('Flower', back_populates='purchased')
    owner = relationship('User', back_populates='purchases')
    
class PurchaseRepository:
    def save(self, db: Session, purchase: PurchaseCreate):
        db_purchase = Purchase(owner_id = purchase.user_id,flower_id = purchase.flower_id )
        db.add(db_purchase)  
        db.commit()
        db.refresh(db_purchase)
    def get_by_user_id(self, db: Session,user_id: int):
        return db.query(Purchase).filter(Purchase.owner_id==user_id).all()
    