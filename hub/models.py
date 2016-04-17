#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
#from database import db.Base
import hub.database as db
#from hub.database import db.Base

class File(db.Base):
    __tablename__="files"

    id = Column(Integer, primary_key=True)
    name   = Column(String)
    origin = Column(String)
    size   = Column(Integer)
    date   = Column(String)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    job    = relationship("Job", back_populates="file")

    def __repr__(self):
        return "<File(name='%s', origin='%s', size='%d', date='%s')>" %\
                (self.name, self.origin, self.size, self.date)

class Job(db.Base):
    __tablename__="jobs"

    id         = Column(Integer, primary_key=True)
    uuid       = Column(Integer, unique=True)
    order      = Column(Integer)
    created_at = Column(String)
    updated_at = Column(String)
    status     = Column(String)
    file       = relationship("File", back_populates="job")
    printer_id = Column(Integer, ForeignKey('printers.id'))
    printer    = relationship("Printer", back_populates="jobs")
    current_printer = relationship("Printer", back_populates="cjob")

    def __repr__(self):
        return "<Job(uuid='%d', created_at='%s', updated_at='%s', status='%s', file='%s')>" %\
        (self.uuid, self.created_at, self.updated_at, self.status,\
            self.file)

class Printer(db.Base):
    __tablename__="printers"

    id   = Column(Integer, primary_key=True)
    uuid = Column(Integer, unique=True)
    jobs = relationship("Job", order_by=Job.id, back_populates="printer")
    cjob = relationship("Job", back_populates="current_printer")

    def __repr__(self):
        return "<Printer(uuid='%d' jobs='%s', cjob='%s')>"\
                % (self.uuid, self.jobs, self.cjob)

