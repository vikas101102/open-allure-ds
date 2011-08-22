#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
from buzhug import Base
import time

# Open database
db = Base('oafc').open()

# pull records 
print('  time                      __id__  url         q   score duration')   
for record in (record for record in db):
        print(time.strftime("%a, %d %b %Y %H:%M:%S ", time.localtime(record.time)), record.__id__, str(record.url), record.q, record.score, str(record.duration))
#    ('Sat, 01 Jan 2011 02:44:13 ', 31, 'cases.txt', 0, None, 'None')
print('  time                      __id__  url         q   score duration')        
raise SystemExit

# insert recrod
record_id = db.insert(localtime=time.time(),filename='test',question=0,answer=1)
record_id = db.insert(localtime=time.time(),filename='test',question=1,answer=2)

# Close database
db.close()

# Get list of questions touched
#[record.question for record in records]

# Get list of answers touched
#[(record.question,record.answer) for record in records]

# Create database
#db = Base(path)
#db.create(('localTime',float),('fileName',string),('question',int),('answer',int))


