import models
from models import Printer
from models import Job
from models import File
from database import init_db, db_session

if __name__=="__main__":
    init_db()
    print "testing..."
    p = Printer(uuid=1236)
    db_session.add(p)
    db_session.commit()
    exit()
    fdate = str(dt.utcnow().isoformat()[:-3])+'Z'
    j = Job(uuid=3121, created_at=fdate, updated_at=fdate,status="ERROR")
    j.file += [File(name="Holder.st",origin="remote",size=9123)]
    p.cjob = []
    p.jobs += [j]
    j2 = Job(uuid=3221,created_at=fdate,updated_at=fdate,status="ERROR")
    p.jobs+=[j2]
    db_session.add(p)
    db_session.commit()
    db_session.remove()
    #print Printer.query.all()
    print p
    #print j

