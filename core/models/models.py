from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint


from re import fullmatch


Base = declarative_base()


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, autoincrement=True, primary_key=True)


class Privileges(Base):
    __tablename__ = 'Privilege'

    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    allow = Column(String, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint(user_id, allow),
        {},
    )

    def __init__(self, user_id: int, allow: str):
        self.user_id = user_id
        self.allow = allow
        if fullmatch(r'^\w+\.\w+$', allow):
            print('good')
        # TODO check allow by '^\w+.\w+$' and has path/paths