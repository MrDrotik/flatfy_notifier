import datetime

from sqlalchemy import Column, Integer, DateTime, Index, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ModelMixin:

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_created = Column(DateTime, default=datetime.datetime.now)

    def keys(self):
        return self.__table__.columns.keys()

    def __getitem__(self, key):
        if key in self.__table__.columns.keys():
            return self.__getattribute__(key)
        else:
            raise KeyError(key)


class PostedArticles(Base, ModelMixin):
    __tablename__ = 'posted_articles'
    article_id = Column(Integer, unique=True)


Index('posted_articles__id__index', PostedArticles.id)
Index('posted_articles__article_id__index', PostedArticles.article_id)


class Users(Base, ModelMixin):
    __tablename__ = 'users'
    telegram_user_id = Column(Integer)


Index('users__id__index', Users.id)
Index('users__telegram_user_id__index', Users.telegram_user_id)


class ScrapFilters(Base, ModelMixin):
    __tablename__ = 'scrap_filters'
    user_id = Column(Integer, ForeignKey(Users.id))
    path = Column(String)


Index('scrap_filters__id__index', ScrapFilters.id)
