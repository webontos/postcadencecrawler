#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017-09-22 michael_yin
#

from sqlalchemy import create_engine, Column, Table, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Integer, Numeric, String, Date, DateTime, Float, Boolean, Text, LargeBinary)

from scrapy.utils.project import get_project_settings
from datetime import datetime


DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    # DeclarativeBase.metadata.drop_all(engine)  # all tables are deleted
    DeclarativeBase.metadata.create_all(engine)


class WebPages(DeclarativeBase):
    __tablename__ = "web_pages"

    id = Column(Integer, primary_key=True)

    url = Column('url', Text(), nullable=False, unique=True)
    publication_date = Column('publication_date', Date)
    modification_date = Column('modification_date', Date)
    section = Column('section', String(50))
    type = Column('type', String(50))
    wordcount = Column('wordcount', Numeric)
    new_ext_domains = Column('new_ext_domains', Numeric)

    first_crawl_date = Column('first_crawl_date', DateTime, default=datetime.now())
    last_crawl_date = Column('last_crawl_date', DateTime)
    crawl_times = Column('crawl_times', Numeric)
    site_id = Column('site_id', Integer, ForeignKey('sites.id'))

    UniqueConstraint('url', name='uix_webpages_url')
    external_links = relationship("ExternalLinks")


class Sites(DeclarativeBase):

    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    first_crawl_date = Column('first_crawl_date', DateTime)
    last_crawl_date = Column('last_crawl_date', DateTime)

    url = Column('url', Text(), nullable=False, unique=True)
    crawl_status = Column('crawl_status', String(50), default="NEW")
    trending_section = Column('trending_section', String(50))
    pub_median_indays = Column('pub_median_indays', Numeric)
    crawl_times = Column('crawl_times', Numeric)
    pub_avg_indays = Column('pub_avg_indays', Numeric)
    pages_count = Column('pages_count', Numeric)
    new_ext_links_median_indays = Column('new_ext_links_median_indays', Numeric)
    new_ext_links_mean_indays = Column('new_ext_links_mean_indays', Numeric)
    links_opp = Column('links_opp', String(50))
    links_opp_score_percent = Column('links_opp_score_percent', Numeric)

    UniqueConstraint('url', name='uix_sites_url')
    webpages = relationship("WebPages")


class ExternalLinks(DeclarativeBase):
    __tablename__ = "external_links"

    id = Column(Integer, primary_key=True)
    ext_domain = Column('ext_domain', String(100))

    page_id = Column('page_id', Integer, ForeignKey('web_pages.id'))

    UniqueConstraint('page_id', 'ext_domain', name='uix_externallinks')









