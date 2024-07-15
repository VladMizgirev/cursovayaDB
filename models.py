import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Word(Base):
    __tablename__ = "word"
    id = sq.Column(sq.Integer, primary_key=True)
    rus = sq.Column(sq.String(length=40), unique=True)
    en = sq.Column(sq.String(length=40), unique=True)
    w_en_1 = sq.Column(sq.String(length=40), unique=True)
    w_en_2 = sq.Column(sq.String(length=40), unique=True)
    w_en_3 = sq.Column(sq.String(length=40), unique=True)

    def __str__(self):
        return f'{self.id}: {self.rus}, {self.en}, {self.w_en}'

class New_word(Base):
    __tablename__ = "new_word"
    id = sq.Column(sq.Integer, primary_key=True)
    rus = sq.Column(sq.String(length=40), unique=True)
    en = sq.Column(sq.String(length=40), unique=True)
    w_en_1 = sq.Column(sq.String(length=40), unique=True)
    w_en_2 = sq.Column(sq.String(length=40), unique=True)
    w_en_3 = sq.Column(sq.String(length=40), unique=True)
    
    def __str__(self):
        return f'{self.id}: {self.id}: {self.rus}, {self.en}, {self.w_en}'

class Client(Base):
    __tablename__ = "client"
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=40), unique=True)
    word = relationship(Word, backref="clients")
    id_word = sq.Column(sq.Integer, sq.ForeignKey("word.id"), nullable=False)
    id_new_word = sq.Column(sq.Integer, sq.ForeignKey("new_word.id"), nullable=False)
    new_word = relationship(New_word, backref="clients")

    def __str__(self):
        return f'{self.id} - {self.name}'

def create_tables(engine):
    Base.metadata.create_all(engine)
