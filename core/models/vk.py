from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from .models import User

Base = declarative_base()


class VkUser(Base):
    __tablename__ = 'VkUser'

    vk_id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id))
    message_count = Column(Integer, default=0, nullable=True)

    def __repr__(self):
        return f"VkUser(vk_id={self.vk_id}, user_id={self.user_id}, messages_count={self.message_count})"
