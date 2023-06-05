import os

AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']
BASE_ID = 'appvOnl6DnnKj8fVM'
TABLE_NAME = 'Automagic'

from pyairtable import Table

table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
rows = table.all()
for row in rows:
  print(row)
  id = row['id']
  status = row['fields']['Status']
  table.update(id, {'Status': f'{status}'})

