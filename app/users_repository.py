from attrs import define
from sqlalchemy import Boolean, Integer, Column, ForeignKey, String
from sqlalchemy.orm import relationship, Session
from .database import Base
    
@define
class UserCreate:
    email: str
    full_name: str
    password: str
    
    
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key = True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    purchases = relationship('Purchase', back_populates='owner')
    
    
class UserRepository:
    def get_by_email(self, db: Session, email: str) ->User:
        return db.query(User).filter(User.email == email).first()
    def get_all(self, db: Session, skip: int = 0, limit: int = 10):
        return db.query(User).offset(skip).limit(limit).all()
    def save(self, db: Session, user: UserCreate)-> User:
        db_user = User(email = user.email, password = user.password, full_name=user.full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    
