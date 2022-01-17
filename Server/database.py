from typing import List
import sqlalchemy as alchemy
import sqlalchemy.ext.declarative as alchemyExt
import sqlalchemy.orm as alchemyOrm

engine = alchemy.create_engine('sqlite:///rowery.db', echo=True)

Base = alchemyExt.declarative_base()

class Rental:
   pass

class User(Base):
   __tablename__ = 'User'

   id = alchemy.Column(alchemy.Integer, primary_key=True, autoincrement=True)
   email = alchemy.Column(alchemy.String(30), unique=True)
   card_id = alchemy.Column(alchemy.String(255), unique=True)
   passwordHash = alchemy.Column(alchemy.String(255))
   balance = alchemy.Column(alchemy.Integer, default=0, nullable=False)
   active = alchemy.Column(alchemy.Boolean, default=False, nullable=False)
   rentals: List[Rental] = alchemyOrm.relationship("Rental", back_populates="user")

class Rental(Base):
   __tablename__ = 'Rental'

   id = alchemy.Column(alchemy.Integer, primary_key=True, autoincrement=True)
   userId = alchemy.Column(alchemy.ForeignKey('User.id'), nullable=False)
   user: List[User] = alchemyOrm.relationship("User", back_populates="rentals")
   timestamp_start = alchemy.Column(alchemy.DateTime, nullable=False)
   timestamp_stop = alchemy.Column(alchemy.DateTime)

class Terminal(Base):
   __tablename__ = 'Terminal'

   id = alchemy.Column(alchemy.Integer, primary_key=True, autoincrement=True)
   terminalName = alchemy.Column(alchemy.String(30), nullable=False)
   passwordHash = alchemy.Column(alchemy.String(255))
   rentalCount = alchemy.Column(alchemy.Integer, nullable=False)

class Log(Base):
   __tablename__ = 'Logs'

   id = alchemy.Column(alchemy.Integer, primary_key=True, autoincrement=True)
   card_id = alchemy.Column(alchemy.String(255))
   timestamp = alchemy.Column(alchemy.DateTime)
   log = alchemy.Column(alchemy.String(255))

Base.metadata.create_all(engine)
Session = alchemyOrm.sessionmaker(bind = engine, autoflush=False)
session: alchemyOrm.Session = Session()