import os
from buzhug import Base

# Open database
db = Base('oadb').open()

# pull records 
for record in (record for record in db):
    if record.cmd:
        print(record.__id__, str(record.url), record.q, record.a, str(record.cmd))
    elif record.a:
        print(record.__id__, str(record.url), record.q, record.a)
    else:
        print(record.__id__, str(record.url), record.q)
        
os.sys.exit()

# insert recrod
record_id = db.insert(localtime=time.time(),filename='test',question=0,answer=1)
record_id = db.insert(localtime=time.time(),filename='test',question=1,answer=2)

# Close database
db.close()

# Get list of questions touched
[record.question for record in records]

# Get list of answers touched
[(record.question,record.answer) for record in records]

# Create database
db = Base(path)
db.create(('localTime',float),('fileName',string),('question',int),('answer',int))


