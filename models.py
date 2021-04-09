import datetime

from sqlalchemy import Column, Integer, DateTime, Index, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, declared_attr


Base = declarative_base()


class ModelBaseMixin:

    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def keys(self):
        return self.__table__.columns.keys()

    def __getitem__(self, key):
        if key in self.__table__.columns.keys():
            return self.__getattribute__(key)
        else:
            raise KeyError(key)


class PostedArticles(Base, ModelBaseMixin):
    __tablename__ = 'posted_articles'
    date_created = Column(DateTime, default=datetime.datetime.now)
    article_id = Column(Integer, unique=True)


Index('posted_articles__id__index', PostedArticles.id)
Index('posted_articles__article_id__index', PostedArticles.article_id)


class ScrapFilters(Base, ModelBaseMixin):
    __tablename__ = 'url_to_scrap'
    date_created = Column(DateTime, default=datetime.datetime.now)
    telegram_user_id = Column(Integer)
    path = Column(String)


Index('url_to_scrap__id__index', ScrapFilters.id)
