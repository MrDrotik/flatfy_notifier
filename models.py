import datetime

from sqlalchemy import Column, Integer, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class PostedArticles(Base):
    __tablename__ = 'posted_articles'
    article_id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=datetime.datetime.now)


Index('posted_articles_id_index', PostedArticles.article_id)
