import sqlalchemy as alchemy;
import sqlalchemy.ext.declarative as alchemyExt;
import sqlalchemy.orm as alchemyOrm;
engine = alchemy.create_engine('sqlite:///rowery.db', echo=True)

Base = alchemyExt.declarative_base()

class User(Base):
   __tablename__ = 'User'

   id = alchemy.Column(alchemy.Integer, primary_key=True, autoincrement=True)
   username = alchemy.Column(alchemy.String(30), unique=True)
   passwordHash = alchemy.Column(alchemy.String(255))
   balance = alchemy.Column(alchemy.Integer, default=0)
   rentals = alchemyOrm.relationship("Rental", back_populates="user")

class Rental(Base):
   __tablename__ = 'Rental'

   id = alchemy.Column(alchemy.Integer, primary_key=True, autoincrement=True)
   userId = alchemy.Column(alchemy.ForeignKey('User.id'), nullable=False)
   user = alchemyOrm.relationship("User", back_populates="rentals")
   timestamp_start = alchemy.Column(alchemy.DateTime, nullable=False)
   timestamp_stop = alchemy.Column(alchemy.DateTime)

class Terminal(Base):
   __tablename__ = 'Terminal'

   id = alchemy.Column(alchemy.Integer, primary_key=True, autoincrement=True)
   terminalName = alchemy.Column(alchemy.String(30), nullable=False)
   passwordHash = alchemy.Column(alchemy.String(255))

Base.metadata.create_all(engine)
Session = alchemyOrm.sessionmaker(bind = engine)
session = Session()