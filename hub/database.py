#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import models
from datetime import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine     = create_engine('sqlite:///stratus.db', convert_unicode=True)
#Session    = sessionmaker(bind=engine)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)


